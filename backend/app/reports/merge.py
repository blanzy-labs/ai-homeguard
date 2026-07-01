from datetime import UTC, datetime

from app.models.enums import FindingStatus, ReportMode
from app.models.report import HomeGuardReport, ReportSummary
from app.version import APP_NAME, APP_VERSION


def merge_reports(reports: list[HomeGuardReport], mode: str = "local") -> HomeGuardReport:
    findings = [finding for report in reports for finding in report.findings]
    generated_at = reports[0].generated_at if reports else datetime.now(UTC)
    safety_notes = _unique(note for report in reports for note in report.safety_notes)
    platform_scope = _unique(finding.platform for finding in findings)

    return HomeGuardReport(
        report_id=f"merged-{mode}-report-{generated_at.strftime('%Y%m%d%H%M%S')}",
        app=reports[0].app if reports else APP_NAME,
        version=reports[0].version if reports else APP_VERSION,
        generated_at=generated_at,
        mode=ReportMode.LOCAL if mode == "local" else reports[0].mode if reports else ReportMode.LOCAL,
        platform_scope=platform_scope,
        summary=summary_from_findings(findings),
        findings=findings,
        disclaimer=reports[0].disclaimer if reports else "Merged report generated from local AI HomeGuard reports.",
        safety_notes=safety_notes,
        runtime_context=reports[0].runtime_context if reports else None,
    )


def summary_from_findings(findings) -> ReportSummary:
    counts = {status: 0 for status in FindingStatus}
    for finding in findings:
        counts[finding.status] += 1

    if counts[FindingStatus.NEEDS_ATTENTION]:
        overall = FindingStatus.NEEDS_ATTENTION
    elif counts[FindingStatus.FIX_SOON]:
        overall = FindingStatus.FIX_SOON
    elif counts[FindingStatus.REVIEW]:
        overall = FindingStatus.REVIEW
    elif counts[FindingStatus.UNABLE_TO_CHECK]:
        overall = FindingStatus.UNABLE_TO_CHECK
    else:
        overall = FindingStatus.GOOD

    score = max(
        0,
        100
        - counts[FindingStatus.NEEDS_ATTENTION] * 18
        - counts[FindingStatus.FIX_SOON] * 12
        - counts[FindingStatus.REVIEW] * 6
        - counts[FindingStatus.UNABLE_TO_CHECK] * 3,
    )

    return ReportSummary(
        overall_status=overall,
        overall_score=score,
        good_count=counts[FindingStatus.GOOD],
        review_count=counts[FindingStatus.REVIEW],
        fix_soon_count=counts[FindingStatus.FIX_SOON],
        needs_attention_count=counts[FindingStatus.NEEDS_ATTENTION],
        unable_to_check_count=counts[FindingStatus.UNABLE_TO_CHECK],
        top_actions=[
            finding.recommended_action
            for finding in findings
            if finding.status != FindingStatus.GOOD and not finding.safe_to_ignore
        ][:5],
    )


def _unique(values):
    unique_values = []
    for value in values:
        if value not in unique_values:
            unique_values.append(value)
    return unique_values
