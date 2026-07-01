from datetime import UTC, datetime

from app.checks.local_runner import CONTAINER_LIMITATION_NOTE, run_local_device_audit
from app.models.enums import (
    Category,
    Confidence,
    Difficulty,
    FindingStatus,
    Platform,
    ReportMode,
    Severity,
)
from app.models.evidence import Evidence
from app.models.finding import Finding
from app.models.report import HomeGuardReport
from app.models.runtime import RuntimeContext, RuntimeEnvironment
from app.reports.merge import summary_from_findings
from app.version import APP_NAME, APP_VERSION


def runtime_context(
    platform: Platform,
    environment: RuntimeEnvironment = RuntimeEnvironment.NATIVE,
) -> RuntimeContext:
    return RuntimeContext(
        detected_platform=platform,
        runtime_environment=environment,
        architecture="test-arch",
        hostname_present=True,
        platform_notes=[f"Detected platform: {platform.value}", f"Runtime environment: {environment.value}"],
        limitations=[],
    )


def sample_report(platform: Platform, status: FindingStatus = FindingStatus.GOOD) -> HomeGuardReport:
    finding = Finding(
        id=f"{platform.value}-sample-finding",
        title="Sample finding",
        home_title="Sample finding",
        technical_title="Sample technical finding",
        status=status,
        severity=Severity.INFO,
        confidence=Confidence.HIGH,
        platform=platform,
        category=Category.DEVICE_POSTURE,
        summary="Sample summary.",
        why_it_matters="Sample rationale.",
        evidence=[
            Evidence(
                source="mock",
                method="mock",
                observed_value="mocked",
                expected_value="mocked",
                notes="Mocked report for tests.",
            )
        ],
        d3fend_guidance=[],
        attack_context=[],
        recommended_action="Review the sample finding.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=5,
        user_can_fix=True,
        requires_admin=False,
        safe_to_ignore=status == FindingStatus.GOOD,
        tags=["mock"],
    )
    return HomeGuardReport(
        report_id=f"{platform.value}-local-audit-test",
        app=APP_NAME,
        version=APP_VERSION,
        generated_at=datetime(2026, 7, 1, tzinfo=UTC),
        mode=ReportMode.LOCAL,
        platform_scope=[platform],
        summary=summary_from_findings([finding]),
        findings=[finding],
        disclaimer="Mock platform report.",
        safety_notes=["Read-only local checks only."],
    )


def test_unified_runner_calls_windows_runner(monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        "app.checks.local_runner.run_windows_local_audit",
        lambda **kwargs: calls.append("windows") or sample_report(Platform.WINDOWS),
    )
    monkeypatch.setattr(
        "app.checks.local_runner.run_macos_local_audit",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("macOS runner should not run")),
    )
    monkeypatch.setattr(
        "app.checks.local_runner.run_linux_local_audit",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("Linux runner should not run")),
    )

    report = run_local_device_audit(runtime_context=runtime_context(Platform.WINDOWS))

    assert calls == ["windows"]
    assert report.report_id.startswith("local-device-audit-")
    assert report.runtime_context
    assert report.runtime_context.detected_platform == "windows"
    assert report.findings[0].platform == "windows"


def test_unified_runner_calls_macos_runner(monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        "app.checks.local_runner.run_windows_local_audit",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("Windows runner should not run")),
    )
    monkeypatch.setattr(
        "app.checks.local_runner.run_macos_local_audit",
        lambda **kwargs: calls.append("macos") or sample_report(Platform.MACOS),
    )
    monkeypatch.setattr(
        "app.checks.local_runner.run_linux_local_audit",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("Linux runner should not run")),
    )

    report = run_local_device_audit(runtime_context=runtime_context(Platform.MACOS))

    assert calls == ["macos"]
    assert report.findings[0].platform == "macos"


def test_unified_runner_calls_linux_runner(monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        "app.checks.local_runner.run_windows_local_audit",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("Windows runner should not run")),
    )
    monkeypatch.setattr(
        "app.checks.local_runner.run_macos_local_audit",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("macOS runner should not run")),
    )
    monkeypatch.setattr(
        "app.checks.local_runner.run_linux_local_audit",
        lambda **kwargs: calls.append("linux") or sample_report(Platform.LINUX, FindingStatus.REVIEW),
    )

    report = run_local_device_audit(runtime_context=runtime_context(Platform.LINUX))

    assert calls == ["linux"]
    assert report.summary.review_count == 1
    assert report.summary.overall_status == "review"
    assert report.findings[0].platform == "linux"


def test_unknown_platform_returns_unable_to_check_report(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.checks.local_runner.run_windows_local_audit",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("Windows runner should not run")),
    )
    monkeypatch.setattr(
        "app.checks.local_runner.run_macos_local_audit",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("macOS runner should not run")),
    )
    monkeypatch.setattr(
        "app.checks.local_runner.run_linux_local_audit",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("Linux runner should not run")),
    )

    report = run_local_device_audit(runtime_context=runtime_context(Platform.UNKNOWN))

    assert report.mode == "local"
    assert report.findings[0].status == "unable_to_check"
    assert report.summary.unable_to_check_count == 1
    assert "No platform-specific local commands were run" in report.findings[0].evidence[0].notes


def test_docker_runtime_adds_container_limitation(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.checks.local_runner.run_linux_local_audit",
        lambda **kwargs: sample_report(Platform.LINUX),
    )
    context = runtime_context(Platform.LINUX, RuntimeEnvironment.DOCKER)

    report = run_local_device_audit(runtime_context=context)

    assert CONTAINER_LIMITATION_NOTE in report.safety_notes
    assert any("Detected runtime: linux docker" == note for note in report.safety_notes)
    assert report.findings[0].id == "local-device-audit-container-runtime"
    assert report.findings[0].home_title == "Container runtime detected"
    assert "container environment instead of the host computer" in report.findings[0].summary
    assert report.summary.review_count >= 1


def test_unified_runner_safety_notes_include_boundaries(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.checks.local_runner.run_macos_local_audit",
        lambda **kwargs: sample_report(Platform.MACOS),
    )

    report = run_local_device_audit(runtime_context=runtime_context(Platform.MACOS))

    combined = " ".join(report.safety_notes)
    assert "Read-only local checks only." in combined
    assert "No settings were changed." in combined
    assert "No network scan was performed." in combined
    assert "No data was uploaded." in combined
    assert "AI provider" in combined
