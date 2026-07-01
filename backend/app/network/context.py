from collections.abc import Sequence
from dataclasses import dataclass
import ipaddress
import re
from typing import Protocol

from app.core.command_runner import CommandResult, SafeCommandRunner
from app.core.platform import LocalPlatform, get_runtime_context
from app.models.enums import Platform
from app.models.network import NetworkContext
from app.models.runtime import RuntimeContext, RuntimeEnvironment


class NetworkCommandRunnerProtocol(Protocol):
    def run(
        self,
        command_name: str,
        args: Sequence[str],
        timeout_seconds: int = 5,
        platform_name: LocalPlatform | None = None,
    ) -> CommandResult:
        ...


@dataclass(frozen=True)
class PassiveNetworkCommandSet:
    runner: NetworkCommandRunnerProtocol
    platform_name: LocalPlatform
    commands: tuple[tuple[str, list[str]], ...]
    route_command_names: tuple[str, ...]
    neighbor_command_names: tuple[str, ...]


MAC_PATTERN = re.compile(r"\b(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}\b")
IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b|(?<![\w:])(?:[0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}(?![\w:])")
CIDR_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}/\d{1,2}\b|(?<![\w:])(?:[0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}/\d{1,3}(?![\w:])")
PRIVATE_IPV4_RANGES = (
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
)
UNIQUE_LOCAL_IPV6 = ipaddress.ip_network("fc00::/7")


def collect_passive_network_context(
    *,
    runtime_context: RuntimeContext | None = None,
    command_set: PassiveNetworkCommandSet | None = None,
) -> NetworkContext:
    context = runtime_context or get_runtime_context()
    if context.runtime_environment == RuntimeEnvironment.DOCKER:
        limitations = [
            *context.limitations,
            "AI HomeGuard appears to be running in a container. Network context may reflect the container network rather than your home network.",
        ]
    else:
        limitations = list(context.limitations)

    command_set = command_set or _command_set_for_platform(context.detected_platform)
    if command_set is None:
        limitations.append("Passive network context is unavailable on this runtime platform.")
        return NetworkContext(
            runtime_platform=context.detected_platform,
            runtime_environment=context.runtime_environment,
            limitations=_unique(limitations),
            safety_notes=_base_safety_notes(),
        )

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

    possible_ranges = _private_ranges_from_text(route_text)
    gateway_addresses = _gateway_addresses(route_text)
    gateway_present = bool(gateway_addresses)
    gateway_private = any(_is_private_address(address) for address in gateway_addresses)
    passive_neighbor_count = _passive_neighbor_count(neighbor_text)

    return NetworkContext(
        runtime_platform=context.detected_platform,
        runtime_environment=context.runtime_environment,
        possible_private_ranges=possible_ranges,
        gateway_present=gateway_present,
        gateway_private=gateway_private,
        passive_neighbor_count=passive_neighbor_count,
        passive_neighbor_summary=_neighbor_summary(passive_neighbor_count),
        local_interface_count=len(possible_ranges) if possible_ranges else None,
        limitations=_unique(limitations),
        safety_notes=_base_safety_notes(),
    )


def mask_mac_address(value: str) -> str:
    return MAC_PATTERN.sub(lambda match: match.group(0)[:8] + ":xx:xx:xx", value)


def _command_set_for_platform(platform: Platform) -> PassiveNetworkCommandSet | None:
    if platform == Platform.MACOS:
        return PassiveNetworkCommandSet(
            runner=SafeCommandRunner(
                {
                    "network_macos_route_default": ("route", "-n", "get", "default"),
                    "network_macos_netstat_routes": ("netstat", "-rn"),
                    "network_macos_arp_cache": ("arp", "-a"),
                },
                required_platform=LocalPlatform.MACOS,
            ),
            platform_name=LocalPlatform.MACOS,
            commands=(
                ("network_macos_route_default", ["route", "-n", "get", "default"]),
                ("network_macos_netstat_routes", ["netstat", "-rn"]),
                ("network_macos_arp_cache", ["arp", "-a"]),
            ),
            route_command_names=("network_macos_route_default", "network_macos_netstat_routes"),
            neighbor_command_names=("network_macos_arp_cache",),
        )
    if platform == Platform.LINUX:
        return PassiveNetworkCommandSet(
            runner=SafeCommandRunner(
                {
                    "network_linux_ip_route": ("ip", "route"),
                    "network_linux_ip_neigh": ("ip", "neigh", "show"),
                    "network_linux_arp_cache": ("arp", "-a"),
                },
                required_platform=LocalPlatform.LINUX,
            ),
            platform_name=LocalPlatform.LINUX,
            commands=(
                ("network_linux_ip_route", ["ip", "route"]),
                ("network_linux_ip_neigh", ["ip", "neigh", "show"]),
                ("network_linux_arp_cache", ["arp", "-a"]),
            ),
            route_command_names=("network_linux_ip_route",),
            neighbor_command_names=("network_linux_ip_neigh", "network_linux_arp_cache"),
        )
    if platform == Platform.WINDOWS:
        return PassiveNetworkCommandSet(
            runner=SafeCommandRunner(
                {
                    "network_windows_ipconfig": ("ipconfig",),
                    "network_windows_route_print": ("route", "print"),
                    "network_windows_arp_cache": ("arp", "-a"),
                },
                required_platform=LocalPlatform.WINDOWS,
            ),
            platform_name=LocalPlatform.WINDOWS,
            commands=(
                ("network_windows_ipconfig", ["ipconfig"]),
                ("network_windows_route_print", ["route", "print"]),
                ("network_windows_arp_cache", ["arp", "-a"]),
            ),
            route_command_names=("network_windows_ipconfig", "network_windows_route_print"),
            neighbor_command_names=("network_windows_arp_cache",),
        )
    return None


def _safe_output(result: CommandResult) -> str:
    return mask_mac_address("\n".join(part for part in [result.stdout, result.stderr] if part))


def _result_usable(result: CommandResult) -> bool:
    return result.supported and not result.timed_out and result.return_code in {0, None} and bool(result.stdout.strip())


def _private_ranges_from_text(text: str) -> list[str]:
    ranges: list[str] = []
    for match in CIDR_PATTERN.findall(text):
        try:
            network = ipaddress.ip_network(match, strict=False)
        except ValueError:
            continue
        if _network_private(network):
            _append_unique(ranges, str(network))
    for match in IP_PATTERN.findall(text):
        address = _parse_ip(match)
        if address and _is_private_address(address):
            _append_unique(ranges, _range_hint(address))
    return ranges


def _gateway_addresses(text: str) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    addresses: list[ipaddress.IPv4Address | ipaddress.IPv6Address] = []
    for line in text.splitlines():
        normalized = line.lower()
        if "default" not in normalized and "gateway" not in normalized and "0.0.0.0" not in normalized:
            continue
        for match in IP_PATTERN.findall(line):
            address = _parse_ip(match)
            if address and not address.is_unspecified:
                addresses.append(address)
    return addresses


def _passive_neighbor_count(text: str) -> int | None:
    if not text.strip():
        return None
    count = 0
    for line in text.splitlines():
        normalized = line.strip().lower()
        if not normalized or "incomplete" in normalized or "failed" in normalized:
            continue
        if IP_PATTERN.search(line):
            count += 1
    return count


def _neighbor_summary(count: int | None) -> str | None:
    if count is None:
        return None
    return f"Passive local cache shows {count} nearby network entries. No active discovery was run."


def _network_private(network: ipaddress.IPv4Network | ipaddress.IPv6Network) -> bool:
    if network.version == 6:
        return network.subnet_of(UNIQUE_LOCAL_IPV6)
    return any(network.subnet_of(private_range) for private_range in PRIVATE_IPV4_RANGES)


def _is_private_address(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    if address.version == 6:
        return address in UNIQUE_LOCAL_IPV6
    return any(address in private_range for private_range in PRIVATE_IPV4_RANGES)


def _range_hint(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> str:
    if address.version == 6:
        return "fc00::/7"
    octets = str(address).split(".")
    return f"{octets[0]}.{octets[1]}.{octets[2]}.0/24"


def _parse_ip(value: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    try:
        return ipaddress.ip_address(value.strip("[]"))
    except ValueError:
        return None


def _base_safety_notes() -> list[str]:
    return [
        "Passive local network context only.",
        "No active discovery was run.",
        "No ports were scanned.",
        "No packets were captured.",
        "No router login was attempted.",
        "No public targets were scanned.",
        "No data was uploaded.",
    ]


def _append_unique(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)


def _unique(values: list[str]) -> list[str]:
    unique_values: list[str] = []
    for value in values:
        if value not in unique_values:
            unique_values.append(value)
    return unique_values
