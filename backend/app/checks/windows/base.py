from collections.abc import Sequence
from dataclasses import dataclass
import json
from typing import Any, Protocol

from app.core.command_runner import CommandResult, SafeCommandRunner
from app.core.platform import LocalPlatform
from app.models.enums import (
    Category,
    Confidence,
    D3FENDGuidanceCategory,
    Difficulty,
    FindingStatus,
    Platform,
    Severity,
)
from app.models.evidence import Evidence
from app.models.finding import Finding
from app.models.guidance import AttackContext, D3FENDGuidance


class CommandRunnerProtocol(Protocol):
    def run(
        self,
        command_name: str,
        args: Sequence[str],
        timeout_seconds: int = 10,
        platform_name: LocalPlatform | None = None,
    ) -> CommandResult:
        ...


WINDOWS_ALLOWED_COMMANDS = {
    "windows_defender_status": ("powershell",),
    "windows_firewall_profiles": ("powershell",),
    "windows_bitlocker_status": ("powershell",),
    "windows_manage_bde_status": ("manage-bde",),
    "windows_remote_desktop_registry": ("powershell",),
    "windows_remote_desktop_service": ("powershell",),
    "windows_listening_ports": ("powershell",),
    "windows_local_admins": ("powershell",),
    "windows_update_visibility": ("powershell",),
}


def create_windows_command_runner() -> SafeCommandRunner:
    return SafeCommandRunner(WINDOWS_ALLOWED_COMMANDS)


@dataclass(frozen=True)
class WindowsCheckContext:
    runner: CommandRunnerProtocol
    platform_name: LocalPlatform


def powershell_args(script: str) -> list[str]:
    return ["powershell", "-NoProfile", "-NonInteractive", "-Command", script]


def parse_json_output(result: CommandResult) -> Any | None:
    if result.return_code != 0 or not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def bool_from_windows(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "1", "on", "enabled"}:
            return True
        if normalized in {"false", "no", "0", "off", "disabled"}:
            return False
    return None


def unable_to_check_finding(
    *,
    finding_id: str,
    home_title: str,
    technical_title: str,
    category: Category,
    summary: str,
    result: CommandResult | None = None,
) -> Finding:
    notes = "The check could not complete. No settings were changed."
    if result and result.timed_out:
        notes = "The read-only command timed out. No settings were changed."
    elif result and result.error:
        notes = f"The read-only command could not run: {result.error}."
    elif result and result.return_code not in {None, 0}:
        notes = "The read-only command returned limited visibility or was unavailable."

    return make_windows_finding(
        finding_id=finding_id,
        title=home_title,
        home_title=home_title,
        technical_title=technical_title,
        status=FindingStatus.UNABLE_TO_CHECK,
        severity=Severity.INFO,
        confidence=Confidence.UNKNOWN,
        category=category,
        summary=summary,
        why_it_matters="This check needs Windows read-only system information that was not available.",
        evidence=[
            Evidence(
                source="windows local check",
                method=result.command_name if result else "platform guard",
                observed_value="unable to check",
                expected_value="read-only Windows information available",
                notes=notes,
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.EDUCATE,
                "Limited visibility handling",
                "Review this area manually on a Windows computer if it matters for your setup.",
                "AI HomeGuard reports limited visibility instead of requiring administrator access or changing settings.",
                Difficulty.EASY,
                10,
            )
        ],
        recommended_action="Run AI HomeGuard on a Windows computer or review this setting manually.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=10,
        requires_admin=True,
        tags=["windows", "unable-to-check"],
    )


def make_windows_finding(
    *,
    finding_id: str,
    title: str,
    home_title: str,
    technical_title: str | None,
    status: FindingStatus,
    severity: Severity,
    confidence: Confidence,
    category: Category,
    summary: str,
    why_it_matters: str,
    evidence: list[Evidence],
    d3fend_guidance: list[D3FENDGuidance],
    recommended_action: str,
    difficulty: Difficulty,
    estimated_time_minutes: int | None,
    user_can_fix: bool = True,
    requires_admin: bool = False,
    safe_to_ignore: bool = False,
    tags: list[str] | None = None,
    attack_context: list[AttackContext] | None = None,
) -> Finding:
    return Finding(
        id=finding_id,
        title=title,
        home_title=home_title,
        technical_title=technical_title,
        status=status,
        severity=severity,
        confidence=confidence,
        platform=Platform.WINDOWS,
        category=category,
        summary=summary,
        why_it_matters=why_it_matters,
        evidence=evidence,
        d3fend_guidance=d3fend_guidance,
        attack_context=attack_context or [],
        recommended_action=recommended_action,
        difficulty=difficulty,
        estimated_time_minutes=estimated_time_minutes,
        user_can_fix=user_can_fix,
        requires_admin=requires_admin,
        safe_to_ignore=safe_to_ignore,
        tags=["windows", *(tags or [])],
    )


def guidance(
    category: D3FENDGuidanceCategory,
    defensive_concept: str,
    home_action: str,
    rationale: str,
    difficulty: Difficulty,
    estimated_time_minutes: int,
    technical_action: str | None = None,
) -> D3FENDGuidance:
    return D3FENDGuidance(
        category=category,
        defensive_concept=defensive_concept,
        home_action=home_action,
        technical_action=technical_action,
        rationale=rationale,
        difficulty=difficulty,
        estimated_time_minutes=estimated_time_minutes,
    )
