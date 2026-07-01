from app.checks.macos.base import (
    MacOSCheckContext,
    command_text,
    command_unavailable,
    guidance,
    make_macos_finding,
    unable_to_check_finding,
)
from app.models.enums import Category, Confidence, D3FENDGuidanceCategory, Difficulty, FindingStatus, Severity
from app.models.evidence import Evidence
from app.models.finding import Finding


def check_macos_gatekeeper(context: MacOSCheckContext) -> Finding:
    result = context.runner.run(
        "macos_gatekeeper_status",
        ["spctl", "--status"],
        timeout_seconds=10,
        platform_name=context.platform_name,
    )
    if command_unavailable(result):
        return unable_to_check_finding(
            finding_id="macos-gatekeeper-unable-to-check",
            home_title="Gatekeeper status could not be checked",
            technical_title="spctl status unavailable",
            category=Category.DEVICE_POSTURE,
            summary="AI HomeGuard could not read Gatekeeper assessment status.",
            result=result,
        )
    return gatekeeper_finding_from_output(command_text(result))


def gatekeeper_finding_from_output(output: str) -> Finding:
    normalized = output.lower()
    enabled = "assessments enabled" in normalized
    disabled = "assessments disabled" in normalized
    if not enabled and not disabled:
        return unable_to_check_finding(
            finding_id="macos-gatekeeper-unclear",
            home_title="Gatekeeper status was unclear",
            technical_title="spctl output unclear",
            category=Category.DEVICE_POSTURE,
            summary="AI HomeGuard read Gatekeeper command output, but could not interpret it.",
        )

    return make_macos_finding(
        finding_id="macos-gatekeeper-status",
        title="Gatekeeper application assessment status",
        home_title="Gatekeeper is enabled" if enabled else "Gatekeeper needs review",
        technical_title="spctl assessment status",
        status=FindingStatus.GOOD if enabled else FindingStatus.FIX_SOON,
        severity=Severity.INFO if enabled else Severity.MEDIUM,
        confidence=Confidence.HIGH,
        category=Category.DEVICE_POSTURE,
        summary=(
            "Gatekeeper application assessment appears enabled."
            if enabled
            else "Gatekeeper application assessment appears disabled."
        ),
        why_it_matters="Gatekeeper helps warn before running unsigned or untrusted apps.",
        evidence=[
            Evidence(
                source="macOS local check",
                method="spctl --status",
                observed_value="assessments enabled" if enabled else "assessments disabled",
                expected_value="assessments enabled",
                notes="Read-only Gatekeeper status check. No application security settings were changed.",
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.HARDEN,
                "Application control",
                "Keep Gatekeeper enabled for normal home use.",
                "Application assessment helps reduce accidental execution of untrusted software.",
                Difficulty.EASY,
                10,
            )
        ],
        recommended_action=(
            "No immediate action from this check."
            if enabled
            else "Open macOS Privacy & Security settings and review app security options."
        ),
        difficulty=Difficulty.EASY,
        estimated_time_minutes=10,
        safe_to_ignore=enabled,
        tags=["gatekeeper", "application-control"],
    )
