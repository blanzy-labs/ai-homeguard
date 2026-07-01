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


def check_macos_firewall(context: MacOSCheckContext) -> Finding:
    result = context.runner.run(
        "macos_firewall_status",
        ["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"],
        timeout_seconds=10,
        platform_name=context.platform_name,
    )
    if command_unavailable(result):
        return unable_to_check_finding(
            finding_id="macos-firewall-unable-to-check",
            home_title="macOS firewall status could not be checked",
            technical_title="socketfilterfw unavailable",
            category=Category.DEVICE_POSTURE,
            summary="AI HomeGuard could not read the macOS Application Firewall status.",
            result=result,
        )
    return firewall_finding_from_output(command_text(result))


def firewall_finding_from_output(output: str) -> Finding:
    normalized = output.lower()
    enabled = "enabled" in normalized or "state = 1" in normalized
    disabled = "disabled" in normalized or "state = 0" in normalized
    if not enabled and not disabled:
        return unable_to_check_finding(
            finding_id="macos-firewall-unclear",
            home_title="macOS firewall status was unclear",
            technical_title="socketfilterfw output unclear",
            category=Category.DEVICE_POSTURE,
            summary="AI HomeGuard read the macOS firewall command output, but could not interpret it.",
        )

    return make_macos_finding(
        finding_id="macos-firewall-status",
        title="macOS Application Firewall status",
        home_title="macOS firewall is on" if enabled else "macOS firewall is off",
        technical_title="Application Firewall global state",
        status=FindingStatus.GOOD if enabled else FindingStatus.FIX_SOON,
        severity=Severity.INFO if enabled else Severity.MEDIUM,
        confidence=Confidence.HIGH,
        category=Category.DEVICE_POSTURE,
        summary=(
            "The macOS Application Firewall appears enabled."
            if enabled
            else "The macOS Application Firewall appears disabled."
        ),
        why_it_matters="The host firewall helps limit unsolicited inbound connections to the Mac.",
        evidence=[
            Evidence(
                source="macOS local check",
                method="socketfilterfw --getglobalstate",
                observed_value="firewall enabled" if enabled else "firewall disabled",
                expected_value="firewall enabled",
                notes="Read-only firewall status check. No firewall rules or settings were changed.",
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.HARDEN,
                "Host firewall",
                "Keep the macOS firewall enabled unless you have a specific reason to turn it off.",
                "Host firewall filtering reduces unexpected inbound access.",
                Difficulty.EASY,
                10,
            )
        ],
        recommended_action=(
            "No immediate action from this check."
            if enabled
            else "Open macOS System Settings and review Network Firewall settings."
        ),
        difficulty=Difficulty.EASY,
        estimated_time_minutes=10,
        safe_to_ignore=enabled,
        tags=["firewall", "device-posture"],
    )
