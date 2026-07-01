from fastapi.testclient import TestClient

from app.main import app
from app.models.enums import Platform, ReportMode
from tests.test_local_runner import sample_report


def test_network_safety_policy_returns_200() -> None:
    client = TestClient(app)

    response = client.get("/network/safety-policy")

    assert response.status_code == 200
    payload = response.json()
    assert payload["statement_version"] == "v0.1.0-slice-9"
    assert "home_network" in payload["allowed_scopes"]
    assert "Nmap" in payload["disallowed_actions"]
    assert "public" in payload["no_public_scanning"].lower()


def test_network_awareness_without_acknowledgement_returns_400() -> None:
    client = TestClient(app)

    response = client.post(
        "/reports/network-awareness",
        json={"acknowledged": False, "scope": "home_network", "statement_version": "v0.1.0-slice-9"},
    )

    assert response.status_code == 400
    assert "authorization" in response.json()["detail"].lower()


def test_network_awareness_with_acknowledgement_returns_report(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.routes.network.run_network_awareness",
        lambda authorization: sample_report(Platform.NETWORK).model_copy(
            update={"mode": ReportMode.NETWORK_AWARENESS}
        ),
    )
    client = TestClient(app)

    response = client.post(
        "/reports/network-awareness",
        json={"acknowledged": True, "scope": "home_network", "statement_version": "v0.1.0-slice-9"},
    )

    assert response.status_code == 200
    assert response.json()["mode"] == "network_awareness"


def test_network_awareness_rejects_device_only_scope() -> None:
    client = TestClient(app)

    response = client.post(
        "/reports/network-awareness",
        json={"acknowledged": True, "scope": "device_only", "statement_version": "v0.1.0-slice-9"},
    )

    assert response.status_code == 400
    assert "home_network" in response.json()["detail"]
