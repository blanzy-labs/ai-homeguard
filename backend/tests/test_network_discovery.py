from collections.abc import Sequence

from app.core.command_runner import CommandResult
from app.core.platform import LocalPlatform
from app.models.enums import Platform
from app.models.network import NetworkAuthorizationScope, NetworkContext
from app.models.network_discovery import (
    DiscoveryAuthorization,
    DiscoveryMethod,
    DiscoveryRuntimeMode,
    NetworkDiscoveryRequest,
)
from app.models.runtime import RuntimeEnvironment
from app.network.discovery import PassiveDiscoveryCommandSet, run_network_discovery, run_network_discovery_report


class FakeRunner:
    def __init__(self, results: dict[str, CommandResult] | None = None) -> None:
        self.results = results or {}
        self.calls: list[list[str]] = []

    def run(
        self,
        command_name: str,
        args: Sequence[str],
        timeout_seconds: int = 5,
        platform_name: LocalPlatform | None = None,
    ) -> CommandResult:
        self.calls.append(list(args))
        return self.results.get(command_name, CommandResult(command_name=command_name, return_code=1))


def discovery_request(
    *,
    method: DiscoveryMethod = DiscoveryMethod.PASSIVE_CACHE,
    active: bool = False,
    max_hosts: int = 64,
) -> NetworkDiscoveryRequest:
    return NetworkDiscoveryRequest(
        authorization=DiscoveryAuthorization(
            acknowledged=True,
            scope=NetworkAuthorizationScope.HOME_NETWORK,
            include_active_discovery=active,
            user_understands_private_network_only=True,
        ),
        method=method,
        max_hosts=max_hosts,
    )


def context(*, runtime: RuntimeEnvironment = RuntimeEnvironment.NATIVE) -> NetworkContext:
    return NetworkContext(
        runtime_platform=Platform.LINUX,
        runtime_environment=runtime,
        possible_private_ranges=["192.168.1.0/30"],
        gateway_present=True,
        gateway_private=True,
        passive_neighbor_count=None,
        limitations=[],
        safety_notes=[],
    )


def passive_command_set(runner: FakeRunner) -> PassiveDiscoveryCommandSet:
    return PassiveDiscoveryCommandSet(
        runner=runner,
        platform_name=LocalPlatform.LINUX,
        commands=(
            ("route", ["ip", "route"]),
            ("neighbors", ["ip", "neigh", "show"]),
        ),
        route_command_names=("route",),
        neighbor_command_names=("neighbors",),
    )


def test_passive_discovery_masks_macs_and_hides_hostnames() -> None:
    runner = FakeRunner(
        {
            "route": CommandResult(command_name="route", return_code=0, stdout="default via 192.168.1.1 dev en0"),
            "neighbors": CommandResult(
                command_name="neighbors",
                return_code=0,
                stdout=(
                    "phone.local (192.168.1.10) at aa:bb:cc:dd:ee:ff on en0\n"
                    "printer.local (192.168.1.11) at 11:22:33:44:55:66 on en0"
                ),
            ),
        }
    )

    result = run_network_discovery(
        discovery_request(),
        context=context(),
        passive_command_set=passive_command_set(runner),
    )

    assert result.discovered_count == 3
    assert result.gateway_detected is True
    assert any(device.label == "Router / Gateway" for device in result.devices)
    assert all("dd:ee:ff" not in (device.mac_hint or "") for device in result.devices)
    assert all("phone.local" not in (device.label or "") for device in result.devices)
    assert all("printer.local" not in note for device in result.devices for note in device.notes)


def test_active_private_ping_only_calls_private_ips() -> None:
    runner = FakeRunner(
        {
            "network_discovery_ping": CommandResult(
                command_name="network_discovery_ping",
                return_code=0,
                stdout="1 packets transmitted, 1 received",
            )
        }
    )

    result = run_network_discovery(
        discovery_request(method=DiscoveryMethod.PRIVATE_PING, active=True, max_hosts=2),
        context=context(),
        ping_runner=runner,
    )

    assert result.discovered_count == 2
    rendered_calls = [" ".join(call).lower() for call in runner.calls]
    assert rendered_calls
    assert all("192.168.1." in call for call in rendered_calls)
    assert all("nmap" not in call for call in rendered_calls)
    assert all("-p" not in call for call in rendered_calls)


def test_docker_limitation_maps_to_review_finding() -> None:
    report = run_network_discovery_report(
        discovery_request(),
        context=context(runtime=RuntimeEnvironment.DOCKER),
        passive_command_set=passive_command_set(FakeRunner()),
    )

    assert report.mode == "network_discovery"
    assert any(finding.id == "network-discovery-container-limitation" for finding in report.findings)
    assert any("container" in note.lower() for note in report.safety_notes)
