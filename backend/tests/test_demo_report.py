from fastapi.testclient import TestClient

from app.demo.demo_report import get_demo_report
from app.main import app


def test_demo_report_route_returns_demo_report_without_api_keys(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    client = TestClient(app)

    response = client.get("/demo/report")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "demo"
    assert payload["app"] == "AI HomeGuard"
    assert payload["findings"]
    assert payload["disclaimer"]
    assert payload["safety_notes"]


def test_demo_report_includes_d3fend_guidance_and_fake_data_notice() -> None:
    report = get_demo_report()

    assert report.mode == "demo"
    assert all(finding.d3fend_guidance for finding in report.findings)
    assert "fake sample findings" in report.disclaimer
    assert any("static sample data" in note for note in report.safety_notes)


def test_demo_report_has_no_real_network_scan_indicator() -> None:
    payload = get_demo_report().model_dump(mode="json")
    content = str(payload).lower()

    assert "no real network scan was run" in content
    assert "static report returned by /demo/report" in content
    assert "nmap" not in content
    assert "packet capture" in content


def test_demo_report_aliases_return_the_same_findings() -> None:
    client = TestClient(app)

    demo_report = client.get("/demo/report")
    reports_demo = client.get("/reports/demo")
    demo_findings = client.get("/demo/findings")

    assert demo_report.status_code == 200
    assert reports_demo.status_code == 200
    assert demo_findings.status_code == 200
    assert len(demo_report.json()["findings"]) == len(reports_demo.json()["findings"])
    assert len(demo_findings.json()) == len(demo_report.json()["findings"])
