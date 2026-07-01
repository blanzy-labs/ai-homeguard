from app.checks.linux.base import (
    LinuxCheckContext,
    command_text,
    guidance,
    make_linux_finding,
    unable_to_check_finding,
)
from app.core.command_runner import CommandResult
from app.models.enums import Category, Confidence, D3FENDGuidanceCategory, Difficulty, FindingStatus, Severity
from app.models.evidence import Evidence
from app.models.finding import Finding
from app.models.guidance import AttackContext


def check_linux_ssh(context: LinuxCheckContext) -> Finding:
    results = [
        context.runner.run(
            "linux_ssh_systemctl_ssh",
            ["systemctl", "is-active", "ssh"],
            timeout_seconds=10,
            platform_name=context.platform_name,
        ),
        context.runner.run(
            "linux_ssh_systemctl_sshd",
            ["systemctl", "is-active", "sshd"],
            timeout_seconds=10,
            platform_name=context.platform_name,
        ),
        context.runner.run(
            "linux_ssh_service",
            ["service", "ssh", "status"],
            timeout_seconds=10,
            platform_name=context.platform_name,
        ),
    ]
    finding = ssh_finding_from_results(results)
    if finding is None:
        return unable_to_check_finding(
            finding_id="linux-ssh-unable-to-check",
            home_title="SSH service status could not be checked",
            technical_title="ssh/sshd service status unavailable",
            category=Category.IDENTITY_ACCESS,
            summary="AI HomeGuard could not read Linux SSH service status from common tools.",
            result=results[-1],
        )
    return finding


def ssh_finding_from_results(results: list[CommandResult]) -> Finding | None:
    states = [_ssh_signal(result) for result in results]
    usable_states = [state for state in states if state != "unavailable"]
    if not usable_states:
        return None

    active = "active" in usable_states
    evidence_summary = "; ".join(
        f"{result.command_name.replace('linux_ssh_', '')}: {state}"
        for result, state in zip(results, states, strict=False)
    )

    return make_linux_finding(
        finding_id="linux-ssh-service-status",
        title="Linux SSH service status",
        home_title="SSH service is inactive" if not active else "SSH service is active",
        technical_title="ssh/sshd service activity status",
        status=FindingStatus.REVIEW if active else FindingStatus.GOOD,
        severity=Severity.LOW if active else Severity.INFO,
        confidence=Confidence.MEDIUM,
        category=Category.IDENTITY_ACCESS,
        summary=(
            "A common SSH service appears active and should be expected for this Linux device."
            if active
            else "Common SSH service checks did not show an active SSH service."
        ),
        why_it_matters="SSH enables remote shell access. It can be legitimate, but should be intentional.",
        evidence=[
            Evidence(
                source="Linux local check",
                method="systemctl is-active ssh/sshd; service ssh status",
                observed_value=evidence_summary,
                expected_value="SSH inactive unless needed",
                notes="Read-only service status checks. No SSH settings or service states were changed.",
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.HARDEN,
                "Remote access review",
                "Keep SSH disabled unless you actively use it and understand who can connect.",
                "Reducing remote access services lowers the chance of unwanted sign-in attempts.",
                Difficulty.MEDIUM,
                15,
            )
        ],
        attack_context=[
            AttackContext(
                tactic="Initial Access",
                technique_id=None,
                technique_name="Remote service exposure",
                explanation="This context is educational only: remote access services can increase exposure if enabled unintentionally.",
                confidence=Confidence.MEDIUM,
                educational_only=True,
            )
        ]
        if active
        else [],
        recommended_action=(
            "Confirm SSH is expected and limited to trusted users."
            if active
            else "No immediate action from this check."
        ),
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=15,
        safe_to_ignore=not active,
        tags=["ssh", "remote-access", "identity-access"],
    )


def _ssh_signal(result: CommandResult) -> str:
    text = command_text(result).lower()
    if not result.supported or result.error or result.timed_out:
        return "unavailable"
    if result.command_name in {"linux_ssh_systemctl_ssh", "linux_ssh_systemctl_sshd"}:
        if text.strip().splitlines()[:1] == ["active"]:
            return "active"
        if any(value in text for value in ["inactive", "failed", "unknown"]):
            return "inactive"
    if result.command_name == "linux_ssh_service":
        if any(value in text for value in ["running", "start/running", "active"]):
            return "active"
        if any(value in text for value in ["not running", "inactive", "stopped"]):
            return "inactive"
    return "unavailable"
