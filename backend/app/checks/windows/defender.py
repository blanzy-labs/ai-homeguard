from typing import Any

from app.checks.windows.base import (
    WindowsCheckContext,
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


def check_windows_defender(context: WindowsCheckContext) -> Finding:
    result = context.runner.run(
        "windows_defender_status",
        powershell_args("Get-MpComputerStatus | ConvertTo-Json -Depth 3"),
        timeout_seconds=12,
        platform_name=context.platform_name,
    )
    data = parse_json_output(result)
    if not isinstance(data, dict):
        return unable_to_check_finding(
            finding_id="windows-defender-unable-to-check",
            home_title="Microsoft Defender status could not be checked",
            technical_title="Get-MpComputerStatus unavailable",
            category=Category.MALWARE_PROTECTION,
            summary="AI HomeGuard could not read Microsoft Defender status from Windows.",
            result=result,
        )

    return defender_finding_from_status(data)


def defender_finding_from_status(data: dict[str, Any]) -> Finding:
    antivirus_enabled = bool_from_windows(data.get("AntivirusEnabled"))
    realtime_enabled = bool_from_windows(data.get("RealTimeProtectionEnabled"))
    signatures_age = data.get("AntivirusSignatureAge")

    healthy = antivirus_enabled is True and realtime_enabled is True
    status = FindingStatus.GOOD if healthy else FindingStatus.FIX_SOON
    severity = Severity.INFO if healthy else Severity.MEDIUM
    confidence = Confidence.HIGH if antivirus_enabled is not None or realtime_enabled is not None else Confidence.LOW

    observed = (
        f"Antivirus enabled: {antivirus_enabled}; "
        f"real-time protection enabled: {realtime_enabled}; "
        f"signature age: {signatures_age if signatures_age is not None else 'unknown'}"
    )

    return make_windows_finding(
        finding_id="windows-defender-status",
        title="Windows Defender status",
        home_title="Microsoft Defender protection is on" if healthy else "Microsoft Defender needs review",
        technical_title="Microsoft Defender Antivirus and real-time protection status",
        status=status,
        severity=severity,
        confidence=confidence,
        category=Category.MALWARE_PROTECTION,
        summary=(
            "Microsoft Defender appears enabled with real-time protection on."
            if healthy
            else "Microsoft Defender or real-time protection appears disabled or unclear."
        ),
        why_it_matters="Endpoint protection helps block common unsafe downloads and suspicious files.",
        evidence=[
            Evidence(
                source="windows local check",
                method="Get-MpComputerStatus",
                observed_value=observed,
                expected_value="Antivirus enabled: true; real-time protection enabled: true",
                notes="Read-only status check. No Defender settings were changed.",
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.HARDEN,
                "Endpoint protection",
                "Keep endpoint protection enabled and allow security intelligence updates.",
                "Updated endpoint protection reduces exposure to common harmful files.",
                Difficulty.EASY,
                10,
            ),
            guidance(
                D3FENDGuidanceCategory.DETECT,
                "Security warning review",
                "Review Windows Security warnings if protection is disabled or out of date.",
                "Warnings often explain whether a setting was turned off temporarily or needs action.",
                Difficulty.EASY,
                10,
            ),
        ],
        recommended_action=(
            "No immediate action from this check."
            if healthy
            else "Open Windows Security and review Microsoft Defender protection status."
        ),
        difficulty=Difficulty.EASY,
        estimated_time_minutes=10,
        requires_admin=False,
        safe_to_ignore=healthy,
        tags=["defender", "malware-protection"],
    )
