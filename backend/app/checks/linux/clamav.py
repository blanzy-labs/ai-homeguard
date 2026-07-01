from app.checks.linux.base import (
    LinuxCheckContext,
    command_missing_or_failed,
    command_text,
    guidance,
    make_linux_finding,
)
from app.models.enums import Category, Confidence, D3FENDGuidanceCategory, Difficulty, FindingStatus, Severity
from app.models.evidence import Evidence
from app.models.finding import Finding


def check_linux_clamav(context: LinuxCheckContext) -> Finding:
    clamscan = context.runner.run(
        "linux_clamscan_version",
        ["clamscan", "--version"],
        timeout_seconds=10,
        platform_name=context.platform_name,
    )
    if not command_missing_or_failed(clamscan):
        return clamav_finding_from_version(command_text(clamscan), "clamscan --version")

    freshclam = context.runner.run(
        "linux_freshclam_version",
        ["freshclam", "--version"],
        timeout_seconds=10,
        platform_name=context.platform_name,
    )
    if not command_missing_or_failed(freshclam):
        return clamav_finding_from_version(command_text(freshclam), "freshclam --version")

    return clamav_missing_finding()


def clamav_finding_from_version(version_output: str, method: str = "clamscan --version") -> Finding:
    first_line = version_output.splitlines()[0] if version_output.splitlines() else "ClamAV command found"
    return make_linux_finding(
        finding_id="linux-clamav-presence",
        title="ClamAV presence",
        home_title="ClamAV appears installed",
        technical_title="ClamAV version command available",
        status=FindingStatus.GOOD,
        severity=Severity.INFO,
        confidence=Confidence.MEDIUM,
        category=Category.MALWARE_PROTECTION,
        summary="A ClamAV command appears available on this Linux device.",
        why_it_matters="Malware scanning can be one useful layer, especially for shared files, but it is not the only Linux security control.",
        evidence=[
            Evidence(
                source="Linux local check",
                method=method,
                observed_value=first_line[:120],
                expected_value="ClamAV available if desired for this device",
                notes="Version-only presence check. AI HomeGuard did not run a file scan.",
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.DETECT,
                "Malware scanning awareness",
                "Keep malware scanning tools updated if you choose to use them.",
                "Scanner presence can support detection workflows, but signatures and safe habits still matter.",
                Difficulty.MEDIUM,
                15,
            )
        ],
        recommended_action="No immediate action from this presence check.",
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=15,
        safe_to_ignore=True,
        tags=["clamav", "malware-protection"],
    )


def clamav_missing_finding() -> Finding:
    return make_linux_finding(
        finding_id="linux-clamav-not-found",
        title="ClamAV presence",
        home_title="ClamAV was not found",
        technical_title="clamscan/freshclam version commands unavailable",
        status=FindingStatus.REVIEW,
        severity=Severity.INFO,
        confidence=Confidence.MEDIUM,
        category=Category.MALWARE_PROTECTION,
        summary="AI HomeGuard did not find common ClamAV commands on this Linux device.",
        why_it_matters="Some Linux users choose ClamAV for scanning shared files, but not every home Linux device needs it.",
        evidence=[
            Evidence(
                source="Linux local check",
                method="clamscan --version; freshclam --version",
                observed_value="ClamAV version commands not found",
                expected_value="ClamAV optional based on user needs",
                notes="Presence-only check. AI HomeGuard did not run a file scan or install packages.",
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.EDUCATE,
                "Malware scanning fit",
                "Decide whether a malware scanner fits how you use this Linux device.",
                "For many home setups, updates, least privilege, and trusted software sources matter more than optional scanner presence.",
                Difficulty.EASY,
                10,
            )
        ],
        recommended_action="Consider whether ClamAV is useful for this device, especially if it handles shared files.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=10,
        tags=["clamav", "malware-protection"],
    )
