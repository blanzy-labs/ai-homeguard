from fastapi.testclient import TestClient

from app.main import app


def test_frontend_origin_can_preflight_post_requests() -> None:
    client = TestClient(app)

    response = client.options(
        "/reports/combined",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "POST" in response.headers["access-control-allow-methods"]
