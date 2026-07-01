from datetime import UTC, datetime
import pytest

from app.models.enums import Platform
from app.models.network import NetworkAuthorization, NetworkAuthorizationScope, NetworkContext
from app.models.runtime import RuntimeEnvironment
from app.network.context import _command_set_for_platform
from app.network.runner import NETWORK_AUTHORIZATION_ERROR, run_network_awareness


def authorized(scope: NetworkAuthorizationScope = NetworkAuthorizationScope.HOME_NETWORK) -> NetworkAuthorization:
    return NetworkAuthorization(
        acknowledged=True,
        scope=scope,
        statement_version="v0.1.0-network-awareness",
    )


def sample_context(environment: RuntimeEnvironment = RuntimeEnvironment.NATIVE) -> NetworkContext:
    return NetworkContext(
        runtime_platform=Platform.NETWORK,
        runtime_environment=environment,
        possible_private_ranges=["192.168.1.0/24"],
        gateway_present=True,
        gateway_private=True,
        passive_neighbor_count=2,
        passive_neighbor_summary="Passive local cache shows 2 nearby network entries. No active discovery was run.",
        limitations=["Mocked context."],
        safety_notes=["Passive local network context only."],
    )


def test_authorization_false_prevents_context_gathering(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.network.runner.collect_passive_network_context",
        lambda: (_ for _ in ()).throw(AssertionError("context should not be gathered")),
    )

    with pytest.raises(ValueError, match=NETWORK_AUTHORIZATION_ERROR):
        run_network_awareness(
            NetworkAuthorization(
                acknowledged=False,
                scope=NetworkAuthorizationScope.HOME_NETWORK,
                statement_version="v0.1.0-network-awareness",
            )
        )


def test_home_network_authorization_returns_report_with_guidance() -> None:
    report = run_network_awareness(
        authorized(),
        generated_at=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
        context=sample_context(),
    )

    assert report.mode == "network_awareness"
    assert report.findings
    assert all(finding.d3fend_guidance for finding in report.findings)
    assert any("No active discovery was run." in note for note in report.safety_notes)
    assert "scan ports" in report.disclaimer


def test_device_only_scope_is_rejected() -> None:
    with pytest.raises(ValueError, match="home_network or demo"):
        run_network_awareness(authorized(NetworkAuthorizationScope.DEVICE_ONLY), context=sample_context())


def test_demo_scope_uses_deterministic_context() -> None:
    report = run_network_awareness(authorized(NetworkAuthorizationScope.DEMO))

    assert report.mode == "network_awareness"
    assert any("Demo" in note or "Demo" in finding.summary for note in report.safety_notes for finding in report.findings)


def test_network_runner_source_does_not_define_active_scan_tools() -> None:
    command_text = []
    for platform in [Platform.MACOS, Platform.LINUX, Platform.WINDOWS]:
        command_set = _command_set_for_platform(platform)
        assert command_set is not None
        for _, args in command_set.commands:
            command_text.append(" ".join(args).lower())

    rendered = " ".join(command_text)
    for prohibited in ["nmap", "ping", "arp-scan", "netdiscover", "tcpdump", "tshark", "scapy"]:
        assert prohibited not in rendered
