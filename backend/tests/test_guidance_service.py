from datetime import UTC, datetime

import pytest

from app.knowledge.guidance_service import (
    enrich_finding_guidance,
    enrich_report_guidance,
    get_guidance_by_id,
    get_guidance_for_finding,
)
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
from app.models.guidance import D3FENDGuidance
from app.models.report import HomeGuardReport, ReportSummary


def finding_without_guidance(
    *,
    category: Category = Category.DATA_PROTECTION,
    platform: Platform = Platform.WINDOWS,
    tags: list[str] | None = None,
) -> Finding:
    return Finding(
        id="guidance-test-finding",
        title="Guidance test finding",
        home_title="Guidance test finding",
        status=FindingStatus.REVIEW,
        severity=Severity.LOW,
        confidence=Confidence.MEDIUM,
        platform=platform,
        category=category,
        summary="A test finding.",
        why_it_matters="It verifies deterministic guidance enrichment.",
        evidence=[
            Evidence(
                source="unit test",
                method="model construction",
                observed_value="present",
                expected_value="reviewed",
            )
        ],
        d3fend_guidance=[],
        recommended_action="Review the test finding.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=5,
        user_can_fix=True,
        requires_admin=False,
        tags=tags or [],
    )


def test_guidance_lookup_by_id_works() -> None:
    guidance = get_guidance_by_id("enable_host_firewall")

    assert guidance.guidance_id == "enable_host_firewall"
    assert guidance.defensive_concept == "Host Firewall"
    assert guidance.educational_only is True


def test_missing_guidance_id_raises_clean_key_error() -> None:
    with pytest.raises(KeyError):
        get_guidance_by_id("missing-guidance-id")


def test_finding_without_guidance_can_be_enriched_by_category_platform() -> None:
    finding = finding_without_guidance()

    guidance = get_guidance_for_finding(finding)
    enriched = enrich_finding_guidance(finding)

    assert guidance[0].guidance_id == "enable_full_disk_encryption"
    assert enriched.d3fend_guidance[0].guidance_id == "enable_full_disk_encryption"
    assert finding.d3fend_guidance == []


def test_tagged_finding_attaches_matching_catalog_guidance() -> None:
    finding = finding_without_guidance(
        category=Category.NETWORK_AWARENESS,
        platform=Platform.LINUX,
        tags=["listening-ports"],
    )

    enriched = enrich_finding_guidance(finding)

    assert [guidance.guidance_id for guidance in enriched.d3fend_guidance] == ["review_local_services"]


def test_existing_guidance_is_preserved_and_not_duplicated() -> None:
    existing = get_guidance_by_id("enable_host_firewall")
    finding = finding_without_guidance(
        category=Category.DEVICE_POSTURE,
        platform=Platform.WINDOWS,
        tags=["enable_host_firewall"],
    ).model_copy(update={"d3fend_guidance": [existing]})

    enriched = enrich_finding_guidance(finding)

    assert enriched.d3fend_guidance == [existing]


def test_report_enrichment_adds_guidance_to_findings_lacking_it() -> None:
    finding = finding_without_guidance()
    report = HomeGuardReport(
        report_id="guidance-report",
        app="AI HomeGuard",
        version="0.1.0-dev",
        generated_at=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
        mode=ReportMode.LOCAL,
        platform_scope=[Platform.WINDOWS],
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
        disclaimer="Test report.",
        safety_notes=["No external calls."],
    )

    enriched = enrich_report_guidance(report)

    assert enriched.findings[0].d3fend_guidance[0].guidance_id == "enable_full_disk_encryption"
    assert report.findings[0].d3fend_guidance == []
    assert isinstance(enriched.findings[0].d3fend_guidance[0], D3FENDGuidance)
