from fastapi.testclient import TestClient

from app.checks.windows.runner import run_windows_local_audit
from app.core.platform import LocalPlatform, current_platform
from app.main import app


def test_platform_detection_values(monkeypatch) -> None:
    monkeypatch.setattr("platform.system", lambda: "Windows")
    assert current_platform() == LocalPlatform.WINDOWS

    monkeypatch.setattr("platform.system", lambda: "Darwin")
    assert current_platform() == LocalPlatform.MACOS

    monkeypatch.setattr("platform.system", lambda: "Linux")
    assert current_platform() == LocalPlatform.LINUX


def test_non_windows_platform_does_not_create_command_runner(monkeypatch) -> None:
    def fail_if_called():
        raise AssertionError("Windows command runner should not be created on non-Windows platforms")

    monkeypatch.setattr("app.checks.windows.runner.create_windows_command_runner", fail_if_called)

    report = run_windows_local_audit(platform_name=LocalPlatform.MACOS)

    assert report.mode == "local"
    assert report.findings[0].status == "unable_to_check"
    assert "No Windows commands were run" in report.findings[0].evidence[0].notes


def test_windows_local_report_route_returns_unsupported_on_non_windows(monkeypatch) -> None:
    monkeypatch.setattr("app.checks.windows.runner.current_platform", lambda: LocalPlatform.MACOS)
    client = TestClient(app)

    response = client.get("/reports/windows-local")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "local"
    assert payload["findings"][0]["status"] == "unable_to_check"
    assert "unsupported" in payload["findings"][0]["id"]


def test_windows_local_report_requires_no_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr("app.checks.windows.runner.current_platform", lambda: LocalPlatform.MACOS)
    client = TestClient(app)

    response = client.get("/reports/windows-local")

    assert response.status_code == 200
