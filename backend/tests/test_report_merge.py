from datetime import UTC, datetime

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
from app.models.guidance import AttackContext, D3FENDGuidance
from app.models.report import HomeGuardReport
from app.reports.merge import merge_homeguard_reports, summary_from_findings
from app.version import APP_NAME, APP_VERSION


def make_finding(
    finding_id: str,
    status: FindingStatus,
    source: str,
    action: str,
    platform: Platform = Platform.QUESTIONNAIRE,
) -> Finding:
    return Finding(
        id=finding_id,
        title=f"Finding {finding_id}",
        home_title=f"Finding {finding_id}",
        technical_title=f"Technical {finding_id}",
        status=status,
        severity=Severity.MEDIUM if status == FindingStatus.FIX_SOON else Severity.INFO,
        confidence=Confidence.MEDIUM,
        platform=platform,
        category=Category.DEVICE_POSTURE,
        summary="A calm summary.",
        why_it_matters="This helps keep the home setup understandable.",
        evidence=[
            Evidence(
                source=source,
                method="mock",
                observed_value="mocked",
                expected_value="expected",
                notes="Mocked evidence.",
            )
        ],
        d3fend_guidance=[
            D3FENDGuidance(
                category=D3FENDGuidanceCategory.HARDEN,
                defensive_concept="Mock hardening",
                home_action="Take the mock defensive action.",
                rationale="This verifies guidance survives merging.",
                difficulty=Difficulty.EASY,
                estimated_time_minutes=5,
            )
        ],
        attack_context=[
            AttackContext(
                tactic="Defense Evasion",
                technique_name="Mock educational context",
                explanation="Educational context only.",
                confidence=Confidence.LOW,
                educational_only=True,
            )
        ]
        if status == FindingStatus.REVIEW
        else [],
        recommended_action=action,
        difficulty=Difficulty.EASY,
        estimated_time_minutes=5,
        user_can_fix=True,
        requires_admin=False,
        safe_to_ignore=status == FindingStatus.GOOD,
        tags=[source],
    )


def make_report(report_id: str, findings: list[Finding], notes: list[str]) -> HomeGuardReport:
    return HomeGuardReport(
        report_id=report_id,
        app=APP_NAME,
        version=APP_VERSION,
        generated_at=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
        mode=ReportMode.LOCAL,
        platform_scope=[finding.platform for finding in findings],
        summary=summary_from_findings(findings),
        findings=findings,
        disclaimer=f"Disclaimer for {report_id}.",
        safety_notes=notes,
    )


def test_merge_homeguard_reports_preserves_findings_and_recomputes_summary() -> None:
    questionnaire = make_report(
        "questionnaire-report",
        [make_finding("questionnaire-password-manager-review", FindingStatus.REVIEW, "questionnaire", "Use a password manager.")],
        ["Questionnaire answers are not persisted."],
    )
    local = make_report(
        "local-report",
        [make_finding("macos-firewall-status", FindingStatus.FIX_SOON, "macOS local check", "Review firewall settings.", Platform.MACOS)],
        ["Read-only local checks only."],
    )

    merged = merge_homeguard_reports([questionnaire, local])

    assert merged.mode == "combined"
    assert len(merged.findings) == 2
    assert merged.summary.review_count == 1
    assert merged.summary.fix_soon_count == 1
    assert merged.summary.top_actions[0] == "Review firewall settings."
    assert "Use a password manager." in merged.summary.top_actions
    assert "Questionnaire answers are not persisted." in merged.safety_notes
    assert "Read-only local checks only." in merged.safety_notes
    assert merged.findings[0].d3fend_guidance


def test_merge_deduplicates_same_finding_id_and_source() -> None:
    first = make_finding("duplicate-id", FindingStatus.REVIEW, "questionnaire", "Review the first item.")
    second = make_finding("duplicate-id", FindingStatus.FIX_SOON, "questionnaire", "Review the duplicate item.")
    third = make_finding("duplicate-id", FindingStatus.FIX_SOON, "local_device", "Review local duplicate source.")
    merged = merge_homeguard_reports([make_report("one", [first, second, third], [])])

    assert len(merged.findings) == 2
    assert [finding.recommended_action for finding in merged.findings] == [
        "Review the first item.",
        "Review local duplicate source.",
    ]


def test_top_actions_prioritize_status_order_and_skip_generic_unable() -> None:
    findings = [
        make_finding("review", FindingStatus.REVIEW, "questionnaire", "Review this later."),
        make_finding("unable", FindingStatus.UNABLE_TO_CHECK, "unsupported_platform", "Run AI HomeGuard on Linux."),
        make_finding("fix", FindingStatus.FIX_SOON, "questionnaire", "Fix this soon."),
        make_finding("attention", FindingStatus.NEEDS_ATTENTION, "questionnaire", "Handle this first."),
    ]

    summary = summary_from_findings(findings)

    assert summary.top_actions == ["Handle this first.", "Fix this soon.", "Review this later."]
