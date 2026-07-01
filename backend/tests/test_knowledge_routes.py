from fastapi.testclient import TestClient

from app.main import app


def test_d3fend_guidance_catalog_route_returns_local_catalog() -> None:
    client = TestClient(app)

    response = client.get("/knowledge/d3fend-guidance")

    assert response.status_code == 200
    payload = response.json()
    assert payload["remote_fetch_performed"] is False
    assert payload["guidance"]
    assert "not official certification" in payload["disclaimer"].lower()
    assert any(entry["guidance_id"] == "review_local_services" for entry in payload["guidance"])


def test_d3fend_guidance_entry_route_returns_one_entry() -> None:
    client = TestClient(app)

    response = client.get("/knowledge/d3fend-guidance/review_remote_access")

    assert response.status_code == 200
    assert response.json()["guidance_id"] == "review_remote_access"


def test_d3fend_guidance_entry_route_returns_404_for_missing_id() -> None:
    client = TestClient(app)

    response = client.get("/knowledge/d3fend-guidance/not-real")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
