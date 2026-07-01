from pathlib import Path

from app.models.device_inventory import DeviceInventoryItem

ROOT = Path(__file__).resolve().parents[1]


def test_device_inventory_code_does_not_run_scanners_or_router_login() -> None:
    files = [
        ROOT / "app" / "inventory" / "analyzer.py",
        ROOT / "app" / "api" / "routes" / "inventory.py",
        ROOT / "app" / "api" / "routes" / "router.py",
        ROOT / "app" / "knowledge" / "router_guidance.py",
        ROOT / "app" / "demo" / "device_inventory.py",
    ]
    source = "\n".join(path.read_text() for path in files).lower()

    for prohibited in [
        "subprocess",
        "safecommandrunner",
        "socket.",
        "nmap(",
        "ping(",
        "tcpdump(",
        "tshark(",
        "router.login",
        "requests.",
        "httpx.",
    ]:
        assert prohibited not in source


def test_device_inventory_model_does_not_require_credentials_or_identifiers() -> None:
    fields = DeviceInventoryItem.model_fields

    for prohibited_field in ["password", "credential", "router_password", "hostname", "serial_number", "owner_name"]:
        assert prohibited_field not in fields
    assert not fields["ip_hint"].is_required()
    assert not fields["mac_hint"].is_required()
    assert not fields["used_by"].is_required()
