from pathlib import Path

from app.knowledge.d3fend_catalog import (
    CATALOG_DISCLAIMER,
    CATALOG_SOURCE_NOTE,
    D3FEND_GUIDANCE_CATALOG,
)


def test_catalog_entries_are_unique_and_complete() -> None:
    guidance_ids = [entry.guidance_id for entry in D3FEND_GUIDANCE_CATALOG]

    assert len(guidance_ids) == len(set(guidance_ids))
    assert "enable_host_firewall" in guidance_ids
    assert "review_remote_access" in guidance_ids
    assert "backup_important_data" in guidance_ids
    for entry in D3FEND_GUIDANCE_CATALOG:
        assert entry.defensive_concept
        assert entry.home_action
        assert entry.rationale
        assert entry.estimated_time_minutes >= 1
        assert entry.applies_to_categories
        assert entry.applies_to_platforms
        assert entry.educational_only is True


def test_catalog_disclaimer_avoids_overclaiming() -> None:
    text = f"{CATALOG_SOURCE_NOTE} {CATALOG_DISCLAIMER}".lower()

    assert "no live mitre" in text
    assert "not official certification" in text
    assert "not full d3fend coverage" in text
    assert "not a guarantee" in text


def test_knowledge_layer_has_no_remote_fetch_or_ai_provider_code() -> None:
    knowledge_dir = Path(__file__).resolve().parents[1] / "app" / "knowledge"
    source = "\n".join(path.read_text() for path in knowledge_dir.glob("*.py"))

    blocked_terms = [
        "requests.",
        "httpx.",
        "urlopen",
        "urllib.request",
        "mitre.org",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "openai.",
        "gemini",
    ]
    assert not any(term in source for term in blocked_terms)
