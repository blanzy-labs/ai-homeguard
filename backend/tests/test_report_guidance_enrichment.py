from app.demo.demo_report import get_demo_report
from app.models.enums import FindingStatus
from app.models.questionnaire import QuestionnaireSubmission
from app.questionnaire.report_builder import build_questionnaire_report
from app.reports.json_export import render_json_export
from app.reports.markdown import render_markdown_report
from tests.test_combined_report import questionnaire_payload
from tests.test_guidance_service import finding_without_guidance
from tests.test_report_merge import make_report


def test_demo_and_questionnaire_reports_include_guidance() -> None:
    demo_report = get_demo_report()
    questionnaire_report = build_questionnaire_report(QuestionnaireSubmission.model_validate(questionnaire_payload()))

    assert all(finding.d3fend_guidance for finding in demo_report.findings)
    assert all(finding.d3fend_guidance for finding in questionnaire_report.findings)
    assert any(
        guidance.guidance_id == "strengthen_authentication"
        for finding in questionnaire_report.findings
        for guidance in finding.d3fend_guidance
    )


def test_exports_enrich_findings_lacking_guidance() -> None:
    report = make_report(
        "guidance-export-report",
        [finding_without_guidance().model_copy(update={"status": FindingStatus.REVIEW})],
        ["No report was saved automatically."],
    )

    exported = render_json_export(report)
    markdown = render_markdown_report(report)

    assert exported["findings"][0]["d3fend_guidance"][0]["guidance_id"] == "enable_full_disk_encryption"
    assert "D3FEND-style countermeasure thinking" in markdown
    assert "do not guarantee complete protection" in markdown
