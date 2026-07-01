from collections.abc import Sequence

from fastapi.testclient import TestClient

from app.checks.macos.runner import run_macos_local_audit
from app.core.command_runner import CommandResult
from app.core.platform import LocalPlatform
from app.main import app


class MacOSReportFakeRunner:
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
            "macos_firewall_status": "Firewall is enabled. (State = 1)",
            "macos_filevault_status": "FileVault is On.",
            "macos_gatekeeper_status": "assessments enabled",
            "macos_remote_login_status": "Remote Login: On",
            "macos_listening_ports_lsof": "sshd 111 root 5u IPv4 0xabc 0t0 TCP *:22 (LISTEN)",
            "macos_system_version": "ProductName: macOS\nProductVersion: 14.5\nBuildVersion: 23F79",
            "macos_update_visibility": "ProductName: macOS\nProductVersion: 14.5\nBuildVersion: 23F79",
        }
        return CommandResult(command_name=command_name, return_code=0, stdout=outputs[command_name])


def test_non_macos_platform_does_not_create_command_runner(monkeypatch) -> None:
    def fail_if_called():
        raise AssertionError("macOS command runner should not be created on non-macOS platforms")

    monkeypatch.setattr("app.checks.macos.runner.create_macos_command_runner", fail_if_called)

    report = run_macos_local_audit(platform_name=LocalPlatform.LINUX)

    assert report.mode == "local"
    assert report.findings[0].status == "unable_to_check"
    assert "No macOS commands were run" in report.findings[0].evidence[0].notes


def test_macos_local_report_route_returns_unsupported_on_non_macos(monkeypatch) -> None:
    monkeypatch.setattr("app.checks.macos.runner.current_platform", lambda: LocalPlatform.LINUX)
    client = TestClient(app)

    response = client.get("/reports/macos-local")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "local"
    assert payload["findings"][0]["status"] == "unable_to_check"
    assert "unsupported" in payload["findings"][0]["id"]


def test_mocked_macos_report_collects_findings(monkeypatch) -> None:
    fake_runner = MacOSReportFakeRunner()
    monkeypatch.setattr("app.checks.macos.runner.create_macos_command_runner", lambda: fake_runner)

    report = run_macos_local_audit(platform_name=LocalPlatform.MACOS)

    assert len(report.findings) == 7
    assert [call[0] for call in fake_runner.calls] == [
        "macos_firewall_status",
        "macos_filevault_status",
        "macos_gatekeeper_status",
        "macos_remote_login_status",
        "macos_listening_ports_lsof",
        "macos_system_version",
        "macos_update_visibility",
    ]
    assert report.summary.review_count >= 1
    assert all(finding.d3fend_guidance for finding in report.findings)
    assert any("No network scan" in note for note in report.safety_notes)


def test_macos_local_report_requires_no_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr("app.checks.macos.runner.current_platform", lambda: LocalPlatform.LINUX)
    client = TestClient(app)

    response = client.get("/reports/macos-local")

    assert response.status_code == 200
