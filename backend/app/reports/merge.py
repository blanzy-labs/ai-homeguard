from datetime import UTC, datetime
from collections.abc import Iterable

from app.models.enums import FindingStatus, ReportMode
from app.models.finding import Finding
from app.models.report import HomeGuardReport, ReportSummary
from app.knowledge.guidance_service import enrich_finding_guidance
from app.version import APP_NAME, APP_VERSION

COMBINED_REPORT_DISCLAIMER = (
    "This combined AI HomeGuard report may include questionnaire-derived findings and read-only "
    "local device audit findings. AI HomeGuard did not scan the network, change settings, upload "
    "data, call an AI provider, or save this report automatically."
)


def merge_reports(reports: list[HomeGuardReport], mode: str = "local") -> HomeGuardReport:
    return merge_homeguard_reports(reports, mode=mode)


def merge_homeguard_reports(
    reports: list[HomeGuardReport],
    mode: str = "combined",
) -> HomeGuardReport:
    findings = [
        enrich_finding_guidance(finding)
        for finding in _dedupe_findings(finding for report in reports for finding in report.findings)
    ]
    generated_at = reports[0].generated_at if reports else datetime.now(UTC)
    safety_notes = _unique(note for report in reports for note in report.safety_notes)
    platform_scope = _unique(finding.platform for finding in findings)
    runtime_context = next((report.runtime_context for report in reports if report.runtime_context), None)
    disclaimers = _unique(report.disclaimer for report in reports if report.disclaimer)
    disclaimer = _combined_disclaimer(disclaimers)

    return HomeGuardReport(
        report_id=f"homeguard-{mode}-report-{generated_at.strftime('%Y%m%d%H%M%S')}",
        app=reports[0].app if reports else APP_NAME,
        version=reports[0].version if reports else APP_VERSION,
        generated_at=generated_at,
        mode=ReportMode.COMBINED if mode == "combined" else ReportMode.LOCAL,
        platform_scope=platform_scope,
        summary=summary_from_findings(findings),
        findings=findings,
        disclaimer=disclaimer,
        safety_notes=safety_notes,
        runtime_context=runtime_context,
    )


def summary_from_findings(findings: list[Finding]) -> ReportSummary:
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
        top_actions=_top_actions(findings),
    )


def _unique(values):
    unique_values = []
    for value in values:
        if value not in unique_values:
            unique_values.append(value)
    return unique_values


def _top_actions(findings: list[Finding], limit: int = 5) -> list[str]:
    priority = {
        FindingStatus.NEEDS_ATTENTION: 0,
        FindingStatus.FIX_SOON: 1,
        FindingStatus.REVIEW: 2,
        FindingStatus.UNABLE_TO_CHECK: 3,
        FindingStatus.GOOD: 4,
    }
    action_candidates = sorted(
        (finding for finding in findings if not finding.safe_to_ignore and finding.status != FindingStatus.GOOD),
        key=lambda finding: (priority[finding.status], finding.id),
    )
    actions: list[str] = []
    for finding in action_candidates:
        if finding.status == FindingStatus.UNABLE_TO_CHECK and _generic_unable_action(finding.recommended_action):
            continue
        if finding.recommended_action not in actions:
            actions.append(finding.recommended_action)
        if len(actions) >= limit:
            break
    return actions


def _generic_unable_action(action: str) -> bool:
    normalized = action.lower()
    return "run ai homeguard on" in normalized or "unsupported" in normalized


def _dedupe_findings(findings: Iterable[Finding]) -> list[Finding]:
    deduped: list[Finding] = []
    seen: set[tuple[str, str]] = set()
    for finding in findings:
        source = finding.evidence[0].source if finding.evidence else "unknown"
        key = (finding.id, source)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(finding)
    return deduped


def _combined_disclaimer(disclaimers: list[str]) -> str:
    if not disclaimers:
        return COMBINED_REPORT_DISCLAIMER
    return f"{COMBINED_REPORT_DISCLAIMER} Source report disclaimers: " + " ".join(disclaimers)
