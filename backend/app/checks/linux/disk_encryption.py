from app.checks.linux.base import (
    LinuxCheckContext,
    command_missing_or_failed,
    command_text,
    guidance,
    make_linux_finding,
    unable_to_check_finding,
)
from app.models.enums import Category, Confidence, D3FENDGuidanceCategory, Difficulty, FindingStatus, Severity
from app.models.evidence import Evidence
from app.models.finding import Finding


def check_linux_disk_encryption(context: LinuxCheckContext) -> Finding:
    result = context.runner.run(
        "linux_lsblk_filesystems",
        ["lsblk", "-f"],
        timeout_seconds=10,
        platform_name=context.platform_name,
    )
    if command_missing_or_failed(result):
        return unable_to_check_finding(
            finding_id="linux-disk-encryption-unable-to-check",
            home_title="Linux disk encryption could not be checked",
            technical_title="lsblk -f unavailable",
            category=Category.DATA_PROTECTION,
            summary="AI HomeGuard could not read limited block-device filesystem information.",
            result=result,
        )
    return disk_encryption_finding_from_lsblk(command_text(result))


def disk_encryption_finding_from_lsblk(output: str) -> Finding:
    has_luks_marker = "crypto_luks" in output.lower() or "luks" in output.lower()
    if not has_luks_marker:
        return unable_to_check_finding(
            finding_id="linux-disk-encryption-limited",
            home_title="Linux disk encryption status is limited",
            technical_title="lsblk did not show an encryption marker",
            category=Category.DATA_PROTECTION,
            summary="AI HomeGuard could not safely confirm Linux disk encryption from unprivileged lsblk output.",
            method="lsblk -f",
            evidence_notes=(
                "No LUKS marker was visible in the limited read-only output. "
                "This is not treated as proof that disk encryption is off."
            ),
        )

    return make_linux_finding(
        finding_id="linux-disk-encryption-visible",
        title="Linux disk encryption visibility",
        home_title="Linux disk encryption marker was visible",
        technical_title="LUKS marker visible in lsblk -f",
        status=FindingStatus.GOOD,
        severity=Severity.INFO,
        confidence=Confidence.MEDIUM,
        category=Category.DATA_PROTECTION,
        summary="A Linux disk encryption marker appears visible in limited block-device output.",
        why_it_matters="Disk encryption helps protect data if a device is lost or stolen.",
        evidence=[
            Evidence(
                source="Linux local check",
                method="lsblk -f",
                observed_value="LUKS or crypto_LUKS marker visible",
                expected_value="disk encryption enabled where appropriate",
                notes="Read-only block-device summary. No disk settings were changed and full device details were not reported.",
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.HARDEN,
                "Full-disk encryption",
                "Keep disk encryption enabled on portable devices and systems with personal data.",
                "Full-disk encryption reduces exposure from device loss or theft.",
                Difficulty.ADVANCED,
                30,
            )
        ],
        recommended_action="No immediate action from this limited visibility check.",
        difficulty=Difficulty.ADVANCED,
        estimated_time_minutes=30,
        safe_to_ignore=True,
        tags=["disk-encryption", "luks"],
    )
