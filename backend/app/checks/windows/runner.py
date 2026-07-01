from datetime import UTC, datetime

from app.checks.windows.base import WindowsCheckContext, create_windows_command_runner, guidance, make_windows_finding
from app.checks.windows.bitlocker import check_windows_bitlocker
from app.checks.windows.defender import check_windows_defender
from app.checks.windows.firewall import check_windows_firewall
from app.checks.windows.listening_ports import check_windows_listening_ports
from app.checks.windows.local_admin import check_windows_local_admins
from app.checks.windows.remote_desktop import check_windows_remote_desktop
from app.checks.windows.update_status import check_windows_update_visibility
from app.core.platform import LocalPlatform, current_platform
from app.models.enums import Category, Confidence, D3FENDGuidanceCategory, Difficulty, FindingStatus, ReportMode, Severity
from app.models.evidence import Evidence
from app.models.finding import Finding
from app.models.report import HomeGuardReport, ReportSummary
from app.knowledge.guidance_service import enrich_report_guidance
from app.version import APP_NAME, APP_VERSION

WINDOWS_LOCAL_AUDIT_DISCLAIMER = (
    "Windows local audit results are based on read-only local checks. AI HomeGuard does not change "
    "settings, perform remediation, scan networks, upload data, or call an AI provider."
)


def run_windows_local_audit(
    *,
    platform_name: LocalPlatform | None = None,
    generated_at: datetime | None = None,
) -> HomeGuardReport:
    active_platform = platform_name or current_platform()
    report_time = generated_at or datetime.now(UTC)
    if active_platform != LocalPlatform.WINDOWS:
        findings = [_unsupported_platform_finding(active_platform)]
    else:
        context = WindowsCheckContext(
            runner=create_windows_command_runner(),
            platform_name=active_platform,
        )
        findings = [
            check_windows_defender(context),
            check_windows_firewall(context),
            check_windows_bitlocker(context),
            check_windows_remote_desktop(context),
            check_windows_listening_ports(context),
            check_windows_local_admins(context),
            check_windows_update_visibility(context),
        ]

    return enrich_report_guidance(HomeGuardReport(
        report_id=f"windows-local-audit-{report_time.strftime('%Y%m%d%H%M%S')}",
        app=APP_NAME,
        version=APP_VERSION,
        generated_at=report_time,
        mode=ReportMode.LOCAL,
        platform_scope=[finding.platform for finding in findings],
        summary=_summary_from_findings(findings),
        findings=findings,
        disclaimer=WINDOWS_LOCAL_AUDIT_DISCLAIMER,
        safety_notes=[
            "Read-only local checks only.",
            "No Windows settings were changed.",
            "No remediation was attempted.",
            "No network scan was performed.",
            "No external upload or AI provider call was performed.",
            "On non-Windows platforms, Windows checks return an unsupported-platform report.",
        ],
    ))


def run_windows_check_findings() -> list[Finding]:
    return run_windows_local_audit().findings


def _unsupported_platform_finding(active_platform: LocalPlatform) -> Finding:
    return make_windows_finding(
        finding_id="windows-local-audit-unsupported-platform",
        title="Windows local checks unavailable on this platform",
        home_title="Windows checks can only run on Windows",
        technical_title="Unsupported platform for Windows local audit",
        status=FindingStatus.UNABLE_TO_CHECK,
        severity=Severity.INFO,
        confidence=Confidence.HIGH,
        category=Category.DEVICE_POSTURE,
        summary=(
            f"AI HomeGuard is running on {active_platform.value}, so Windows local checks were not executed."
        ),
        why_it_matters="Windows posture checks need Windows read-only system information from the local computer.",
        evidence=[
            Evidence(
                source="platform guard",
                method="current_platform",
                observed_value=f"current platform: {active_platform.value}",
                expected_value="windows",
                notes="No Windows commands were run on this platform.",
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.EDUCATE,
                "Platform-specific validation",
                "Run Windows local checks only when AI HomeGuard is running on a Windows computer.",
                "Platform guards prevent unsupported checks from running on macOS or Linux.",
                Difficulty.EASY,
                5,
            )
        ],
        recommended_action="Run AI HomeGuard on a Windows computer to use Windows local checks.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=5,
        user_can_fix=True,
        requires_admin=False,
        tags=["unsupported-platform"],
    )


def _summary_from_findings(findings: list[Finding]) -> ReportSummary:
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
