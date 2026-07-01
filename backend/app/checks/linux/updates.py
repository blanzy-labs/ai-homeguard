from app.checks.linux.base import (
    LinuxCheckContext,
    command_missing_or_failed,
    command_text,
    guidance,
    make_linux_finding,
    unable_to_check_finding,
)
from app.models.enums import Category, Confidence, D3FENDGuidanceCategory, Difficulty, FindingStatus, Severity
from app.models.evidence import Evidence
from app.models.finding import Finding


def check_linux_update_visibility(context: LinuxCheckContext) -> Finding:
    os_release = context.runner.run(
        "linux_update_os_release",
        ["cat", "/etc/os-release"],
        timeout_seconds=8,
        platform_name=context.platform_name,
    )
    kernel = context.runner.run(
        "linux_update_uname_kernel",
        ["uname", "-r"],
        timeout_seconds=8,
        platform_name=context.platform_name,
    )
    if command_missing_or_failed(os_release) and command_missing_or_failed(kernel):
        return unable_to_check_finding(
            finding_id="linux-update-visibility-unable-to-check",
            home_title="Linux update visibility could not be checked",
            technical_title="/etc/os-release and uname unavailable for update context",
            category=Category.UPDATES,
            summary="AI HomeGuard could not read basic Linux version information for update guidance.",
            result=kernel,
        )
    return update_visibility_finding_from_outputs(command_text(os_release), command_text(kernel))


def update_visibility_finding_from_outputs(os_release: str, kernel: str) -> Finding:
    name = _distribution_name(os_release)
    kernel_summary = kernel.splitlines()[0].strip() if kernel.splitlines() else "unknown kernel"
    observed = f"{name}; kernel {kernel_summary}"

    return make_linux_finding(
        finding_id="linux-update-visibility",
        title="Linux update visibility",
        home_title="Check distribution updates regularly",
        technical_title="Linux update posture not asserted from version information",
        status=FindingStatus.REVIEW,
        severity=Severity.INFO,
        confidence=Confidence.MEDIUM,
        category=Category.UPDATES,
        summary="AI HomeGuard can see basic Linux version information, but does not claim the system is fully patched.",
        why_it_matters="Linux security updates close vulnerabilities, but version visibility alone is not a package update check.",
        evidence=[
            Evidence(
                source="Linux local check",
                method="cat /etc/os-release; uname -r",
                observed_value=observed,
                expected_value="updates reviewed in distribution package tools",
                notes=(
                    "Informational read-only version check. AI HomeGuard did not run package updates, "
                    "install packages, change settings, or contact package repositories."
                ),
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.HARDEN,
                "Security update routine",
                "Use your distribution's normal update tool to keep security updates current.",
                "A regular update routine reduces exposure to known vulnerabilities.",
                Difficulty.MEDIUM,
                15,
            )
        ],
        recommended_action="Use your distribution update tool to confirm security updates are current when convenient.",
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=15,
        tags=["updates", "version"],
    )


def _distribution_name(output: str) -> str:
    for line in output.splitlines():
        if line.startswith("PRETTY_NAME="):
            return line.split("=", 1)[1].strip().strip('"')
    return "Linux distribution visible"
