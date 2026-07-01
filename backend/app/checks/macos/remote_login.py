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
from app.models.guidance import AttackContext


def check_macos_remote_login(context: MacOSCheckContext) -> Finding:
    result = context.runner.run(
        "macos_remote_login_status",
        ["systemsetup", "-getremotelogin"],
        timeout_seconds=10,
        platform_name=context.platform_name,
    )
    if command_unavailable(result):
        return unable_to_check_finding(
            finding_id="macos-remote-login-unable-to-check",
            home_title="Remote Login status could not be checked",
            technical_title="systemsetup Remote Login unavailable",
            category=Category.IDENTITY_ACCESS,
            summary="AI HomeGuard could not read macOS Remote Login status.",
            result=result,
        )
    return remote_login_finding_from_output(command_text(result))


def remote_login_finding_from_output(output: str) -> Finding:
    normalized = output.lower()
    enabled = "remote login: on" in normalized or normalized.strip() == "on"
    disabled = "remote login: off" in normalized or normalized.strip() == "off"
    if not enabled and not disabled:
        return unable_to_check_finding(
            finding_id="macos-remote-login-unclear",
            home_title="Remote Login status was unclear",
            technical_title="systemsetup output unclear",
            category=Category.IDENTITY_ACCESS,
            summary="AI HomeGuard read Remote Login command output, but could not interpret it.",
        )

    return make_macos_finding(
        finding_id="macos-remote-login-status",
        title="macOS Remote Login status",
        home_title="Remote Login is off" if disabled else "Remote Login is on",
        technical_title="systemsetup Remote Login status",
        status=FindingStatus.GOOD if disabled else FindingStatus.REVIEW,
        severity=Severity.INFO if disabled else Severity.LOW,
        confidence=Confidence.HIGH,
        category=Category.IDENTITY_ACCESS,
        summary=(
            "macOS Remote Login appears disabled."
            if disabled
            else "macOS Remote Login appears enabled and should be expected for this Mac."
        ),
        why_it_matters="Remote Login enables SSH access. It can be legitimate, but should be intentional.",
        evidence=[
            Evidence(
                source="macOS local check",
                method="systemsetup -getremotelogin",
                observed_value="Remote Login off" if disabled else "Remote Login on",
                expected_value="Remote Login off unless needed",
                notes="Read-only sharing status check. No sharing or SSH settings were changed.",
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.HARDEN,
                "Remote access review",
                "Keep Remote Login off unless you actively use SSH and understand who can connect.",
                "Reducing remote access services lowers the chance of unwanted sign-in attempts.",
                Difficulty.EASY,
                10,
            )
        ],
        attack_context=[
            AttackContext(
                tactic="Initial Access",
                technique_id=None,
                technique_name="Remote service exposure",
                explanation="This context is educational only: remote login services can increase exposure if enabled unintentionally.",
                confidence=Confidence.MEDIUM,
                educational_only=True,
            )
        ]
        if enabled
        else [],
        recommended_action=(
            "No immediate action from this check."
            if disabled
            else "Confirm Remote Login is expected and limited to trusted users."
        ),
        difficulty=Difficulty.EASY,
        estimated_time_minutes=10,
        safe_to_ignore=disabled,
        tags=["remote-login", "ssh", "identity-access"],
    )
