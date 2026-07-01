from fastapi.testclient import TestClient

from app.main import app


def test_reports_questionnaire_returns_homeguard_report() -> None:
    client = TestClient(app)
    submission = {
        "answers": [
            {"question_id": "has_important_file_backups", "value": "no"},
            {"question_id": "uses_mfa_important_accounts", "value": "no"},
            {"question_id": "uses_password_manager", "value": "no"},
        ]
    }

    response = client.post("/reports/questionnaire", json=submission)

    assert response.status_code == 200
    payload = response.json()
    assert payload["app"] == "AI HomeGuard"
    assert payload["mode"] == "demo"
    assert payload["summary"]["fix_soon_count"] >= 2
    assert payload["findings"]
    assert "questionnaire answers only" in payload["disclaimer"]
    assert any("not written to disk" in note for note in payload["safety_notes"])


def test_no_backup_answer_produces_fix_soon_backup_finding() -> None:
    client = TestClient(app)

    response = client.post(
        "/reports/questionnaire",
        json={"answers": [{"question_id": "has_important_file_backups", "value": "no"}]},
    )

    assert response.status_code == 200
    findings = response.json()["findings"]
    backup_findings = [
        finding for finding in findings if finding["category"] == "backup_recovery"
    ]
    assert backup_findings
    assert backup_findings[0]["status"] == "fix_soon"
    assert backup_findings[0]["platform"] == "questionnaire"
    assert backup_findings[0]["evidence"][0]["source"] == "questionnaire"


def test_no_mfa_answer_produces_identity_finding() -> None:
    client = TestClient(app)

    response = client.post(
        "/reports/questionnaire",
        json={"answers": [{"question_id": "uses_mfa_important_accounts", "value": "no"}]},
    )

    assert response.status_code == 200
    findings = response.json()["findings"]
    identity_findings = [
        finding for finding in findings if finding["category"] == "identity_access"
    ]
    assert identity_findings
    assert identity_findings[0]["status"] == "fix_soon"
    assert identity_findings[0]["confidence"] == "medium"


def test_questionnaire_report_includes_d3fend_guidance() -> None:
    client = TestClient(app)
    submission = {
        "answers": [
            {"question_id": "old_unsupported_devices", "value": "yes"},
            {"question_id": "smart_devices_isolated", "value": "no"},
            {"question_id": "has_smart_devices", "value": "yes"},
        ]
    }

    response = client.post("/reports/questionnaire", json=submission)

    assert response.status_code == 200
    findings = response.json()["findings"]
    assert findings
    assert all(finding["d3fend_guidance"] for finding in findings)
    assert any(
        guidance["category"] == "isolate"
        for finding in findings
        for guidance in finding["d3fend_guidance"]
    )


def test_questionnaire_answers_are_not_returned_or_persisted() -> None:
    client = TestClient(app)
    submission = {
        "answers": [
            {"question_id": "uses_password_manager", "value": "no"},
        ]
    }

    response = client.post("/reports/questionnaire", json=submission)

    assert response.status_code == 200
    payload = response.json()
    assert "answers" not in payload
    assert "no" in payload["findings"][0]["evidence"][0]["observed_value"]
    assert any("not written to disk" in note for note in payload["safety_notes"])
