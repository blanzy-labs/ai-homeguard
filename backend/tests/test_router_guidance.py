from fastapi.testclient import TestClient

from app.knowledge.router_guidance import get_router_guidance
from app.main import app


def guidance_text() -> str:
    guidance = get_router_guidance()
    return " ".join(
        [
            guidance.source_note,
            *guidance.safety_notes,
            *(topic.title for topic in guidance.topics),
            *(topic.summary for topic in guidance.topics),
            *(step for topic in guidance.topics for step in topic.steps),
        ]
    ).lower()


def test_router_guidance_is_vendor_neutral() -> None:
    guidance = get_router_guidance()

    assert "vendor-neutral" in guidance.source_note
    assert any("router app" in topic.summary.lower() or "router app" in " ".join(topic.steps).lower() for topic in guidance.topics)
    assert not any(vendor in guidance_text() for vendor in ["netgear", "tp-link", "eero", "asus", "xfinity"])


def test_router_guidance_does_not_include_default_passwords_or_credential_requests() -> None:
    text = guidance_text()

    assert "admin/admin" not in text
    assert "password123" not in text
    assert "enter your router password into ai homeguard" not in text
    assert "enter your router credentials" not in text
    assert "submit your router password" not in text


def test_router_guidance_does_not_include_exploit_or_scanning_instructions() -> None:
    text = guidance_text()

    for prohibited in ["nmap", "tcpdump", "tshark", "run a scan", "start a port scan", "capture packets with"]:
        assert prohibited not in text


def test_router_guidance_route_returns_200() -> None:
    client = TestClient(app)

    response = client.get("/router/guidance")

    assert response.status_code == 200
    payload = response.json()
    assert payload["topics"]
    assert "vendor-neutral" in payload["source_note"]
