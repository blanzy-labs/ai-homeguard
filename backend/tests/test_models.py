from datetime import UTC, datetime

from app.models import (
    Category,
    Confidence,
    D3FENDGuidance,
    D3FENDGuidanceCategory,
    Difficulty,
    Evidence,
    Finding,
    FindingStatus,
    HomeGuardReport,
    Platform,
    ReportMode,
    ReportSummary,
    Severity,
)


def test_homeguard_report_serializes_to_json_values() -> None:
    finding = Finding(
        id="test-finding",
        title="Test finding",
        home_title="A friendly test finding",
        status=FindingStatus.REVIEW,
        severity=Severity.LOW,
        confidence=Confidence.HIGH,
        platform=Platform.CROSS_PLATFORM,
        category=Category.SAFETY,
        summary="A test summary.",
        why_it_matters="A test reason.",
        evidence=[
            Evidence(
                source="unit test",
                method="model construction",
                observed_value="observed",
                expected_value="expected",
            )
        ],
        d3fend_guidance=[
            D3FENDGuidance(
                category=D3FENDGuidanceCategory.EDUCATE,
                defensive_concept="Safe model use",
                home_action="Read the friendly explanation.",
                rationale="This checks nested model serialization.",
                difficulty=Difficulty.EASY,
                estimated_time_minutes=5,
            )
        ],
        recommended_action="Review the test output.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=5,
        user_can_fix=True,
        requires_admin=False,
        tags=["test"],
    )
    report = HomeGuardReport(
        report_id="test-report",
        app="AI HomeGuard",
        version="0.1.0-dev",
        generated_at=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
        mode=ReportMode.DEMO,
        platform_scope=[Platform.CROSS_PLATFORM],
        summary=ReportSummary(
            overall_status=FindingStatus.REVIEW,
            overall_score=80,
            good_count=0,
            review_count=1,
            fix_soon_count=0,
            needs_attention_count=0,
            unable_to_check_count=0,
            top_actions=["Review the test finding."],
        ),
        findings=[finding],
        disclaimer="Test disclaimer.",
        safety_notes=["Test safety note."],
    )

    payload = report.model_dump(mode="json")

    assert payload["mode"] == "demo"
    assert payload["summary"]["overall_status"] == "review"
    assert payload["findings"][0]["platform"] == "cross_platform"
    assert payload["findings"][0]["d3fend_guidance"][0]["category"] == "educate"
    assert payload["findings"][0]["safe_to_ignore"] is False
