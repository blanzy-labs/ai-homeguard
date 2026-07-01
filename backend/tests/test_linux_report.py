from collections.abc import Sequence

from fastapi.testclient import TestClient

from app.checks.linux.runner import run_linux_local_audit
from app.core.command_runner import CommandResult
from app.core.platform import LocalPlatform
from app.main import app


class LinuxReportFakeRunner:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[str]]] = []

    def run(
        self,
        command_name: str,
        args: Sequence[str],
        timeout_seconds: int = 10,
        platform_name: LocalPlatform | None = None,
    ) -> CommandResult:
        self.calls.append((command_name, list(args)))
        outputs = {
            "linux_firewall_ufw": "Status: active",
            "linux_firewall_firewall_cmd": "not running",
            "linux_firewall_firewalld_active": "inactive",
            "linux_ssh_systemctl_ssh": "inactive",
            "linux_ssh_systemctl_sshd": "active",
            "linux_ssh_service": "ssh is running",
            "linux_listening_ports_ss": (
                "Netid State Recv-Q Send-Q Local Address:Port Peer Address:Port\n"
                "tcp LISTEN 0 128 0.0.0.0:22 0.0.0.0:*"
            ),
            "linux_clamscan_version": "ClamAV 1.4.1/27000/Wed Jul  1 10:00:00 2026",
            "linux_os_release": 'PRETTY_NAME="Ubuntu 24.04 LTS"',
            "linux_uname_kernel": "6.8.0-31-generic",
            "linux_update_os_release": 'PRETTY_NAME="Ubuntu 24.04 LTS"',
            "linux_update_uname_kernel": "6.8.0-31-generic",
            "linux_lsblk_filesystems": "NAME FSTYPE FSVER LABEL UUID FSAVAIL FSUSE% MOUNTPOINTS\nsda\n",
        }
        return_code = 0 if outputs[command_name] not in {"inactive", "not running"} else 3
        return CommandResult(command_name=command_name, return_code=return_code, stdout=outputs[command_name])


def test_non_linux_platform_does_not_create_command_runner(monkeypatch) -> None:
    def fail_if_called():
        raise AssertionError("Linux command runner should not be created on non-Linux platforms")

    monkeypatch.setattr("app.checks.linux.runner.create_linux_command_runner", fail_if_called)

    report = run_linux_local_audit(platform_name=LocalPlatform.MACOS)

    assert report.mode == "local"
    assert report.findings[0].status == "unable_to_check"
    assert "No Linux commands were run" in report.findings[0].evidence[0].notes


def test_linux_local_report_route_returns_unsupported_on_non_linux(monkeypatch) -> None:
    monkeypatch.setattr("app.checks.linux.runner.current_platform", lambda: LocalPlatform.MACOS)
    client = TestClient(app)

    response = client.get("/reports/linux-local")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "local"
    assert payload["findings"][0]["status"] == "unable_to_check"
    assert "unsupported" in payload["findings"][0]["id"]


def test_mocked_linux_report_collects_findings(monkeypatch) -> None:
    fake_runner = LinuxReportFakeRunner()
    monkeypatch.setattr("app.checks.linux.runner.create_linux_command_runner", lambda: fake_runner)

    report = run_linux_local_audit(platform_name=LocalPlatform.LINUX)

    assert len(report.findings) == 7
    assert [call[0] for call in fake_runner.calls] == [
        "linux_firewall_ufw",
        "linux_firewall_firewall_cmd",
        "linux_firewall_firewalld_active",
        "linux_ssh_systemctl_ssh",
        "linux_ssh_systemctl_sshd",
        "linux_ssh_service",
        "linux_listening_ports_ss",
        "linux_clamscan_version",
        "linux_os_release",
        "linux_uname_kernel",
        "linux_update_os_release",
        "linux_update_uname_kernel",
        "linux_lsblk_filesystems",
    ]
    assert report.summary.review_count >= 1
    assert report.summary.unable_to_check_count >= 1
    assert all(finding.d3fend_guidance for finding in report.findings)
    assert any("No ClamAV file scan" in note for note in report.safety_notes)


def test_linux_local_report_requires_no_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr("app.checks.linux.runner.current_platform", lambda: LocalPlatform.MACOS)
    client = TestClient(app)

    response = client.get("/reports/linux-local")

    assert response.status_code == 200
