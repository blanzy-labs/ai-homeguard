from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
import ipaddress
import math
from typing import Protocol

from app.core.command_runner import CommandResult, SafeCommandRunner
from app.core.platform import LocalPlatform, get_runtime_context
from app.knowledge.guidance_service import enrich_report_guidance
from app.models.enums import Category, Confidence, Difficulty, FindingStatus, Platform, ReportMode, Severity
from app.models.evidence import Evidence
from app.models.finding import Finding
from app.models.network import NetworkAuthorizationScope, NetworkContext
from app.models.network_discovery import (
    DeviceRecognition,
    DeviceTypeGuess,
    DiscoveredDevice,
    DiscoveryMethod,
    DiscoveryRuntimeMode,
    NetworkDiscoveryRequest,
    NetworkDiscoveryResult,
)
from app.models.report import HomeGuardReport
from app.models.runtime import RuntimeEnvironment
from app.network.context import (
    IP_PATTERN,
    MAC_PATTERN,
    collect_passive_network_context,
    mask_mac_address,
)
from app.network.device_classifier import classify_device_confidence, classify_device_type, device_needs_review
from app.network.guardrails import limit_subnet_size, validate_private_subnet
from app.reports.merge import summary_from_findings
from app.version import APP_NAME, APP_VERSION

DISCOVERY_AUTHORIZATION_ERROR = "Network discovery requires authorization acknowledgement."
DISCOVERY_SCOPE_ERROR = "Network discovery requires home_network scope."
DISCOVERY_PRIVATE_ONLY_ERROR = "Network discovery requires private-network-only acknowledgement."
DISCOVERY_ACTIVE_ERROR = "Active private discovery requires explicit active discovery authorization."
DISCOVERY_METHOD_ERROR = "Network discovery method is not supported."

NETWORK_DISCOVERY_DISCLAIMER = (
    "Network discovery is local and authorization-gated. AI HomeGuard checks private local IPv4 "
    "addresses only when authorized. It does not scan public targets, scan ports, run Nmap, "
    "capture packets, log in to routers, test credentials, upload data, change settings, or save "
    "this report automatically."
)


class DiscoveryCommandRunnerProtocol(Protocol):
    def run(
        self,
        command_name: str,
        args: Sequence[str],
        timeout_seconds: int = 5,
        platform_name: LocalPlatform | None = None,
    ) -> CommandResult:
        ...


@dataclass(frozen=True)
class PassiveDiscoveryCommandSet:
    runner: DiscoveryCommandRunnerProtocol
    platform_name: LocalPlatform
    commands: tuple[tuple[str, list[str]], ...]
    route_command_names: tuple[str, ...]
    neighbor_command_names: tuple[str, ...]


def run_network_discovery_report(
    request: NetworkDiscoveryRequest,
    *,
    generated_at: datetime | None = None,
    context: NetworkContext | None = None,
    passive_command_set: PassiveDiscoveryCommandSet | None = None,
    ping_runner: DiscoveryCommandRunnerProtocol | None = None,
) -> HomeGuardReport:
    report_time = generated_at or datetime.now(UTC)
    result = run_network_discovery(
        request,
        context=context,
        passive_command_set=passive_command_set,
        ping_runner=ping_runner,
    )
    findings = build_network_discovery_findings(result)
    result.findings = findings
    result.top_actions = summary_from_findings(findings).top_actions

    return enrich_report_guidance(HomeGuardReport(
        report_id=f"network-discovery-report-{report_time.strftime('%Y%m%d%H%M%S')}",
        app=APP_NAME,
        version=APP_VERSION,
        generated_at=report_time,
        mode=ReportMode.NETWORK_DISCOVERY,
        platform_scope=[Platform.NETWORK, Platform.ROUTER] if result.gateway_detected else [Platform.NETWORK],
        summary=summary_from_findings(findings),
        findings=findings,
        disclaimer=NETWORK_DISCOVERY_DISCLAIMER,
        safety_notes=result.safety_notes,
    ))


def run_network_discovery(
    request: NetworkDiscoveryRequest,
    *,
    context: NetworkContext | None = None,
    passive_command_set: PassiveDiscoveryCommandSet | None = None,
    ping_runner: DiscoveryCommandRunnerProtocol | None = None,
) -> NetworkDiscoveryResult:
    _validate_request(request)
    network_context = context or collect_passive_network_context()
    runtime_mode = _runtime_mode(network_context)
    limitations = list(network_context.limitations)
    devices: list[DiscoveredDevice] = []

    if request.method in {DiscoveryMethod.PASSIVE_CACHE, DiscoveryMethod.COMBINED}:
        passive_devices = collect_passive_discovery_devices(
            network_context,
            include_router_gateway=request.include_router_gateway,
            command_set=passive_command_set,
        )
        devices = _merge_devices(devices, passive_devices)

    if request.method in {DiscoveryMethod.PRIVATE_PING, DiscoveryMethod.COMBINED}:
        if not request.authorization.include_active_discovery:
            if request.method == DiscoveryMethod.PRIVATE_PING:
                raise ValueError(DISCOVERY_ACTIVE_ERROR)
            limitations.append("Active private discovery was not enabled; passive cache only was used.")
        else:
            active_devices, active_limitations = run_private_ping_discovery(
                network_context,
                max_hosts=request.max_hosts,
                timeout_ms=request.timeout_ms,
                ping_runner=ping_runner,
            )
            devices = _merge_devices(devices, active_devices)
            limitations.extend(active_limitations)

    devices = _ensure_passive_placeholders(devices, network_context.passive_neighbor_count)
    devices = _finalize_devices(devices)
    safety_notes = _safety_notes(request, network_context)
    private_summary = _private_subnet_summary(network_context)

    return NetworkDiscoveryResult(
        method=request.method,
        runtime_mode=runtime_mode,
        discovered_count=len(devices),
        gateway_detected=any(device.is_gateway for device in devices) or network_context.gateway_present,
        private_subnet_summary=private_summary,
        devices=devices,
        limitations=_unique(limitations),
        safety_notes=_unique([*safety_notes, *limitations]),
        findings=[],
        top_actions=[],
    )


def collect_passive_discovery_devices(
    context: NetworkContext,
    *,
    include_router_gateway: bool = True,
    command_set: PassiveDiscoveryCommandSet | None = None,
) -> list[DiscoveredDevice]:
    command_set = command_set or _passive_command_set_for_platform(context.runtime_platform)
    if command_set is None:
        return _fallback_gateway_devices(context, include_router_gateway=include_router_gateway)

    results = [
        command_set.runner.run(command_name, args, timeout_seconds=5, platform_name=command_set.platform_name)
        for command_name, args in command_set.commands
    ]
    route_text = "\n".join(
        _safe_output(result)
        for result in results
        if result.command_name in command_set.route_command_names and _result_usable(result)
    )
    neighbor_text = "\n".join(
        _safe_output(result)
        for result in results
        if result.command_name in command_set.neighbor_command_names and _result_usable(result)
    )
    gateway_addresses = {str(address) for address in _gateway_ipv4_addresses(route_text)}
    devices = _devices_from_neighbor_text(neighbor_text, gateway_addresses)
    if include_router_gateway:
        for gateway_address in gateway_addresses:
            if not any(device.ip_hint == gateway_address for device in devices):
                devices.insert(0, _gateway_device(gateway_address))
    if not devices:
        devices = _fallback_gateway_devices(context, include_router_gateway=include_router_gateway)
    return devices


def run_private_ping_discovery(
    context: NetworkContext,
    *,
    max_hosts: int,
    timeout_ms: int,
    ping_runner: DiscoveryCommandRunnerProtocol | None = None,
) -> tuple[list[DiscoveredDevice], list[str]]:
    limitations: list[str] = []
    subnet = _active_discovery_subnet(context)
    if subnet is None:
        return [], ["AI HomeGuard could not identify a private /24-or-smaller IPv4 subnet for active discovery."]
    try:
        hosts = limit_subnet_size(subnet, max_hosts=max_hosts)
    except ValueError as error:
        return [], [str(error)]

    runtime_platform = _local_platform_for_model(context.runtime_platform)
    if runtime_platform == LocalPlatform.UNKNOWN:
        return [], ["Private ping discovery is unavailable on this runtime platform."]

    runner = ping_runner or _default_ping_runner(runtime_platform)
    devices: list[DiscoveredDevice] = []
    for address in hosts:
        ip_hint = str(address)
        validate_private_subnet(ip_hint)
        args = _ping_args(runtime_platform, ip_hint, timeout_ms)
        result = runner.run(
            "network_discovery_ping",
            args,
            timeout_seconds=_ping_timeout_seconds(timeout_ms),
            platform_name=runtime_platform,
        )
        if result.supported and not result.timed_out and result.return_code == 0:
            devices.append(_ping_device(ip_hint))
    if not devices:
        limitations.append("No devices responded to bounded private ping discovery, or ping was blocked.")
    return devices, limitations


def build_network_discovery_findings(result: NetworkDiscoveryResult) -> list[Finding]:
    findings = [_devices_found_finding(result)]
    review_count = sum(1 for device in result.devices if device.needs_review)
    if review_count:
        findings.append(_unknown_devices_finding(review_count))
    if result.gateway_detected:
        findings.append(_gateway_detected_finding(result))
    if result.runtime_mode == DiscoveryRuntimeMode.DOCKER_LIMITED:
        findings.append(_docker_limitation_finding())
    if result.discovered_count == 0 or result.limitations:
        findings.append(_limited_discovery_finding(result))
    findings.extend(_device_finding(device, index) for index, device in enumerate(result.devices, start=1))
    return findings


def demo_network_discovery_result() -> NetworkDiscoveryResult:
    devices = _finalize_devices(
        [
            DiscoveredDevice(
                id="demo-router",
                ip_hint="192.168.1.1",
                mac_hint="aa:bb:cc:xx:xx:xx",
                label="Router / Gateway",
                source_methods=[DiscoveryMethod.PASSIVE_CACHE],
                is_gateway=True,
                notes=["Demo device only."],
            ),
            DiscoveredDevice(
                id="demo-device-1",
                ip_hint="192.168.1.23",
                mac_hint="10:22:33:xx:xx:xx",
                source_methods=[DiscoveryMethod.PASSIVE_CACHE, DiscoveryMethod.PRIVATE_PING],
                notes=["Demo device only."],
            ),
            DiscoveredDevice(
                id="demo-device-2",
                ip_hint="192.168.1.42",
                source_methods=[DiscoveryMethod.PRIVATE_PING],
                notes=["Demo device only."],
            ),
        ]
    )
    result = NetworkDiscoveryResult(
        method=DiscoveryMethod.COMBINED,
        runtime_mode=DiscoveryRuntimeMode.NATIVE_HOST,
        discovered_count=len(devices),
        gateway_detected=True,
        private_subnet_summary="Demo private subnet 192.168.1.0/24.",
        devices=devices,
        limitations=["Demo discovery uses fake devices only."],
        safety_notes=[
            "Demo discovery does not send packets.",
            "No public targets were scanned.",
            "No ports were scanned.",
            "No router login was attempted.",
        ],
    )
    result.findings = build_network_discovery_findings(result)
    result.top_actions = summary_from_findings(result.findings).top_actions
    return result


def _validate_request(request: NetworkDiscoveryRequest) -> None:
    authorization = request.authorization
    if not authorization.acknowledged:
        raise ValueError(DISCOVERY_AUTHORIZATION_ERROR)
    if authorization.scope != NetworkAuthorizationScope.HOME_NETWORK:
        raise ValueError(DISCOVERY_SCOPE_ERROR)
    if not authorization.user_understands_private_network_only:
        raise ValueError(DISCOVERY_PRIVATE_ONLY_ERROR)
    if request.method not in {DiscoveryMethod.PASSIVE_CACHE, DiscoveryMethod.PRIVATE_PING, DiscoveryMethod.COMBINED}:
        raise ValueError(DISCOVERY_METHOD_ERROR)


def _passive_command_set_for_platform(platform: Platform) -> PassiveDiscoveryCommandSet | None:
    if platform == Platform.MACOS:
        return PassiveDiscoveryCommandSet(
            runner=SafeCommandRunner(
                {
                    "network_discovery_macos_route_default": ("route", "-n", "get", "default"),
                    "network_discovery_macos_netstat_routes": ("netstat", "-rn"),
                    "network_discovery_macos_arp_cache": ("arp", "-a"),
                },
                required_platform=LocalPlatform.MACOS,
            ),
            platform_name=LocalPlatform.MACOS,
            commands=(
                ("network_discovery_macos_route_default", ["route", "-n", "get", "default"]),
                ("network_discovery_macos_netstat_routes", ["netstat", "-rn"]),
                ("network_discovery_macos_arp_cache", ["arp", "-a"]),
            ),
            route_command_names=("network_discovery_macos_route_default", "network_discovery_macos_netstat_routes"),
            neighbor_command_names=("network_discovery_macos_arp_cache",),
        )
    if platform == Platform.LINUX:
        return PassiveDiscoveryCommandSet(
            runner=SafeCommandRunner(
                {
                    "network_discovery_linux_ip_route": ("ip", "route"),
                    "network_discovery_linux_ip_neigh": ("ip", "neigh", "show"),
                    "network_discovery_linux_arp_cache": ("arp", "-a"),
                },
                required_platform=LocalPlatform.LINUX,
            ),
            platform_name=LocalPlatform.LINUX,
            commands=(
                ("network_discovery_linux_ip_route", ["ip", "route"]),
                ("network_discovery_linux_ip_neigh", ["ip", "neigh", "show"]),
                ("network_discovery_linux_arp_cache", ["arp", "-a"]),
            ),
            route_command_names=("network_discovery_linux_ip_route",),
            neighbor_command_names=("network_discovery_linux_ip_neigh", "network_discovery_linux_arp_cache"),
        )
    if platform == Platform.WINDOWS:
        return PassiveDiscoveryCommandSet(
            runner=SafeCommandRunner(
                {
                    "network_discovery_windows_ipconfig": ("ipconfig",),
                    "network_discovery_windows_route_print": ("route", "print"),
                    "network_discovery_windows_arp_cache": ("arp", "-a"),
                },
                required_platform=LocalPlatform.WINDOWS,
            ),
            platform_name=LocalPlatform.WINDOWS,
            commands=(
                ("network_discovery_windows_ipconfig", ["ipconfig"]),
                ("network_discovery_windows_route_print", ["route", "print"]),
                ("network_discovery_windows_arp_cache", ["arp", "-a"]),
            ),
            route_command_names=("network_discovery_windows_ipconfig", "network_discovery_windows_route_print"),
            neighbor_command_names=("network_discovery_windows_arp_cache",),
        )
    return None


def _devices_from_neighbor_text(text: str, gateway_addresses: set[str]) -> list[DiscoveredDevice]:
    devices: list[DiscoveredDevice] = []
    seen_ips: set[str] = set()
    for line in text.splitlines():
        normalized = line.lower()
        if "incomplete" in normalized or "failed" in normalized:
            continue
        ip_hint = _first_private_ipv4(line)
        if ip_hint is None or ip_hint in seen_ips:
            continue
        seen_ips.add(ip_hint)
        mac_match = MAC_PATTERN.search(line)
        is_gateway = ip_hint in gateway_addresses
        methods = [DiscoveryMethod.PASSIVE_CACHE]
        devices.append(
            DiscoveredDevice(
                id=_device_id("passive", ip_hint),
                ip_hint=ip_hint,
                mac_hint=mask_mac_address(mac_match.group(0)) if mac_match else None,
                label="Router / Gateway" if is_gateway else None,
                source_methods=methods,
                is_gateway=is_gateway,
                notes=["Found in passive local cache. No packets were sent by this passive check."],
            )
        )
    return devices


def _fallback_gateway_devices(context: NetworkContext, *, include_router_gateway: bool) -> list[DiscoveredDevice]:
    if not include_router_gateway or not context.gateway_present:
        return []
    return [
        DiscoveredDevice(
            id="gateway-passive-detected",
            label="Router / Gateway",
            source_methods=[DiscoveryMethod.PASSIVE_CACHE],
            is_gateway=True,
            notes=["Passive route context suggests a gateway exists, but no device identifier is shown."],
        )
    ]


def _gateway_ipv4_addresses(text: str) -> list[ipaddress.IPv4Address]:
    addresses: list[ipaddress.IPv4Address] = []
    for line in text.splitlines():
        normalized = line.lower()
        if "default" not in normalized and "gateway" not in normalized and "0.0.0.0" not in normalized:
            continue
        for match in IP_PATTERN.findall(line):
            try:
                address = ipaddress.ip_address(match.strip("[]"))
            except ValueError:
                continue
            if isinstance(address, ipaddress.IPv4Address) and _is_rfc1918(address):
                addresses.append(address)
    return addresses


def _active_discovery_subnet(context: NetworkContext) -> ipaddress.IPv4Network | None:
    for range_hint in context.possible_private_ranges:
        try:
            network = validate_private_subnet(range_hint)
        except ValueError:
            continue
        if network.prefixlen < 24:
            return None
        return network
    return None


def _default_ping_runner(platform: LocalPlatform) -> SafeCommandRunner:
    if platform == LocalPlatform.WINDOWS:
        return SafeCommandRunner({"network_discovery_ping": ("ping", "-n", "1", "-w")}, required_platform=platform)
    return SafeCommandRunner({"network_discovery_ping": ("ping", "-c", "1", "-W")}, required_platform=platform)


def _ping_args(platform: LocalPlatform, ip_hint: str, timeout_ms: int) -> list[str]:
    if platform == LocalPlatform.WINDOWS:
        return ["ping", "-n", "1", "-w", str(timeout_ms), ip_hint]
    timeout_seconds = max(1, math.ceil(timeout_ms / 1000))
    return ["ping", "-c", "1", "-W", str(timeout_seconds), ip_hint]


def _ping_timeout_seconds(timeout_ms: int) -> int:
    return max(2, math.ceil(timeout_ms / 1000) + 1)


def _ping_device(ip_hint: str) -> DiscoveredDevice:
    return DiscoveredDevice(
        id=_device_id("private-ping", ip_hint),
        ip_hint=ip_hint,
        source_methods=[DiscoveryMethod.PRIVATE_PING],
        notes=["Responded to one bounded private IPv4 ping. No ports were checked."],
    )


def _merge_devices(current: list[DiscoveredDevice], incoming: list[DiscoveredDevice]) -> list[DiscoveredDevice]:
    merged = list(current)
    for device in incoming:
        key = device.ip_hint or device.id
        existing_index = next(
            (index for index, existing in enumerate(merged) if (existing.ip_hint or existing.id) == key),
            None,
        )
        if existing_index is None:
            merged.append(device)
            continue
        existing = merged[existing_index]
        methods = _unique([*existing.source_methods, *device.source_methods])
        notes = _unique([*existing.notes, *device.notes])
        merged[existing_index] = existing.model_copy(
            update={
                "mac_hint": existing.mac_hint or device.mac_hint,
                "label": existing.label or device.label,
                "source_methods": methods,
                "is_gateway": existing.is_gateway or device.is_gateway,
                "notes": notes,
            }
        )
    return merged


def _ensure_passive_placeholders(devices: list[DiscoveredDevice], passive_neighbor_count: int | None) -> list[DiscoveredDevice]:
    if passive_neighbor_count is None:
        return devices
    non_gateway_count = sum(1 for device in devices if not device.is_gateway)
    placeholders_needed = max(0, passive_neighbor_count - non_gateway_count)
    additions = [
        DiscoveredDevice(
            id=f"passive-device-{index + 1}",
            source_methods=[DiscoveryMethod.PASSIVE_CACHE],
            notes=["Passive local cache counted this device, but identifiers are not shown by default."],
        )
        for index in range(placeholders_needed)
    ]
    return [*devices, *additions]


def _finalize_devices(devices: list[DiscoveredDevice]) -> list[DiscoveredDevice]:
    finalized: list[DiscoveredDevice] = []
    for index, device in enumerate(devices, start=1):
        device_type = classify_device_type(is_gateway=device.is_gateway, source_methods=device.source_methods)
        confidence = classify_device_confidence(is_gateway=device.is_gateway, source_methods=device.source_methods)
        label = device.label or ("Router / Gateway" if device.is_gateway else f"Device {index}")
        finalized.append(
            device.model_copy(
                update={
                    "label": label,
                    "device_type_guess": device_type,
                    "confidence": confidence,
                    "needs_review": device_needs_review(is_gateway=device.is_gateway, device_type=device_type),
                    "recognized": device.recognized or DeviceRecognition.NOT_ASKED,
                }
            )
        )
    return finalized


def _devices_found_finding(result: NetworkDiscoveryResult) -> Finding:
    review_count = sum(1 for device in result.devices if device.needs_review)
    if result.discovered_count == 0:
        status = FindingStatus.UNABLE_TO_CHECK
        summary = "HomeGuard could not find likely devices from the selected local network discovery method."
        action = "Check that you are on your home Wi-Fi and try again, or review your router's device list."
    else:
        status = FindingStatus.REVIEW if review_count else FindingStatus.GOOD
        summary = f"HomeGuard found {result.discovered_count} likely devices on the local private network."
        action = "Compare the device list with your router app and mark devices you recognize."
    return _network_discovery_finding(
        finding_id="network-discovery-devices-found",
        home_title="Devices found on your home network",
        status=status,
        severity=Severity.INFO,
        confidence=Confidence.MEDIUM if result.discovered_count else Confidence.LOW,
        platform=Platform.NETWORK,
        summary=summary,
        why_it_matters="Knowing what is on the home network helps you spot devices that need a closer look.",
        evidence=[
            Evidence(
                source="network discovery",
                method=result.method.value,
                observed_value=(
                    f"devices found: {result.discovered_count}; need review: {review_count}; "
                    f"gateway detected: {result.gateway_detected}"
                ),
                expected_value="private local network devices only",
                notes="No public targets were scanned. No ports were scanned. No router login was attempted.",
            )
        ],
        recommended_action=action,
        difficulty=Difficulty.EASY,
        estimated_time_minutes=10,
        tags=["network-discovery", "identify_assets"],
    )


def _unknown_devices_finding(review_count: int) -> Finding:
    return _network_discovery_finding(
        finding_id="network-discovery-unknown-devices-review",
        home_title="Some devices need review",
        status=FindingStatus.REVIEW,
        severity=Severity.INFO,
        confidence=Confidence.MEDIUM,
        platform=Platform.NETWORK,
        summary=f"{review_count} discovered device{'s' if review_count != 1 else ''} could not be identified automatically.",
        why_it_matters="Unknown devices are review items. They are not proof of a problem, but they are worth comparing with your router app.",
        evidence=[
            Evidence(
                source="network discovery",
                method="device classification",
                observed_value=f"unknown devices: {review_count}",
                expected_value="recognized household devices",
                notes="Automatically discovered unknown devices are review-level findings, not panic findings.",
            )
        ],
        recommended_action="Compare the device list with your router app and mark the devices you recognize.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=10,
        tags=["network-discovery", "identify_assets", "isolate_untrusted_devices"],
    )


def _gateway_detected_finding(result: NetworkDiscoveryResult) -> Finding:
    return _network_discovery_finding(
        finding_id="network-discovery-gateway-detected",
        home_title="Likely router or gateway detected",
        status=FindingStatus.GOOD,
        severity=Severity.INFO,
        confidence=Confidence.MEDIUM,
        platform=Platform.ROUTER,
        summary="HomeGuard detected a likely router or gateway for the local private network.",
        why_it_matters="The router or gateway is usually the center of a home network and is useful context for reviewing devices.",
        evidence=[
            Evidence(
                source="network discovery",
                method=result.method.value,
                observed_value=f"gateway detected: {result.gateway_detected}",
                expected_value="private local gateway if visible",
                notes="No router login was attempted.",
            )
        ],
        recommended_action="Review your router app for the complete device list and router admin settings.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=10,
        safe_to_ignore=True,
        tags=["network-discovery", "router", "review_router_admin"],
    )


def _docker_limitation_finding() -> Finding:
    return _network_discovery_finding(
        finding_id="network-discovery-container-limitation",
        home_title="Container networking may limit discovery",
        status=FindingStatus.REVIEW,
        severity=Severity.INFO,
        confidence=Confidence.HIGH,
        platform=Platform.NETWORK,
        summary="HomeGuard appears to be running in a container, so discovery may reflect the container network.",
        why_it_matters="Docker networking can differ from the host computer's view of the home network.",
        evidence=[
            Evidence(
                source="runtime context",
                method="detect_runtime_environment",
                observed_value="runtime environment: docker",
                expected_value="native host runtime for home network discovery",
                notes="No host network discovery was attempted from outside the container.",
            )
        ],
        recommended_action="For host-level home network discovery, run the backend natively.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=10,
        tags=["network-discovery", "runtime_context"],
    )


def _limited_discovery_finding(result: NetworkDiscoveryResult) -> Finding:
    return _network_discovery_finding(
        finding_id="network-discovery-limited",
        home_title="Device discovery had limited visibility",
        status=FindingStatus.UNABLE_TO_CHECK if result.discovered_count == 0 else FindingStatus.REVIEW,
        severity=Severity.INFO,
        confidence=Confidence.LOW,
        platform=Platform.NETWORK,
        summary="HomeGuard could not complete every part of device discovery.",
        why_it_matters="Local network visibility can be limited by Docker, VPNs, firewall settings, guest Wi-Fi, or client isolation.",
        evidence=[
            Evidence(
                source="network discovery",
                method=result.method.value,
                observed_value="; ".join(result.limitations) if result.limitations else "limited visibility",
                expected_value="private local network visibility",
                notes="No public targets, ports, router logins, or credentials were used.",
            )
        ],
        recommended_action="Check that you are on your home Wi-Fi and try again, or review your router's device list.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=10,
        tags=["network-discovery", "identify_assets"],
    )


def _device_finding(device: DiscoveredDevice, index: int) -> Finding:
    label = "Router / Gateway" if device.is_gateway else device.label or f"Device {index}"
    return _network_discovery_finding(
        finding_id=f"network-discovery-{device.id}",
        home_title=label,
        status=FindingStatus.GOOD if device.is_gateway else FindingStatus.REVIEW,
        severity=Severity.INFO,
        confidence=device.confidence,
        platform=Platform.ROUTER if device.is_gateway else Platform.NETWORK,
        summary=f"{label} was found on the local private network.",
        why_it_matters="Reviewing discovered devices helps you understand what is connected at home.",
        evidence=[
            Evidence(
                source="network discovery",
                method="+".join(method.value for method in device.source_methods) or "unknown",
                observed_value=_device_observed_value(device),
                expected_value="recognized household device",
                notes="MAC hints are masked and hostnames are hidden by default.",
            )
        ],
        recommended_action="Mark whether you recognize this device after comparing it with your router app.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=5,
        safe_to_ignore=True,
        tags=["network-discovery", "network-discovery-device", "identify_assets"],
    )


def _network_discovery_finding(
    *,
    finding_id: str,
    home_title: str,
    status: FindingStatus,
    severity: Severity,
    confidence: Confidence,
    platform: Platform,
    summary: str,
    why_it_matters: str,
    evidence: list[Evidence],
    recommended_action: str,
    difficulty: Difficulty,
    estimated_time_minutes: int,
    tags: list[str],
    safe_to_ignore: bool = False,
) -> Finding:
    return Finding(
        id=finding_id,
        title=f"Network discovery: {home_title}",
        home_title=home_title,
        technical_title=f"Private network discovery finding for {finding_id}",
        status=status,
        severity=severity,
        confidence=confidence,
        platform=platform,
        category=Category.NETWORK_AWARENESS,
        summary=summary,
        why_it_matters=why_it_matters,
        evidence=evidence,
        d3fend_guidance=[],
        recommended_action=recommended_action,
        difficulty=difficulty,
        estimated_time_minutes=estimated_time_minutes,
        user_can_fix=True,
        requires_admin=False,
        safe_to_ignore=safe_to_ignore,
        tags=tags,
    )


def _device_observed_value(device: DiscoveredDevice) -> str:
    parts = [
        f"label: {device.label or 'Device'}",
        f"source: {'+'.join(method.value for method in device.source_methods) or 'unknown'}",
        f"type guess: {device.device_type_guess.value}",
        f"recognized: {device.recognized.value}",
    ]
    if device.ip_hint:
        parts.append(f"IP hint: {device.ip_hint}")
    if device.mac_hint:
        parts.append(f"masked MAC hint: {device.mac_hint}")
    return "; ".join(parts)


def _safe_output(result: CommandResult) -> str:
    return mask_mac_address("\n".join(part for part in [result.stdout, result.stderr] if part))


def _result_usable(result: CommandResult) -> bool:
    return result.supported and not result.timed_out and result.return_code in {0, None} and bool(result.stdout.strip())


def _first_private_ipv4(text: str) -> str | None:
    for match in IP_PATTERN.findall(text):
        try:
            address = ipaddress.ip_address(match.strip("[]"))
        except ValueError:
            continue
        if isinstance(address, ipaddress.IPv4Address) and _is_rfc1918(address):
            return str(address)
    return None


def _is_rfc1918(address: ipaddress.IPv4Address) -> bool:
    return (
        address in ipaddress.ip_network("10.0.0.0/8")
        or address in ipaddress.ip_network("172.16.0.0/12")
        or address in ipaddress.ip_network("192.168.0.0/16")
    )


def _runtime_mode(context: NetworkContext) -> DiscoveryRuntimeMode:
    if context.runtime_environment == RuntimeEnvironment.DOCKER:
        return DiscoveryRuntimeMode.DOCKER_LIMITED
    if context.runtime_environment == RuntimeEnvironment.NATIVE:
        return DiscoveryRuntimeMode.NATIVE_HOST
    return DiscoveryRuntimeMode.UNKNOWN


def _local_platform_for_model(platform: Platform) -> LocalPlatform:
    if platform == Platform.MACOS:
        return LocalPlatform.MACOS
    if platform == Platform.LINUX:
        return LocalPlatform.LINUX
    if platform == Platform.WINDOWS:
        return LocalPlatform.WINDOWS
    return LocalPlatform.UNKNOWN


def _private_subnet_summary(context: NetworkContext) -> str | None:
    if not context.possible_private_ranges:
        return None
    return f"Private local range hints: {', '.join(context.possible_private_ranges[:3])}"


def _safety_notes(request: NetworkDiscoveryRequest, context: NetworkContext) -> list[str]:
    active_note = (
        "Active private discovery used bounded ping only."
        if request.authorization.include_active_discovery and request.method in {DiscoveryMethod.PRIVATE_PING, DiscoveryMethod.COMBINED}
        else "No active private discovery was run."
    )
    notes = [
        "Network discovery authorization is request-level only and is not stored.",
        "Only private RFC1918 IPv4 addresses are eligible.",
        "No public targets were scanned.",
        "No ports were scanned.",
        "No Nmap command was run.",
        "No packet capture was performed.",
        "No router login was attempted.",
        "No credentials were collected or tested.",
        "No data was uploaded.",
        "No report was saved automatically.",
        "No settings were changed.",
        "Full MAC addresses and hostnames are not shown by default.",
        active_note,
        *context.safety_notes,
    ]
    if context.runtime_environment == RuntimeEnvironment.DOCKER:
        notes.append("Docker/container networking may reflect the container network rather than the host home network.")
    return notes


def _device_id(prefix: str, ip_hint: str) -> str:
    return f"{prefix}-{ip_hint.replace('.', '-')}"


def _gateway_device(ip_hint: str) -> DiscoveredDevice:
    return DiscoveredDevice(
        id=_device_id("gateway", ip_hint),
        ip_hint=ip_hint,
        label="Router / Gateway",
        source_methods=[DiscoveryMethod.PASSIVE_CACHE],
        is_gateway=True,
        notes=["Detected as a likely local gateway from passive route context."],
    )


def _unique(values):
    unique_values = []
    for value in values:
        if value not in unique_values:
            unique_values.append(value)
    return unique_values
