from collections.abc import Sequence

from app.core.command_runner import CommandResult
from app.core.platform import LocalPlatform
from app.models.enums import Platform
from app.models.runtime import RuntimeContext, RuntimeEnvironment
from app.network.context import PassiveNetworkCommandSet, collect_passive_network_context, mask_mac_address


class FakeNetworkRunner:
    def __init__(self, outputs: dict[str, str]) -> None:
        self.outputs = outputs
        self.calls: list[tuple[str, list[str]]] = []

    def run(
        self,
        command_name: str,
        args: Sequence[str],
        timeout_seconds: int = 5,
        platform_name: LocalPlatform | None = None,
    ) -> CommandResult:
        self.calls.append((command_name, list(args)))
        return CommandResult(command_name=command_name, return_code=0, stdout=self.outputs.get(command_name, ""))


def runtime_context(platform: Platform, environment: RuntimeEnvironment = RuntimeEnvironment.NATIVE) -> RuntimeContext:
    return RuntimeContext(
        detected_platform=platform,
        runtime_environment=environment,
        architecture="test-arch",
        hostname_present=True,
        platform_notes=[f"Detected platform: {platform.value}", f"Runtime environment: {environment.value}"],
        limitations=[],
    )


def command_set(
    *,
    platform: LocalPlatform,
    runner: FakeNetworkRunner,
    route_command_names: tuple[str, ...],
    neighbor_command_names: tuple[str, ...],
) -> PassiveNetworkCommandSet:
    commands = tuple(
        (command_name, [command_name.replace("_", "-")])
        for command_name in [*route_command_names, *neighbor_command_names]
    )
    return PassiveNetworkCommandSet(
        runner=runner,
        platform_name=platform,
        commands=commands,
        route_command_names=route_command_names,
        neighbor_command_names=neighbor_command_names,
    )


def test_macos_passive_context_parses_route_and_arp_safely() -> None:
    runner = FakeNetworkRunner(
        {
            "route": "gateway: 192.168.1.1\ninterface: en0\n",
            "arp": "? (192.168.1.22) at aa:bb:cc:dd:ee:ff on en0 ifscope [ethernet]\n",
        }
    )

    context = collect_passive_network_context(
        runtime_context=runtime_context(Platform.MACOS),
        command_set=command_set(
            platform=LocalPlatform.MACOS,
            runner=runner,
            route_command_names=("route",),
            neighbor_command_names=("arp",),
        ),
    )

    assert context.gateway_present is True
    assert context.gateway_private is True
    assert context.possible_private_ranges == ["192.168.1.0/24"]
    assert context.passive_neighbor_count == 1
    assert "aa:bb:cc:dd:ee:ff" not in context.model_dump_json()


def test_linux_passive_context_parses_route_and_neigh_safely() -> None:
    runner = FakeNetworkRunner(
        {
            "ip_route": "default via 10.0.0.1 dev eth0\n10.0.0.0/24 dev eth0 proto kernel\n",
            "ip_neigh": "10.0.0.42 dev eth0 lladdr aa:bb:cc:dd:ee:ff REACHABLE\n",
        }
    )

    context = collect_passive_network_context(
        runtime_context=runtime_context(Platform.LINUX),
        command_set=command_set(
            platform=LocalPlatform.LINUX,
            runner=runner,
            route_command_names=("ip_route",),
            neighbor_command_names=("ip_neigh",),
        ),
    )

    assert context.gateway_private is True
    assert context.possible_private_ranges == ["10.0.0.0/24"]
    assert context.passive_neighbor_summary == "Passive local cache shows 1 nearby network entries. No active discovery was run."


def test_windows_passive_context_parses_ipconfig_and_arp_safely() -> None:
    runner = FakeNetworkRunner(
        {
            "ipconfig": "IPv4 Address . . . : 192.168.0.44\nDefault Gateway . . . : 192.168.0.1\n",
            "arp": "192.168.0.10          aa-bb-cc-dd-ee-ff     dynamic\n",
        }
    )

    context = collect_passive_network_context(
        runtime_context=runtime_context(Platform.WINDOWS),
        command_set=command_set(
            platform=LocalPlatform.WINDOWS,
            runner=runner,
            route_command_names=("ipconfig",),
            neighbor_command_names=("arp",),
        ),
    )

    assert context.gateway_private is True
    assert context.possible_private_ranges == ["192.168.0.0/24"]
    assert context.passive_neighbor_count == 1


def test_container_runtime_adds_network_limitation() -> None:
    context = collect_passive_network_context(
        runtime_context=runtime_context(Platform.UNKNOWN, RuntimeEnvironment.DOCKER),
        command_set=None,
    )

    assert any("container" in limitation.lower() for limitation in context.limitations)


def test_mac_addresses_are_masked_if_seen_in_passive_output() -> None:
    assert mask_mac_address("aa:bb:cc:dd:ee:ff") == "aa:bb:cc:xx:xx:xx"
