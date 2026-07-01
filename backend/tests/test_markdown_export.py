from fastapi.testclient import TestClient

from app.main import app
from app.models.enums import FindingStatus, Platform
from app.reports.markdown import render_markdown_report
from tests.test_report_merge import make_finding, make_report


def test_markdown_report_includes_required_sections_and_guidance() -> None:
    finding = make_finding(
        "review-with-attack-context",
        FindingStatus.REVIEW,
        "questionnaire",
        "Review this calm action.",
        Platform.QUESTIONNAIRE,
    )
    report = make_report("markdown-report", [finding], ["No network scan was performed."])

    markdown = render_markdown_report(report)

    assert "# AI HomeGuard Report" in markdown
    assert "## Top Recommended Actions" in markdown
    assert "## D3FEND-Informed Defensive Guidance" in markdown
    assert "educational only" in markdown
    assert "Disclaimer for markdown-report." in markdown
    assert "Review this report before sharing" in markdown
    assert "OPENAI_API_KEY" not in markdown
    assert "sk-" not in markdown


def test_markdown_export_endpoint_returns_markdown() -> None:
    report = make_report(
        "markdown-route-report",
        [make_finding("fix", FindingStatus.FIX_SOON, "questionnaire", "Fix this soon.")],
        ["No data was uploaded."],
    )
    client = TestClient(app)

    response = client.post("/reports/export/markdown", json=report.model_dump(mode="json"))

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")
    assert "# AI HomeGuard Report" in response.text
    assert "Fix this soon." in response.text
