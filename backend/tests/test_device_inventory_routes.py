from fastapi.testclient import TestClient

from app.main import app


def inventory_payload() -> dict:
    return {
        "mode": "manual",
        "acknowledged_manual": True,
        "devices": [
            {
                "id": "manual-unknown",
                "label": "Unknown device",
                "device_type": "unknown",
                "recognized": False,
                "trust_level": "unknown",
                "network_placement": "unknown",
                "update_status": "unknown",
                "sensitive": False,
            }
        ],
    }


def test_inventory_demo_returns_200() -> None:
    client = TestClient(app)

    response = client.get("/inventory/demo")

    assert response.status_code == 200
    payload = response.json()
    assert payload["submission"]["mode"] == "demo"
    assert payload["result"]["device_count"] == 6
    assert payload["report"]["mode"] == "device_inventory"


def test_inventory_analyze_returns_200() -> None:
    client = TestClient(app)

    response = client.post("/inventory/analyze", json=inventory_payload())

    assert response.status_code == 200
    payload = response.json()
    assert payload["unknown_count"] == 1
    assert payload["findings"][0]["evidence"][0]["source"] == "manual_inventory"


def test_device_inventory_report_returns_homeguard_report() -> None:
    client = TestClient(app)

    response = client.post("/reports/device-inventory", json=inventory_payload())

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "device_inventory"
    assert payload["findings"]
    assert any("No scan is run" in note for note in payload["safety_notes"])


def test_device_inventory_routes_do_not_require_persistence_ai_or_scanning(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    client = TestClient(app)

    response = client.post("/reports/device-inventory", json=inventory_payload())

    assert response.status_code == 200
    serialized = response.text.lower()
    assert "database" in serialized
    assert "no database" in serialized
    assert "no scan is run" in serialized
    assert "router login" in serialized
