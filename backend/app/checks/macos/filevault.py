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


def check_macos_filevault(context: MacOSCheckContext) -> Finding:
    result = context.runner.run(
        "macos_filevault_status",
        ["fdesetup", "status"],
        timeout_seconds=10,
        platform_name=context.platform_name,
    )
    if command_unavailable(result):
        return unable_to_check_finding(
            finding_id="macos-filevault-unable-to-check",
            home_title="FileVault status could not be checked",
            technical_title="fdesetup status unavailable",
            category=Category.DATA_PROTECTION,
            summary="AI HomeGuard could not read FileVault status.",
            result=result,
        )
    return filevault_finding_from_output(command_text(result))


def filevault_finding_from_output(output: str) -> Finding:
    normalized = output.lower()
    enabled = "filevault is on" in normalized or "encryption in progress" in normalized
    disabled = "filevault is off" in normalized or "decryption in progress" in normalized
    if not enabled and not disabled:
        return unable_to_check_finding(
            finding_id="macos-filevault-unclear",
            home_title="FileVault status was unclear",
            technical_title="fdesetup output unclear",
            category=Category.DATA_PROTECTION,
            summary="AI HomeGuard read FileVault command output, but could not interpret it.",
        )

    return make_macos_finding(
        finding_id="macos-filevault-status",
        title="FileVault disk encryption status",
        home_title="FileVault is on" if enabled else "FileVault is off",
        technical_title="fdesetup FileVault status",
        status=FindingStatus.GOOD if enabled else FindingStatus.FIX_SOON,
        severity=Severity.INFO if enabled else Severity.MEDIUM,
        confidence=Confidence.HIGH,
        category=Category.DATA_PROTECTION,
        summary=(
            "FileVault full-disk encryption appears enabled."
            if enabled
            else "FileVault full-disk encryption appears disabled or being turned off."
        ),
        why_it_matters="Disk encryption helps protect data if a Mac is lost or stolen.",
        evidence=[
            Evidence(
                source="macOS local check",
                method="fdesetup status",
                observed_value="FileVault enabled" if enabled else "FileVault disabled",
                expected_value="FileVault enabled",
                notes="Read-only FileVault status check. No disk or encryption settings were changed.",
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.HARDEN,
                "Full-disk encryption",
                "Keep FileVault enabled on portable Macs and other devices with personal data.",
                "Full-disk encryption reduces exposure from device loss or theft.",
                Difficulty.MEDIUM,
                20,
            )
        ],
        recommended_action=(
            "No immediate action from this check."
            if enabled
            else "Open macOS System Settings and review FileVault disk encryption."
        ),
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=20,
        requires_admin=not enabled,
        safe_to_ignore=enabled,
        tags=["filevault", "disk-encryption"],
    )
