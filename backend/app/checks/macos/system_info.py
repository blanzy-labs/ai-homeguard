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


def check_macos_system_info(context: MacOSCheckContext) -> Finding:
    result = context.runner.run(
        "macos_system_version",
        ["sw_vers"],
        timeout_seconds=8,
        platform_name=context.platform_name,
    )
    if command_unavailable(result):
        return unable_to_check_finding(
            finding_id="macos-system-info-unable-to-check",
            home_title="macOS version could not be checked",
            technical_title="sw_vers unavailable",
            category=Category.DEVICE_POSTURE,
            summary="AI HomeGuard could not read basic macOS version information.",
            result=result,
        )
    return system_info_finding_from_output(command_text(result))


def system_info_finding_from_output(output: str) -> Finding:
    fields = _parse_sw_vers(output)
    version = fields.get("ProductVersion", "unknown")
    build = fields.get("BuildVersion", "unknown")
    name = fields.get("ProductName", "macOS")

    return make_macos_finding(
        finding_id="macos-system-info",
        title="macOS version visibility",
        home_title="macOS version was read",
        technical_title="sw_vers product and build information",
        status=FindingStatus.GOOD,
        severity=Severity.INFO,
        confidence=Confidence.HIGH if version != "unknown" else Confidence.MEDIUM,
        category=Category.DEVICE_POSTURE,
        summary="AI HomeGuard read basic macOS version information for report context.",
        why_it_matters="Knowing the operating system version helps frame update and compatibility guidance.",
        evidence=[
            Evidence(
                source="macOS local check",
                method="sw_vers",
                observed_value=f"{name} {version}; build {build}",
                expected_value="basic macOS version visible",
                notes="Informational read-only version check. It does not prove the Mac is fully patched.",
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.EDUCATE,
                "Asset awareness",
                "Keep a rough note of which macOS version your Mac is running.",
                "Version awareness helps you recognize when updates or support changes apply.",
                Difficulty.EASY,
                5,
            )
        ],
        recommended_action="No immediate action from this informational check.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=5,
        safe_to_ignore=True,
        tags=["system-info", "version"],
    )


def _parse_sw_vers(output: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in output.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields
