from fastapi.testclient import TestClient

from app.main import app


def test_version() -> None:
    client = TestClient(app)

    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {
        "app": "AI HomeGuard",
        "repo": "ai-homeguard",
        "version": "0.1.0",
        "family": "Blanzy Labs",
    }
