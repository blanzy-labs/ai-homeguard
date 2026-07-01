from fastapi.testclient import TestClient

from app.main import app
from app.questionnaire.questions import get_questionnaire_sections


SENSITIVE_TERMS = {
    "password:",
    "wi-fi password",
    "wifi password",
    "username",
    "email address",
    "home address",
    "street address",
    "ip address",
    "mac address",
    "router credential",
    "secret",
}


def test_get_questionnaire_returns_sections_and_questions() -> None:
    client = TestClient(app)

    response = client.get("/questionnaire")

    assert response.status_code == 200
    sections = response.json()
    assert len(sections) == 5
    assert sum(len(section["questions"]) for section in sections) == 18
    assert sections[0]["id"] == "router_wifi"


def test_questionnaire_contains_no_sensitive_prompts() -> None:
    sections = get_questionnaire_sections()
    parts: list[str] = []
    for section in sections:
        parts.extend([section.title, section.description])
        for question in section.questions:
            parts.extend(
                [
                    question.prompt,
                    question.help_text or "",
                    question.home_user_label or "",
                ]
            )
    text = " ".join(parts).lower()

    for term in SENSITIVE_TERMS:
        assert term not in text


def test_questionnaire_demo_answers_are_deterministic() -> None:
    client = TestClient(app)

    first = client.get("/questionnaire/demo-answers")
    second = client.get("/questionnaire/demo-answers")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()
    assert len(first.json()["answers"]) == 18


def test_questionnaire_evaluate_requires_no_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    client = TestClient(app)
    submission = {
        "answers": [
            {"question_id": "router_admin_password_changed", "value": "unsure"},
            {"question_id": "has_important_file_backups", "value": "no"},
        ]
    }

    response = client.post("/questionnaire/evaluate", json=submission)

    assert response.status_code == 200
    payload = response.json()
    assert payload["answered_count"] == 2
    assert payload["skipped_count"] == 0
    assert len(payload["findings"]) == 2
    assert all(finding["d3fend_guidance"] for finding in payload["findings"])


def test_unsure_answers_produce_review_low_confidence_findings() -> None:
    client = TestClient(app)
    submission = {
        "answers": [
            {"question_id": "router_admin_password_changed", "value": "unsure"},
            {"question_id": "knows_connected_devices", "value": "unsure"},
        ]
    }

    response = client.post("/questionnaire/evaluate", json=submission)

    assert response.status_code == 200
    findings = response.json()["findings"]
    assert findings
    assert all(finding["status"] == "review" for finding in findings)
    assert all(finding["confidence"] == "low" for finding in findings)


def test_skipped_answers_do_not_create_findings() -> None:
    client = TestClient(app)
    submission = {
        "answers": [
            {"question_id": "has_important_file_backups", "value": None, "skipped": True}
        ]
    }

    response = client.post("/questionnaire/evaluate", json=submission)

    assert response.status_code == 200
    assert response.json()["answered_count"] == 0
    assert response.json()["skipped_count"] == 1
    assert response.json()["findings"] == []
