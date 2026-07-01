from fastapi.testclient import TestClient

from app.main import app
from tests.test_combined_report import questionnaire_payload
from tests.test_device_inventory_routes import inventory_payload


def test_combined_report_rejects_device_inventory_without_submission() -> None:
    client = TestClient(app)

    response = client.post(
        "/reports/combined",
        json={
            "include_questionnaire": True,
            "include_device_inventory": True,
            "questionnaire_submission": questionnaire_payload(),
        },
    )

    assert response.status_code == 400
    assert "device inventory submission" in response.json()["detail"].lower()


def test_combined_report_can_include_device_inventory() -> None:
    client = TestClient(app)

    response = client.post(
        "/reports/combined",
        json={
            "include_questionnaire": True,
            "include_device_inventory": True,
            "questionnaire_submission": questionnaire_payload(),
            "device_inventory_submission": inventory_payload(),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["report"]["mode"] == "combined"
    assert any(finding["tags"][0] == "device-inventory" for finding in payload["report"]["findings"])
    assert any("manual/demo device information" in limitation for limitation in payload["limitations"])
    assert "manual/demo device inventory" in payload["report"]["disclaimer"]
