from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.main import app
from app.models.enums import FindingStatus, Platform, ReportMode
from app.models.report import HomeGuardReport, ReportSummary


def sample_report() -> HomeGuardReport:
    return HomeGuardReport(
        report_id="combined-network-discovery",
        app="AI HomeGuard",
        version="0.1.0",
        generated_at=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
        mode=ReportMode.NETWORK_DISCOVERY,
        platform_scope=[Platform.NETWORK],
        summary=ReportSummary(
            overall_status=FindingStatus.REVIEW,
            overall_score=94,
            good_count=0,
            review_count=1,
            fix_soon_count=0,
            needs_attention_count=0,
            unable_to_check_count=0,
            top_actions=["Compare the device list with your router app."],
        ),
        findings=[],
        disclaimer="Network discovery test report.",
        safety_notes=["No public targets were scanned.", "No ports were scanned."],
    )


def discovery_payload() -> dict:
    return {
        "authorization": {
            "acknowledged": True,
            "scope": "home_network",
            "statement_version": "v0.1.0-slice-14",
            "include_active_discovery": False,
            "user_understands_private_network_only": True,
        },
        "method": "passive_cache",
    }


def test_combined_report_requires_discovery_request_when_enabled() -> None:
    client = TestClient(app)

    response = client.post(
        "/reports/combined",
        json={
            "include_questionnaire": False,
            "include_local_device": False,
            "include_network_discovery": True,
        },
    )

    assert response.status_code == 400
    assert "Network discovery request is required" in response.json()["detail"]


def test_combined_report_includes_authorized_network_discovery(monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        "app.api.routes.reports.run_network_discovery_report",
        lambda request: calls.append(request.method.value) or sample_report(),
    )
    client = TestClient(app)

    response = client.post(
        "/reports/combined",
        json={
            "include_questionnaire": False,
            "include_local_device": False,
            "include_network_discovery": True,
            "network_discovery_request": discovery_payload(),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert calls == ["passive_cache"]
    assert payload["report"]["mode"] == "combined"
    assert any("private IPv4" in limitation for limitation in payload["limitations"])
    assert "No public targets were scanned." in " ".join(payload["report"]["safety_notes"])
