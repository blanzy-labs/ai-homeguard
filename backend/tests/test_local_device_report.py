from fastapi.testclient import TestClient

from app.main import app
from app.models.enums import Platform
from app.models.runtime import RuntimeContext, RuntimeEnvironment
from tests.test_local_runner import sample_report


def test_runtime_route_returns_privacy_safe_context(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.routes.local_checks.get_runtime_context",
        lambda: RuntimeContext(
            detected_platform=Platform.MACOS,
            runtime_environment=RuntimeEnvironment.NATIVE,
            architecture="arm64",
            hostname_present=True,
            platform_notes=["Detected platform: macos", "Runtime environment: native"],
            limitations=[],
        ),
    )
    client = TestClient(app)

    response = client.get("/runtime")

    assert response.status_code == 200
    payload = response.json()
    assert payload["detected_platform"] == "macos"
    assert payload["runtime_environment"] == "native"
    assert payload["hostname_present"] is True
    assert "hostname" not in payload
    assert "username" not in payload
    assert "environment_variables" not in payload


def test_local_device_report_route_returns_report(monkeypatch) -> None:
    report = sample_report(Platform.MACOS)
    report.runtime_context = RuntimeContext(
        detected_platform=Platform.MACOS,
        runtime_environment=RuntimeEnvironment.NATIVE,
        architecture="arm64",
        hostname_present=True,
        platform_notes=[],
        limitations=[],
    )
    report.safety_notes.append("No network scan was performed.")
    monkeypatch.setattr("app.api.routes.local_checks.run_local_device_audit", lambda: report)
    client = TestClient(app)

    response = client.get("/reports/local-device")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "local"
    assert payload["findings"]
    assert payload["safety_notes"]
    assert payload["runtime_context"]["detected_platform"] == "macos"


def test_local_device_report_requires_no_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr("app.api.routes.local_checks.run_local_device_audit", lambda: sample_report(Platform.LINUX))
    client = TestClient(app)

    response = client.get("/reports/local-device")

    assert response.status_code == 200
