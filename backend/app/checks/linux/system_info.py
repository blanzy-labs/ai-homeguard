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


def check_linux_system_info(context: LinuxCheckContext) -> Finding:
    os_release = context.runner.run(
        "linux_os_release",
        ["cat", "/etc/os-release"],
        timeout_seconds=8,
        platform_name=context.platform_name,
    )
    kernel = context.runner.run(
        "linux_uname_kernel",
        ["uname", "-r"],
        timeout_seconds=8,
        platform_name=context.platform_name,
    )
    if command_missing_or_failed(os_release) and command_missing_or_failed(kernel):
        return unable_to_check_finding(
            finding_id="linux-system-info-unable-to-check",
            home_title="Linux system version could not be checked",
            technical_title="/etc/os-release and uname unavailable",
            category=Category.DEVICE_POSTURE,
            summary="AI HomeGuard could not read basic Linux distribution or kernel information.",
            result=kernel,
        )
    return system_info_finding_from_outputs(command_text(os_release), command_text(kernel))


def system_info_finding_from_outputs(os_release: str, kernel: str) -> Finding:
    fields = _parse_os_release(os_release)
    pretty_name = fields.get("PRETTY_NAME") or fields.get("NAME") or "Linux"
    kernel_summary = kernel.splitlines()[0].strip() if kernel.splitlines() else "unknown kernel"

    return make_linux_finding(
        finding_id="linux-system-info",
        title="Linux system version visibility",
        home_title="Linux version information was read",
        technical_title="/etc/os-release and uname -r",
        status=FindingStatus.GOOD,
        severity=Severity.INFO,
        confidence=Confidence.HIGH if pretty_name != "Linux" else Confidence.MEDIUM,
        category=Category.DEVICE_POSTURE,
        summary="AI HomeGuard read basic Linux distribution and kernel information for report context.",
        why_it_matters="Knowing the distribution and kernel version helps frame update and compatibility guidance.",
        evidence=[
            Evidence(
                source="Linux local check",
                method="cat /etc/os-release; uname -r",
                observed_value=f"{pretty_name}; kernel {kernel_summary}",
                expected_value="basic Linux version visible",
                notes="Informational read-only version check. It does not prove the system is fully patched.",
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.EDUCATE,
                "Asset awareness",
                "Keep a rough note of which Linux distribution and kernel your device is running.",
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


def _parse_os_release(output: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in output.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        fields[key.strip()] = value.strip().strip('"')
    return fields
