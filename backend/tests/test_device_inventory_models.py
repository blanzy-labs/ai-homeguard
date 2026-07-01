from app.models.device_inventory import (
    DeviceInventoryItem,
    DeviceNetworkPlacement,
    DeviceTrustLevel,
    DeviceType,
    DeviceUpdateStatus,
)


def test_device_inventory_item_validates_without_ip_mac_or_personal_fields() -> None:
    item = DeviceInventoryItem(
        id="laptop-1",
        label="Main laptop",
        device_type=DeviceType.COMPUTER,
        recognized=True,
        trust_level=DeviceTrustLevel.TRUSTED,
        network_placement=DeviceNetworkPlacement.MAIN_NETWORK,
        update_status=DeviceUpdateStatus.UP_TO_DATE,
        sensitive=True,
    )

    assert item.ip_hint is None
    assert item.mac_hint is None
    assert item.used_by is None
    assert item.sensitive is True


def test_mac_hint_is_masked_if_provided() -> None:
    item = DeviceInventoryItem(
        id="tv-1",
        label="Smart TV",
        device_type=DeviceType.SMART_TV,
        recognized=True,
        trust_level=DeviceTrustLevel.LIMITED_TRUST,
        network_placement=DeviceNetworkPlacement.MAIN_NETWORK,
        update_status=DeviceUpdateStatus.UNKNOWN,
        mac_hint="aa:bb:cc:11:22:33",
    )

    assert item.mac_hint == "aa:bb:cc:xx:xx:xx"
    assert "11:22:33" not in item.mac_hint


def test_ip_hint_is_privacy_masked_if_provided() -> None:
    item = DeviceInventoryItem(
        id="printer-1",
        label="Printer",
        device_type=DeviceType.PRINTER,
        recognized=True,
        trust_level=DeviceTrustLevel.LIMITED_TRUST,
        network_placement=DeviceNetworkPlacement.MAIN_NETWORK,
        update_status=DeviceUpdateStatus.NEEDS_REVIEW,
        ip_hint="192.168.1.44",
    )

    assert item.ip_hint == "192.168.1.x"
    assert "44" not in item.ip_hint
