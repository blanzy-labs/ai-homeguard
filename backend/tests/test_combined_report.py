from fastapi.testclient import TestClient

from app.main import app
from app.models.enums import Platform
from tests.test_local_runner import sample_report


def questionnaire_payload() -> dict:
    return {
        "mode": "questionnaire",
        "answers": [
            {"question_id": "uses_password_manager", "value": "no", "skipped": False},
            {"question_id": "uses_mfa_important_accounts", "value": "some", "skipped": False},
        ],
    }


def test_combined_report_questionnaire_only_returns_combined_report() -> None:
    client = TestClient(app)

    response = client.post(
        "/reports/combined",
        json={
            "include_questionnaire": True,
            "include_local_device": False,
            "questionnaire_submission": questionnaire_payload(),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["report"]["mode"] == "combined"
    assert payload["report"]["findings"]
    assert payload["report"]["summary"]["top_actions"]
    assert payload["warnings"] == []
    assert any("No active network discovery" in item for item in payload["limitations"])


def test_combined_report_local_audit_requires_authorization() -> None:
    client = TestClient(app)

    response = client.post(
        "/reports/combined",
        json={
            "include_questionnaire": False,
            "include_local_device": True,
            "acknowledged_authorization": False,
        },
    )

    assert response.status_code == 400
    assert "authorization" in response.json()["detail"].lower()


def test_combined_report_with_local_authorization_calls_local_runner(monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        "app.api.routes.reports.run_local_device_audit",
        lambda: calls.append("local") or sample_report(Platform.MACOS),
    )
    client = TestClient(app)

    response = client.post(
        "/reports/combined",
        json={
            "include_questionnaire": True,
            "include_local_device": True,
            "acknowledged_authorization": True,
            "questionnaire_submission": questionnaire_payload(),
        },
    )

    assert response.status_code == 200
    assert calls == ["local"]
    payload = response.json()
    assert payload["report"]["mode"] == "combined"
    assert len(payload["report"]["findings"]) >= 2
    combined_notes = " ".join(payload["report"]["safety_notes"])
    assert "No network scan was performed." in combined_notes
    assert "not saved automatically" in combined_notes


def test_combined_report_requires_questionnaire_submission_when_selected() -> None:
    client = TestClient(app)

    response = client.post(
        "/reports/combined",
        json={"include_questionnaire": True, "include_local_device": False},
    )

    assert response.status_code == 400
    assert "questionnaire submission" in response.json()["detail"].lower()


def test_combined_report_requires_no_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    client = TestClient(app)

    response = client.post(
        "/reports/combined",
        json={
            "include_questionnaire": True,
            "include_local_device": False,
            "questionnaire_submission": questionnaire_payload(),
        },
    )

    assert response.status_code == 200
