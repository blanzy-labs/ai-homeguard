from collections.abc import Sequence

from app.checks.windows.base import WindowsCheckContext
from app.checks.windows.bitlocker import bitlocker_finding_from_volumes, check_windows_bitlocker
from app.checks.windows.defender import check_windows_defender, defender_finding_from_status
from app.checks.windows.firewall import firewall_finding_from_profiles
from app.checks.windows.listening_ports import listening_ports_finding_from_connections
from app.checks.windows.local_admin import local_admin_finding_from_members
from app.checks.windows.remote_desktop import remote_desktop_finding_from_registry
from app.core.command_runner import CommandResult
from app.core.platform import LocalPlatform


class FakeRunner:
    def __init__(self, results: dict[str, CommandResult]) -> None:
        self.results = results
        self.calls: list[str] = []

    def run(
        self,
        command_name: str,
        args: Sequence[str],
        timeout_seconds: int = 10,
        platform_name: LocalPlatform | None = None,
    ) -> CommandResult:
        self.calls.append(command_name)
        return self.results[command_name]


def test_mocked_defender_healthy_output_maps_to_good() -> None:
    finding = defender_finding_from_status(
        {
            "AntivirusEnabled": True,
            "RealTimeProtectionEnabled": True,
            "AntivirusSignatureAge": 0,
        }
    )

    assert finding.status == "good"
    assert finding.category == "malware_protection"
    assert finding.d3fend_guidance


def test_mocked_defender_disabled_output_maps_to_fix_soon() -> None:
    finding = defender_finding_from_status(
        {
            "AntivirusEnabled": False,
            "RealTimeProtectionEnabled": False,
            "AntivirusSignatureAge": 3,
        }
    )

    assert finding.status == "fix_soon"
    assert finding.severity == "medium"


def test_mocked_firewall_enabled_output_maps_to_good() -> None:
    finding = firewall_finding_from_profiles(
        [
            {"Name": "Domain", "Enabled": True},
            {"Name": "Private", "Enabled": True},
            {"Name": "Public", "Enabled": True},
        ]
    )

    assert finding.status == "good"
    assert finding.safe_to_ignore is True


def test_mocked_firewall_disabled_output_maps_to_fix_soon() -> None:
    finding = firewall_finding_from_profiles(
        [
            {"Name": "Domain", "Enabled": True},
            {"Name": "Private", "Enabled": False},
            {"Name": "Public", "Enabled": True},
        ]
    )

    assert finding.status == "fix_soon"
    assert "Private: disabled" in finding.evidence[0].observed_value


def test_mocked_bitlocker_off_maps_to_fix_soon() -> None:
    finding = bitlocker_finding_from_volumes(
        [
            {
                "MountPoint": "C:",
                "ProtectionStatus": "Off",
                "VolumeStatus": "FullyDecrypted",
            }
        ]
    )

    assert finding.status == "fix_soon"
    assert finding.category == "data_protection"


def test_mocked_remote_desktop_enabled_maps_to_review() -> None:
    finding = remote_desktop_finding_from_registry({"fDenyTSConnections": 0})

    assert finding.status == "review"
    assert finding.category == "identity_access"
    assert finding.attack_context
    assert finding.attack_context[0].educational_only is True


def test_mocked_listening_ports_with_remote_access_ports_maps_to_review() -> None:
    finding = listening_ports_finding_from_connections(
        [
            {"LocalAddress": "0.0.0.0", "LocalPort": 3389, "OwningProcess": 100},
            {"LocalAddress": "0.0.0.0", "LocalPort": 445, "OwningProcess": 200},
        ]
    )

    assert finding.status == "review"
    assert "3389" in finding.evidence[0].observed_value
    assert "445" in finding.evidence[0].observed_value


def test_local_admin_output_is_summarized_without_full_usernames() -> None:
    finding = local_admin_finding_from_members(
        [
            {"Name": "DESKTOP-123\\Alice", "ObjectClass": "User", "PrincipalSource": "Local"},
            {"Name": "DESKTOP-123\\Bob", "ObjectClass": "User", "PrincipalSource": "Local"},
            {"Name": "DOMAIN\\Helpdesk Admins", "ObjectClass": "Group", "PrincipalSource": "ActiveDirectory"},
        ]
    )

    combined_user_facing = " ".join(
        [
            finding.home_title,
            finding.summary,
            finding.why_it_matters,
            finding.evidence[0].observed_value,
            finding.recommended_action,
        ]
    )

    assert finding.status == "review"
    assert "3 member" in finding.evidence[0].observed_value
    assert "Alice" not in combined_user_facing
    assert "Bob" not in combined_user_facing
    assert "Helpdesk" not in combined_user_facing


def test_command_timeout_maps_to_unable_to_check() -> None:
    runner = FakeRunner(
        {
            "windows_defender_status": CommandResult(
                command_name="windows_defender_status",
                timed_out=True,
                error="Command timed out.",
            )
        }
    )
    context = WindowsCheckContext(runner=runner, platform_name=LocalPlatform.WINDOWS)

    finding = check_windows_defender(context)

    assert finding.status == "unable_to_check"
    assert "timed out" in finding.evidence[0].notes.lower()


def test_bitlocker_fallback_uses_manage_bde_when_powershell_unavailable() -> None:
    runner = FakeRunner(
        {
            "windows_bitlocker_status": CommandResult(
                command_name="windows_bitlocker_status",
                return_code=1,
                stderr="Get-BitLockerVolume not available",
            ),
            "windows_manage_bde_status": CommandResult(
                command_name="windows_manage_bde_status",
                return_code=0,
                stdout="Protection Status:    Protection On\nConversion Status:    Fully Encrypted",
            ),
        }
    )
    context = WindowsCheckContext(runner=runner, platform_name=LocalPlatform.WINDOWS)

    finding = check_windows_bitlocker(context)

    assert runner.calls == ["windows_bitlocker_status", "windows_manage_bde_status"]
    assert finding.status == "good"


def test_all_mocked_windows_findings_include_d3fend_guidance() -> None:
    findings = [
        defender_finding_from_status({"AntivirusEnabled": True, "RealTimeProtectionEnabled": True}),
        firewall_finding_from_profiles([{"Name": "Private", "Enabled": True}]),
        bitlocker_finding_from_volumes([{"MountPoint": "C:", "ProtectionStatus": "On"}]),
        remote_desktop_finding_from_registry({"fDenyTSConnections": 1}),
        listening_ports_finding_from_connections([{"LocalPort": 135}]),
        local_admin_finding_from_members([{"Name": "Hidden", "ObjectClass": "User"}]),
    ]

    assert all(finding.d3fend_guidance for finding in findings)
    assert all(finding.platform == "windows" for finding in findings)
