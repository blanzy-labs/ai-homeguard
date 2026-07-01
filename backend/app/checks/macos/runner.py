from datetime import UTC, datetime

from app.checks.macos.base import MacOSCheckContext, create_macos_command_runner, guidance, make_macos_finding
from app.checks.macos.filevault import check_macos_filevault
from app.checks.macos.firewall import check_macos_firewall
from app.checks.macos.gatekeeper import check_macos_gatekeeper
from app.checks.macos.listening_ports import check_macos_listening_ports
from app.checks.macos.remote_login import check_macos_remote_login
from app.checks.macos.system_info import check_macos_system_info
from app.checks.macos.updates import check_macos_update_visibility
from app.core.platform import LocalPlatform, current_platform
from app.models.enums import Category, Confidence, D3FENDGuidanceCategory, Difficulty, FindingStatus, ReportMode, Severity
from app.models.evidence import Evidence
from app.models.finding import Finding
from app.models.report import HomeGuardReport, ReportSummary
from app.knowledge.guidance_service import enrich_report_guidance
from app.version import APP_NAME, APP_VERSION

MACOS_LOCAL_AUDIT_DISCLAIMER = (
    "macOS local audit results are based on read-only local checks. AI HomeGuard does not change "
    "settings, perform remediation, scan networks, upload data, or call an AI provider."
)


def run_macos_local_audit(
    *,
    platform_name: LocalPlatform | None = None,
    generated_at: datetime | None = None,
) -> HomeGuardReport:
    active_platform = platform_name or current_platform()
    report_time = generated_at or datetime.now(UTC)
    if active_platform != LocalPlatform.MACOS:
        findings = [_unsupported_platform_finding(active_platform)]
    else:
        context = MacOSCheckContext(
            runner=create_macos_command_runner(),
            platform_name=active_platform,
        )
        findings = [
            check_macos_firewall(context),
            check_macos_filevault(context),
            check_macos_gatekeeper(context),
            check_macos_remote_login(context),
            check_macos_listening_ports(context),
            check_macos_system_info(context),
            check_macos_update_visibility(context),
        ]

    return enrich_report_guidance(HomeGuardReport(
        report_id=f"macos-local-audit-{report_time.strftime('%Y%m%d%H%M%S')}",
        app=APP_NAME,
        version=APP_VERSION,
        generated_at=report_time,
        mode=ReportMode.LOCAL,
        platform_scope=[finding.platform for finding in findings],
        summary=_summary_from_findings(findings),
        findings=findings,
        disclaimer=MACOS_LOCAL_AUDIT_DISCLAIMER,
        safety_notes=[
            "Read-only local checks only.",
            "No macOS settings were changed.",
            "No remediation was attempted.",
            "No network scan was performed.",
            "No external upload or AI provider call was performed.",
            "Listening services are summarized from the local Mac only.",
            "On non-macOS platforms, macOS checks return an unsupported-platform report.",
        ],
    ))


def run_macos_check_findings() -> list[Finding]:
    return run_macos_local_audit().findings


def _unsupported_platform_finding(active_platform: LocalPlatform) -> Finding:
    return make_macos_finding(
        finding_id="macos-local-audit-unsupported-platform",
        title="macOS local checks unavailable on this platform",
        home_title="macOS checks can only run on macOS",
        technical_title="Unsupported platform for macOS local audit",
        status=FindingStatus.UNABLE_TO_CHECK,
        severity=Severity.INFO,
        confidence=Confidence.HIGH,
        category=Category.DEVICE_POSTURE,
        summary=f"AI HomeGuard is running on {active_platform.value}, so macOS local checks were not executed.",
        why_it_matters="macOS posture checks need macOS read-only system information from the local computer.",
        evidence=[
            Evidence(
                source="platform guard",
                method="current_platform",
                observed_value=f"current platform: {active_platform.value}",
                expected_value="macos",
                notes="No macOS commands were run on this platform.",
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.EDUCATE,
                "Platform-specific validation",
                "Run macOS local checks only when AI HomeGuard is running on a Mac.",
                "Platform guards prevent unsupported checks from running on Windows or Linux.",
                Difficulty.EASY,
                5,
            )
        ],
        recommended_action="Run AI HomeGuard on a Mac to use macOS local checks.",
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
