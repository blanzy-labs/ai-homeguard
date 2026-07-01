from collections import Counter
from typing import Any

from app.checks.windows.base import (
    WindowsCheckContext,
    as_list,
    guidance,
    make_windows_finding,
    parse_json_output,
    powershell_args,
    unable_to_check_finding,
)
from app.models.enums import Category, Confidence, D3FENDGuidanceCategory, Difficulty, FindingStatus, Severity
from app.models.evidence import Evidence
from app.models.finding import Finding


def check_windows_local_admins(context: WindowsCheckContext) -> Finding:
    result = context.runner.run(
        "windows_local_admins",
        powershell_args(
            "Get-LocalGroupMember -Group Administrators | "
            "Select-Object Name, ObjectClass, PrincipalSource | ConvertTo-Json"
        ),
        timeout_seconds=12,
        platform_name=context.platform_name,
    )
    data = parse_json_output(result)
    members = [item for item in as_list(data) if isinstance(item, dict)]
    if not members:
        return unable_to_check_finding(
            finding_id="windows-local-admins-unable-to-check",
            home_title="Local administrator membership could not be summarized",
            technical_title="Get-LocalGroupMember unavailable",
            category=Category.IDENTITY_ACCESS,
            summary="AI HomeGuard could not read local Administrators group membership.",
            result=result,
        )
    return local_admin_finding_from_members(members)


def local_admin_finding_from_members(members: list[dict[str, Any]]) -> Finding:
    count = len(members)
    classes = Counter(str(member.get("ObjectClass", "Unknown")) for member in members)
    sources = Counter(str(member.get("PrincipalSource", "Unknown")) for member in members)
    multiple = count > 1

    return make_windows_finding(
        finding_id="windows-local-admins-summary",
        title="Windows local administrators summary",
        home_title="Local administrator access should be reviewed" if multiple else "Local administrator access looks limited",
        technical_title="Administrators group member count and category summary",
        status=FindingStatus.REVIEW if multiple else FindingStatus.GOOD,
        severity=Severity.LOW if multiple else Severity.INFO,
        confidence=Confidence.MEDIUM,
        category=Category.IDENTITY_ACCESS,
        summary=(
            "Multiple local administrator entries were found."
            if multiple
            else "Only one local administrator entry was found."
        ),
        why_it_matters="Daily use of administrator accounts can make accidental changes more likely.",
        evidence=[
            Evidence(
                source="windows local check",
                method="Get-LocalGroupMember -Group Administrators",
                observed_value=(
                    f"Administrators group contains {count} member(s); "
                    f"classes: {_counter_summary(classes)}; sources: {_counter_summary(sources)}"
                ),
                expected_value="only expected household administrator accounts",
                notes="Names were intentionally not included in the finding output.",
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.HARDEN,
                "Privilege reduction",
                "Use standard accounts for routine activity where practical.",
                "Reducing everyday administrator use lowers the chance of accidental system-wide changes.",
                Difficulty.MEDIUM,
                20,
            ),
            guidance(
                D3FENDGuidanceCategory.EDUCATE,
                "Administrator membership review",
                "Review who should have local administrator access.",
                "Keeping administrator membership understandable makes the device easier to manage.",
                Difficulty.MEDIUM,
                20,
            ),
        ],
        recommended_action=(
            "Review local administrator membership and remove accounts that do not need admin access."
            if multiple
            else "No immediate action from this check."
        ),
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=20,
        requires_admin=True,
        safe_to_ignore=not multiple,
        tags=["local-admins", "identity-access"],
    )


def _counter_summary(counter: Counter[str]) -> str:
    return ", ".join(f"{key}: {value}" for key, value in sorted(counter.items()))
