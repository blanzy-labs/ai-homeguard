from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.main import app
from app.models.enums import FindingStatus, Platform, ReportMode
from app.models.report import HomeGuardReport, ReportSummary


def discovery_payload(*, acknowledged: bool = True, private_only: bool = True, active: bool = False) -> dict:
    return {
        "authorization": {
            "acknowledged": acknowledged,
            "scope": "home_network",
            "statement_version": "v0.1.0-slice-14",
            "include_active_discovery": active,
            "user_understands_private_network_only": private_only,
        },
        "method": "passive_cache",
    }


def sample_report() -> HomeGuardReport:
    return HomeGuardReport(
        report_id="test-network-discovery",
        app="AI HomeGuard",
        version="0.1.0",
        generated_at=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
        mode=ReportMode.NETWORK_DISCOVERY,
        platform_scope=[Platform.NETWORK],
        summary=ReportSummary(
            overall_status=FindingStatus.GOOD,
            overall_score=100,
            good_count=1,
            review_count=0,
            fix_soon_count=0,
            needs_attention_count=0,
            unable_to_check_count=0,
            top_actions=[],
        ),
        findings=[],
        disclaimer="Test network discovery report.",
        safety_notes=["No public targets were scanned."],
    )


def test_discovery_policy_route_returns_plain_safety_boundaries() -> None:
    client = TestClient(app)

    response = client.get("/network/discovery-policy")

    assert response.status_code == 200
    payload = response.json()
    assert payload["authorization_required"] is True
    assert payload["allowed_scopes"] == ["home_network"]
    assert "No public targets" in payload["no_public_scanning"]
    assert "No ports" in payload["no_port_scanning"]
    assert "Nmap is not used" in payload["no_nmap"]


def test_network_discovery_route_requires_authorization() -> None:
    client = TestClient(app)

    response = client.post("/reports/network-discovery", json=discovery_payload(acknowledged=False))

    assert response.status_code == 400
    assert "authorization" in response.json()["detail"].lower()


def test_network_discovery_route_requires_private_only_acknowledgement() -> None:
    client = TestClient(app)

    response = client.post("/reports/network-discovery", json=discovery_payload(private_only=False))

    assert response.status_code == 400
    assert "private-network-only" in response.json()["detail"].lower()


def test_network_discovery_route_accepts_authorized_passive_request(monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        "app.api.routes.network.run_network_discovery_report",
        lambda request: calls.append(request.method.value) or sample_report(),
    )
    client = TestClient(app)

    response = client.post("/reports/network-discovery", json=discovery_payload())

    assert response.status_code == 200
    assert calls == ["passive_cache"]
    assert response.json()["mode"] == "network_discovery"


def test_network_discovery_demo_uses_fake_masked_devices() -> None:
    client = TestClient(app)

    response = client.get("/network/discovery/demo")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "network_discovery"
    assert payload["devices"]
    assert all("xx:xx:xx" in device["mac_hint"] for device in payload["devices"] if device["mac_hint"])
