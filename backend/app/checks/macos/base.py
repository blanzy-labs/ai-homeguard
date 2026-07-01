from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

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


MACOS_ALLOWED_COMMANDS = {
    "macos_firewall_status": ("/usr/libexec/ApplicationFirewall/socketfilterfw",),
    "macos_filevault_status": ("fdesetup",),
    "macos_gatekeeper_status": ("spctl",),
    "macos_remote_login_status": ("systemsetup",),
    "macos_listening_ports_lsof": ("lsof",),
    "macos_listening_ports_netstat": ("netstat",),
    "macos_system_version": ("sw_vers",),
    "macos_update_visibility": ("sw_vers",),
}


def create_macos_command_runner() -> SafeCommandRunner:
    return SafeCommandRunner(MACOS_ALLOWED_COMMANDS, required_platform=LocalPlatform.MACOS)


@dataclass(frozen=True)
class MacOSCheckContext:
    runner: CommandRunnerProtocol
    platform_name: LocalPlatform


def command_text(result: CommandResult) -> str:
    return "\n".join(part for part in [result.stdout, result.stderr] if part).strip()


def command_unavailable(result: CommandResult) -> bool:
    text = command_text(result).lower()
    return (
        not result.supported
        or result.timed_out
        or result.return_code not in {0, None}
        or "administrator" in text
        or "not permitted" in text
        or "operation not permitted" in text
        or "password" in text
    )


def unable_to_check_finding(
    *,
    finding_id: str,
    home_title: str,
    technical_title: str,
    category: Category,
    summary: str,
    result: CommandResult | None = None,
    method: str | None = None,
) -> Finding:
    notes = "The check could not complete. No settings were changed."
    if result and result.timed_out:
        notes = "The read-only command timed out. No settings were changed."
    elif result and result.error:
        notes = f"The read-only command could not run: {result.error}."
    elif result and result.return_code not in {None, 0}:
        notes = "The read-only command returned limited visibility or was unavailable."

    return make_macos_finding(
        finding_id=finding_id,
        title=home_title,
        home_title=home_title,
        technical_title=technical_title,
        status=FindingStatus.UNABLE_TO_CHECK,
        severity=Severity.INFO,
        confidence=Confidence.UNKNOWN,
        category=category,
        summary=summary,
        why_it_matters="This check needs read-only macOS system information that was not available.",
        evidence=[
            Evidence(
                source="macOS local check",
                method=result.command_name if result else method or "platform guard",
                observed_value="unable to check",
                expected_value="read-only macOS information available",
                notes=notes,
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.EDUCATE,
                "Limited visibility handling",
                "Review this area manually in macOS System Settings if it matters for your setup.",
                "AI HomeGuard reports limited visibility instead of requesting administrator access or changing settings.",
                Difficulty.EASY,
                10,
            )
        ],
        recommended_action="Review this setting manually in macOS System Settings if needed.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=10,
        requires_admin=False,
        tags=["unable-to-check"],
    )


def make_macos_finding(
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
        platform=Platform.MACOS,
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
        tags=["macos", *(tags or [])],
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
