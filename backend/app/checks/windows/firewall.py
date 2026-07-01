from typing import Any

from app.checks.windows.base import (
    WindowsCheckContext,
    as_list,
    bool_from_windows,
    guidance,
    make_windows_finding,
    parse_json_output,
    powershell_args,
    unable_to_check_finding,
)
from app.models.enums import Category, Confidence, D3FENDGuidanceCategory, Difficulty, FindingStatus, Severity
from app.models.evidence import Evidence
from app.models.finding import Finding


def check_windows_firewall(context: WindowsCheckContext) -> Finding:
    result = context.runner.run(
        "windows_firewall_profiles",
        powershell_args("Get-NetFirewallProfile | Select-Object Name, Enabled | ConvertTo-Json"),
        timeout_seconds=12,
        platform_name=context.platform_name,
    )
    data = parse_json_output(result)
    profiles = [item for item in as_list(data) if isinstance(item, dict)]
    if not profiles:
        return unable_to_check_finding(
            finding_id="windows-firewall-unable-to-check",
            home_title="Windows Firewall status could not be checked",
            technical_title="Get-NetFirewallProfile unavailable",
            category=Category.DEVICE_POSTURE,
            summary="AI HomeGuard could not read Windows Firewall profile status.",
            result=result,
        )
    return firewall_finding_from_profiles(profiles)


def firewall_finding_from_profiles(profiles: list[dict[str, Any]]) -> Finding:
    disabled_profiles = [
        str(profile.get("Name", "Unknown"))
        for profile in profiles
        if bool_from_windows(profile.get("Enabled")) is False
    ]
    unknown_profiles = [
        str(profile.get("Name", "Unknown"))
        for profile in profiles
        if bool_from_windows(profile.get("Enabled")) is None
    ]
    all_enabled = not disabled_profiles and not unknown_profiles

    return make_windows_finding(
        finding_id="windows-firewall-status",
        title="Windows Firewall status",
        home_title="Windows Firewall is on" if all_enabled else "Windows Firewall profiles need review",
        technical_title="Windows Firewall profile enabled status",
        status=FindingStatus.GOOD if all_enabled else FindingStatus.FIX_SOON,
        severity=Severity.INFO if all_enabled else Severity.MEDIUM,
        confidence=Confidence.HIGH if not unknown_profiles else Confidence.MEDIUM,
        category=Category.DEVICE_POSTURE,
        summary=(
            "All Windows Firewall profiles appear enabled."
            if all_enabled
            else "One or more Windows Firewall profiles appear disabled or unclear."
        ),
        why_it_matters="The host firewall helps limit unsolicited inbound connections to the device.",
        evidence=[
            Evidence(
                source="windows local check",
                method="Get-NetFirewallProfile",
                observed_value=_profile_summary(profiles),
                expected_value="Domain, Private, and Public profiles enabled",
                notes="Read-only firewall profile check. No firewall rules or settings were changed.",
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.HARDEN,
                "Host firewall",
                "Keep Windows Firewall enabled for all profiles.",
                "Host firewall filtering reduces unexpected inbound access.",
                Difficulty.EASY,
                10,
            ),
            guidance(
                D3FENDGuidanceCategory.HARDEN,
                "Allowed application review",
                "Review allowed apps if a program asks for firewall access.",
                "Keeping allowed apps tidy reduces unnecessary exposure.",
                Difficulty.MEDIUM,
                15,
            ),
        ],
        recommended_action=(
            "No immediate action from this check."
            if all_enabled
            else "Open Windows Security and review Windows Firewall profile settings."
        ),
        difficulty=Difficulty.EASY,
        estimated_time_minutes=10,
        requires_admin=False,
        safe_to_ignore=all_enabled,
        tags=["firewall", "device-posture"],
    )


def _profile_summary(profiles: list[dict[str, Any]]) -> str:
    parts = []
    for profile in profiles:
        name = profile.get("Name", "Unknown")
        enabled = bool_from_windows(profile.get("Enabled"))
        parts.append(f"{name}: {'enabled' if enabled else 'disabled' if enabled is False else 'unknown'}")
    return "; ".join(parts)
