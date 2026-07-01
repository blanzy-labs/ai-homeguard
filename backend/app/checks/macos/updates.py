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


def check_macos_update_visibility(context: MacOSCheckContext) -> Finding:
    result = context.runner.run(
        "macos_update_visibility",
        ["sw_vers"],
        timeout_seconds=8,
        platform_name=context.platform_name,
    )
    if command_unavailable(result):
        return unable_to_check_finding(
            finding_id="macos-update-visibility-unable-to-check",
            home_title="macOS update visibility could not be checked",
            technical_title="sw_vers unavailable for update context",
            category=Category.UPDATES,
            summary="AI HomeGuard could not read macOS version information for update guidance.",
            result=result,
        )
    return update_visibility_finding_from_output(command_text(result))


def update_visibility_finding_from_output(output: str) -> Finding:
    version = _product_version(output)
    observed = f"macOS version visible: {version}" if version else "macOS version visible"

    return make_macos_finding(
        finding_id="macos-update-visibility",
        title="macOS update visibility",
        home_title="Check Software Update regularly",
        technical_title="macOS update posture not asserted from sw_vers",
        status=FindingStatus.REVIEW,
        severity=Severity.INFO,
        confidence=Confidence.MEDIUM,
        category=Category.UPDATES,
        summary="AI HomeGuard can see the macOS version, but does not claim the Mac is fully patched.",
        why_it_matters="macOS security updates close vulnerabilities, but local version visibility alone is not a full patch check.",
        evidence=[
            Evidence(
                source="macOS local check",
                method="sw_vers",
                observed_value=observed,
                expected_value="updates reviewed in macOS Software Update",
                notes=(
                    "Informational read-only version check. AI HomeGuard did not run package updates, "
                    "change settings, or contact Apple update services."
                ),
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.HARDEN,
                "Security update routine",
                "Open Software Update periodically and install trusted macOS security updates.",
                "A regular update routine reduces exposure to known vulnerabilities.",
                Difficulty.EASY,
                15,
            )
        ],
        recommended_action="Open macOS Software Update and confirm updates are current when convenient.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=15,
        tags=["updates", "version"],
    )


def _product_version(output: str) -> str | None:
    for line in output.splitlines():
        if line.startswith("ProductVersion:"):
            return line.split(":", 1)[1].strip()
    return None
