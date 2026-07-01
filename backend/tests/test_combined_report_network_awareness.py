from fastapi.testclient import TestClient

from app.main import app
from app.models.enums import Platform, ReportMode
from tests.test_combined_report import questionnaire_payload
from tests.test_local_runner import sample_report


def test_combined_report_rejects_network_awareness_without_authorization() -> None:
    client = TestClient(app)

    response = client.post(
        "/reports/combined",
        json={
            "include_questionnaire": True,
            "include_network_awareness": True,
            "questionnaire_submission": questionnaire_payload(),
        },
    )

    assert response.status_code == 400
    assert "network awareness requires authorization" in response.json()["detail"].lower()


def test_combined_report_can_include_authorized_network_awareness(monkeypatch) -> None:
    calls: list[str] = []

    def network_report(*args, **kwargs):
        report = sample_report(Platform.NETWORK)
        return report.model_copy(
            update={
                "mode": ReportMode.NETWORK_AWARENESS,
                "report_id": "mock-network-awareness",
                "safety_notes": ["No active discovery was run.", "No ports were scanned."],
            }
        )

    monkeypatch.setattr(
        "app.api.routes.reports.run_network_awareness",
        lambda authorization: calls.append(authorization.scope.value) or network_report(),
    )
    client = TestClient(app)

    response = client.post(
        "/reports/combined",
        json={
            "include_questionnaire": True,
            "include_network_awareness": True,
            "questionnaire_submission": questionnaire_payload(),
            "network_authorization": {
                "acknowledged": True,
                "scope": "home_network",
                "statement_version": "v0.1.0-slice-9",
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert calls == ["home_network"]
    assert payload["report"]["mode"] == "combined"
    assert any(finding["platform"] == "network" for finding in payload["report"]["findings"])
    assert any("passive only" in limitation for limitation in payload["limitations"])
