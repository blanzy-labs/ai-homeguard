from app.demo.device_inventory import get_demo_device_inventory_submission
from app.models.device_inventory import DeviceType


def test_demo_inventory_returns_deterministic_fake_devices() -> None:
    first = get_demo_device_inventory_submission()
    second = get_demo_device_inventory_submission()

    assert first == second
    assert len(first.devices) == 6
    assert all(device.label.startswith("Demo") or device.label.startswith("Unknown Demo") for device in first.devices)


def test_demo_inventory_has_unknown_and_smart_devices() -> None:
    submission = get_demo_device_inventory_submission()

    assert any(device.device_type == DeviceType.UNKNOWN and not device.recognized for device in submission.devices)
    assert any(device.device_type in {DeviceType.SMART_TV, DeviceType.DOORBELL} for device in submission.devices)


def test_demo_inventory_contains_no_real_ip_mac_or_hostname() -> None:
    submission = get_demo_device_inventory_submission()

    for device in submission.devices:
        assert device.ip_hint is None
        assert device.mac_hint is None
        assert "." not in device.label
        assert ".local" not in device.label.lower()
        assert "host" not in device.label.lower()
