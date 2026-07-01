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
from app.models.guidance import AttackContext


def check_windows_remote_desktop(context: WindowsCheckContext) -> Finding:
    result = context.runner.run(
        "windows_remote_desktop_registry",
        powershell_args(
            "Get-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server' "
            "-Name fDenyTSConnections | Select-Object fDenyTSConnections | ConvertTo-Json"
        ),
        timeout_seconds=10,
        platform_name=context.platform_name,
    )
    data = parse_json_output(result)
    if not isinstance(data, dict):
        return unable_to_check_finding(
            finding_id="windows-remote-desktop-unable-to-check",
            home_title="Remote Desktop status could not be checked",
            technical_title="Remote Desktop registry value unavailable",
            category=Category.IDENTITY_ACCESS,
            summary="AI HomeGuard could not read the Remote Desktop status value.",
            result=result,
        )
    return remote_desktop_finding_from_registry(data)


def remote_desktop_finding_from_registry(data: dict[str, Any]) -> Finding:
    raw_value = data.get("fDenyTSConnections")
    disabled = str(raw_value).strip() in {"1", "True", "true"}
    enabled = str(raw_value).strip() in {"0", "False", "false"}

    return make_windows_finding(
        finding_id="windows-remote-desktop-status",
        title="Windows Remote Desktop status",
        home_title="Remote Desktop is off" if disabled else "Remote Desktop may need review",
        technical_title="Terminal Server fDenyTSConnections registry value",
        status=FindingStatus.GOOD if disabled else FindingStatus.REVIEW,
        severity=Severity.INFO if disabled else Severity.MEDIUM,
        confidence=Confidence.HIGH if disabled or enabled else Confidence.LOW,
        category=Category.IDENTITY_ACCESS,
        summary=(
            "Remote Desktop appears disabled."
            if disabled
            else "Remote Desktop appears enabled or could not be clearly interpreted."
        ),
        why_it_matters="Remote access can be useful, but it should be enabled only when needed and protected carefully.",
        evidence=[
            Evidence(
                source="windows local check",
                method="Get-ItemProperty fDenyTSConnections",
                observed_value=f"fDenyTSConnections: {raw_value}",
                expected_value="fDenyTSConnections: 1 when Remote Desktop is not needed",
                notes="Read-only registry value check. Remote Desktop settings were not changed.",
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.HARDEN,
                "Remote access reduction",
                "Disable Remote Desktop if no one in the household uses it.",
                "Removing unused remote access reduces ways the device can be reached.",
                Difficulty.MEDIUM,
                15,
            ),
            guidance(
                D3FENDGuidanceCategory.ISOLATE,
                "Network access control",
                "Restrict remote access to trusted networks if it must remain enabled.",
                "Trusted network restrictions reduce accidental exposure.",
                Difficulty.MEDIUM,
                20,
            ),
            guidance(
                D3FENDGuidanceCategory.HARDEN,
                "Authentication strengthening",
                "Use strong authentication for accounts allowed to connect remotely.",
                "Stronger sign-in settings help protect remote access.",
                Difficulty.MEDIUM,
                20,
            ),
        ],
        attack_context=[
            AttackContext(
                tactic="Lateral Movement",
                technique_id="T1021.001",
                technique_name="Remote Services: Remote Desktop Protocol",
                explanation=(
                    "ATT&CK documents Remote Desktop as a remote services technique. "
                    "This is educational context only and does not mean this device was attacked."
                ),
                confidence=Confidence.MEDIUM,
            )
        ]
        if not disabled
        else [],
        recommended_action=(
            "No immediate action from this check."
            if disabled
            else "Confirm whether Remote Desktop is needed. If not, disable it."
        ),
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=15,
        requires_admin=False,
        safe_to_ignore=disabled,
        tags=["remote-desktop", "identity-access"],
    )
