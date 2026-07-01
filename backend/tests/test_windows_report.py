from collections.abc import Sequence

from app.checks.windows.runner import run_windows_local_audit
from app.core.command_runner import CommandResult
from app.core.platform import LocalPlatform


class ReportFakeRunner:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def run(
        self,
        command_name: str,
        args: Sequence[str],
        timeout_seconds: int = 10,
        platform_name: LocalPlatform | None = None,
    ) -> CommandResult:
        self.calls.append(command_name)
        outputs = {
            "windows_defender_status": '{"AntivirusEnabled":true,"RealTimeProtectionEnabled":true}',
            "windows_firewall_profiles": '[{"Name":"Private","Enabled":true},{"Name":"Public","Enabled":true}]',
            "windows_bitlocker_status": '[{"MountPoint":"C:","ProtectionStatus":"Off","VolumeStatus":"FullyDecrypted"}]',
            "windows_remote_desktop_registry": '{"fDenyTSConnections":0}',
            "windows_listening_ports": '[{"LocalAddress":"0.0.0.0","LocalPort":3389,"OwningProcess":100}]',
            "windows_local_admins": '[{"Name":"DESKTOP-123\\\\Alice","ObjectClass":"User","PrincipalSource":"Local"},{"Name":"DESKTOP-123\\\\Bob","ObjectClass":"User","PrincipalSource":"Local"}]',
            "windows_update_visibility": '{"WindowsProductName":"Windows 11 Pro","WindowsVersion":"23H2","OsBuildNumber":"22631"}',
        }
        return CommandResult(command_name=command_name, return_code=0, stdout=outputs[command_name])


def test_mocked_windows_report_collects_findings(monkeypatch) -> None:
    fake_runner = ReportFakeRunner()
    monkeypatch.setattr("app.checks.windows.runner.create_windows_command_runner", lambda: fake_runner)

    report = run_windows_local_audit(platform_name=LocalPlatform.WINDOWS)

    assert report.mode == "local"
    assert len(report.findings) == 7
    assert fake_runner.calls == [
        "windows_defender_status",
        "windows_firewall_profiles",
        "windows_bitlocker_status",
        "windows_remote_desktop_registry",
        "windows_listening_ports",
        "windows_local_admins",
        "windows_update_visibility",
    ]
    assert report.summary.fix_soon_count >= 1
    assert report.summary.review_count >= 1
    assert all(finding.d3fend_guidance for finding in report.findings)
    assert any("No network scan" in note for note in report.safety_notes)


def test_windows_report_user_facing_output_omits_admin_names(monkeypatch) -> None:
    fake_runner = ReportFakeRunner()
    monkeypatch.setattr("app.checks.windows.runner.create_windows_command_runner", lambda: fake_runner)

    report = run_windows_local_audit(platform_name=LocalPlatform.WINDOWS)
    user_facing = " ".join(
        [
            report.summary.model_dump_json(),
            *[
                " ".join(
                    [
                        finding.home_title,
                        finding.summary,
                        finding.why_it_matters,
                        finding.recommended_action,
                        finding.evidence[0].observed_value,
                    ]
                )
                for finding in report.findings
            ],
        ]
    )

    assert "Alice" not in user_facing
    assert "Bob" not in user_facing


def test_windows_command_names_are_local_read_only() -> None:
    fake_runner = ReportFakeRunner()
    for command_name in [
        "windows_defender_status",
        "windows_firewall_profiles",
        "windows_bitlocker_status",
        "windows_remote_desktop_registry",
        "windows_listening_ports",
        "windows_local_admins",
        "windows_update_visibility",
    ]:
        result = fake_runner.run(command_name, [])
        assert result.command_name == command_name
        assert "nmap" not in result.stdout.lower()
        assert "clamscan" not in result.stdout.lower()
