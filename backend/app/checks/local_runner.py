from datetime import UTC, datetime

from app.checks.linux.runner import run_linux_local_audit
from app.checks.macos.runner import run_macos_local_audit
from app.checks.windows.runner import run_windows_local_audit
from app.core.platform import LocalPlatform, get_runtime_context
from app.models.enums import (
    Category,
    Confidence,
    D3FENDGuidanceCategory,
    Difficulty,
    FindingStatus,
    Platform,
    ReportMode,
    Severity,
)
from app.models.evidence import Evidence
from app.models.finding import Finding
from app.models.guidance import D3FENDGuidance
from app.models.report import HomeGuardReport
from app.models.runtime import RuntimeContext, RuntimeEnvironment
from app.knowledge.guidance_service import enrich_report_guidance
from app.reports.merge import summary_from_findings
from app.version import APP_NAME, APP_VERSION

LOCAL_DEVICE_AUDIT_DISCLAIMER = (
    "Unified local device audit results are based on read-only local checks for the detected "
    "runtime platform. AI HomeGuard does not change settings, perform remediation, scan networks, "
    "upload data, or call an AI provider."
)

CONTAINER_LIMITATION_NOTE = (
    "AI HomeGuard appears to be running inside a container. Local checks may reflect the container "
    "environment rather than the host computer. For host-level macOS checks, run the backend "
    "directly on macOS."
)


def run_local_device_audit(
    *,
    runtime_context: RuntimeContext | None = None,
    generated_at: datetime | None = None,
) -> HomeGuardReport:
    context = runtime_context or get_runtime_context()
    report_time = generated_at or datetime.now(UTC)

    if context.detected_platform == Platform.WINDOWS:
        report = run_windows_local_audit(platform_name=LocalPlatform.WINDOWS, generated_at=report_time)
    elif context.detected_platform == Platform.MACOS:
        report = run_macos_local_audit(platform_name=LocalPlatform.MACOS, generated_at=report_time)
    elif context.detected_platform == Platform.LINUX:
        report = run_linux_local_audit(platform_name=LocalPlatform.LINUX, generated_at=report_time)
    else:
        report = _unknown_platform_report(context, report_time)

    safety_notes = _enhanced_safety_notes(report.safety_notes, context)

    return enrich_report_guidance(report.model_copy(
        update={
            "report_id": f"local-device-audit-{report_time.strftime('%Y%m%d%H%M%S')}",
            "summary": summary_from_findings(report.findings),
            "disclaimer": LOCAL_DEVICE_AUDIT_DISCLAIMER,
            "safety_notes": safety_notes,
            "runtime_context": context,
        }
    ))


def _unknown_platform_report(context: RuntimeContext, report_time: datetime) -> HomeGuardReport:
    finding = Finding(
        id="local-device-audit-unknown-platform",
        title="Local device audit could not identify this platform",
        home_title="Local device checks are unavailable here",
        technical_title="Unsupported runtime platform for unified local audit",
        status=FindingStatus.UNABLE_TO_CHECK,
        severity=Severity.INFO,
        confidence=Confidence.HIGH,
        platform=Platform.UNKNOWN,
        category=Category.DEVICE_POSTURE,
        summary=(
            "AI HomeGuard could not match this runtime to Windows, macOS, or Linux, so local device "
            "checks were not executed."
        ),
        why_it_matters="Local device checks need platform-specific read-only system information.",
        evidence=[
            Evidence(
                source="runtime context",
                method="detect_platform",
                observed_value=f"current platform: {context.detected_platform.value}",
                expected_value="windows, macos, or linux",
                notes="No platform-specific local commands were run.",
            )
        ],
        d3fend_guidance=[
            D3FENDGuidance(
                category=D3FENDGuidanceCategory.EDUCATE,
                defensive_concept="Platform-specific validation",
                home_action="Run AI HomeGuard on Windows, macOS, or Linux for local device checks.",
                rationale="Platform guards prevent unsupported local checks from running.",
                difficulty=Difficulty.EASY,
                estimated_time_minutes=5,
            )
        ],
        attack_context=[],
        recommended_action="Run AI HomeGuard on Windows, macOS, or Linux to use local device checks.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=5,
        user_can_fix=True,
        requires_admin=False,
        safe_to_ignore=False,
        tags=["local-device", "unsupported-platform"],
    )

    return enrich_report_guidance(HomeGuardReport(
        report_id=f"local-device-audit-{report_time.strftime('%Y%m%d%H%M%S')}",
        app=APP_NAME,
        version=APP_VERSION,
        generated_at=report_time,
        mode=ReportMode.LOCAL,
        platform_scope=[Platform.UNKNOWN],
        summary=summary_from_findings([finding]),
        findings=[finding],
        disclaimer=LOCAL_DEVICE_AUDIT_DISCLAIMER,
        safety_notes=[],
        runtime_context=context,
    ))


def _enhanced_safety_notes(existing_notes: list[str], context: RuntimeContext) -> list[str]:
    notes = [
        "Read-only local checks only.",
        "No settings were changed.",
        "No remediation was attempted.",
        "No network scan was performed.",
        "No data was uploaded.",
        "No external upload or AI provider call was performed.",
        *existing_notes,
        f"Detected runtime: {context.detected_platform.value} {context.runtime_environment.value}",
    ]
    if context.runtime_environment == RuntimeEnvironment.DOCKER:
        notes.append(CONTAINER_LIMITATION_NOTE)
    notes.extend(context.limitations)
    return _unique(notes)


def _unique(values: list[str]) -> list[str]:
    unique_values: list[str] = []
    for value in values:
        if value not in unique_values:
            unique_values.append(value)
    return unique_values
