from fastapi.testclient import TestClient

from app.main import app
from app.models.enums import FindingStatus
from app.reports.json_export import render_json_export
from tests.test_report_merge import make_finding, make_report


def test_json_export_returns_serializable_report_dict() -> None:
    report = make_report(
        "json-report",
        [make_finding("json-finding", FindingStatus.REVIEW, "questionnaire", "Review JSON export.")],
        ["No report was saved automatically."],
    )

    exported = render_json_export(report)

    assert exported["app"] == "AI HomeGuard"
    assert exported["mode"] == "local"
    assert exported["findings"][0]["id"] == "json-finding"
    assert "No report was saved automatically." in exported["safety_notes"]


def test_json_export_endpoint_validates_and_returns_json() -> None:
    report = make_report(
        "json-route-report",
        [make_finding("json-route-finding", FindingStatus.FIX_SOON, "questionnaire", "Review JSON route.")],
        ["Exports are user-triggered."],
    )
    client = TestClient(app)

    response = client.post("/reports/export/json", json=report.model_dump(mode="json"))

    assert response.status_code == 200
    payload = response.json()
    assert payload["report_id"] == "json-route-report"
    assert payload["findings"][0]["id"] == "json-route-finding"
