from typing import Any

from app.checks.windows.base import (
    WindowsCheckContext,
    guidance,
    make_windows_finding,
    parse_json_output,
    powershell_args,
    unable_to_check_finding,
)
from app.models.enums import Category, Confidence, D3FENDGuidanceCategory, Difficulty, FindingStatus, Severity
from app.models.evidence import Evidence
from app.models.finding import Finding


def check_windows_update_visibility(context: WindowsCheckContext) -> Finding:
    result = context.runner.run(
        "windows_update_visibility",
        powershell_args(
            "Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber | ConvertTo-Json"
        ),
        timeout_seconds=15,
        platform_name=context.platform_name,
    )
    data = parse_json_output(result)
    if not isinstance(data, dict):
        return unable_to_check_finding(
            finding_id="windows-update-visibility-unable-to-check",
            home_title="Windows update visibility could not be checked",
            technical_title="Get-ComputerInfo unavailable",
            category=Category.UPDATES,
            summary="AI HomeGuard could not read basic Windows version information.",
            result=result,
        )
    return update_visibility_finding_from_computer_info(data)


def update_visibility_finding_from_computer_info(data: dict[str, Any]) -> Finding:
    product = data.get("WindowsProductName", "Windows")
    version = data.get("WindowsVersion", "unknown")
    build = data.get("OsBuildNumber", "unknown")
    return make_windows_finding(
        finding_id="windows-update-visibility",
        title="Windows update visibility",
        home_title="Windows version information was visible",
        technical_title="Windows product version and OS build",
        status=FindingStatus.REVIEW,
        severity=Severity.INFO,
        confidence=Confidence.MEDIUM,
        category=Category.UPDATES,
        summary="AI HomeGuard read basic Windows version information, but did not verify full patch status.",
        why_it_matters="Keeping Windows updated helps receive reliability and security improvements.",
        evidence=[
            Evidence(
                source="windows local check",
                method="Get-ComputerInfo",
                observed_value=f"{product}; version: {version}; build: {build}",
                expected_value="Windows Update enabled and current",
                notes="Read-only OS visibility check. This does not prove the device is fully patched.",
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.HARDEN,
                "Operating system update maintenance",
                "Keep Windows Update enabled and restart when updates need it.",
                "Updates often include security, reliability, and compatibility fixes.",
                Difficulty.EASY,
                15,
            ),
            guidance(
                D3FENDGuidanceCategory.EDUCATE,
                "Patch status review",
                "Use Windows Settings to review pending updates.",
                "AI HomeGuard does not claim full patch status from this light visibility check.",
                Difficulty.EASY,
                10,
            ),
        ],
        recommended_action="Open Windows Update and confirm there are no pending updates or required restarts.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=15,
        requires_admin=False,
        tags=["updates", "visibility"],
    )
