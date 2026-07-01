from app.inventory.analyzer import analyze_device_inventory, build_device_inventory_report
from app.models.device_inventory import (
    DeviceInventoryItem,
    DeviceInventoryMode,
    DeviceInventorySubmission,
    DeviceNetworkPlacement,
    DeviceTrustLevel,
    DeviceType,
    DeviceUpdateStatus,
)
from app.models.enums import FindingStatus, Severity


def item(
    item_id: str,
    *,
    device_type: DeviceType = DeviceType.COMPUTER,
    recognized: bool = True,
    trust_level: DeviceTrustLevel = DeviceTrustLevel.TRUSTED,
    placement: DeviceNetworkPlacement = DeviceNetworkPlacement.MAIN_NETWORK,
    update_status: DeviceUpdateStatus = DeviceUpdateStatus.UP_TO_DATE,
    sensitive: bool = False,
) -> DeviceInventoryItem:
    return DeviceInventoryItem(
        id=item_id,
        label=f"Device {item_id}",
        device_type=device_type,
        recognized=recognized,
        trust_level=trust_level,
        network_placement=placement,
        update_status=update_status,
        sensitive=sensitive,
    )


def submission(devices: list[DeviceInventoryItem]) -> DeviceInventorySubmission:
    return DeviceInventorySubmission(
        mode=DeviceInventoryMode.MANUAL,
        acknowledged_manual=True,
        devices=devices,
    )


def finding_ids(result) -> set[str]:
    return {finding.id for finding in result.findings}


def test_unknown_device_creates_review_finding_with_guidance() -> None:
    result = analyze_device_inventory(
        submission([
            item(
                "unknown",
                device_type=DeviceType.UNKNOWN,
                recognized=False,
                trust_level=DeviceTrustLevel.UNKNOWN,
                placement=DeviceNetworkPlacement.UNKNOWN,
                update_status=DeviceUpdateStatus.UNKNOWN,
            )
        ])
    )

    finding = next(finding for finding in result.findings if finding.id == "device-inventory-unknown-devices")
    guidance_ids = {guidance.guidance_id for guidance in finding.d3fend_guidance}
    assert finding.status == FindingStatus.REVIEW
    assert finding.severity != Severity.HIGH
    assert {"identify_assets", "isolate_untrusted_devices"}.issubset(guidance_ids)
    assert "router app/device list" in finding.recommended_action


def test_iot_on_main_network_creates_isolation_guidance() -> None:
    result = analyze_device_inventory(
        submission([
            item(
                "doorbell",
                device_type=DeviceType.DOORBELL,
                trust_level=DeviceTrustLevel.LIMITED_TRUST,
                placement=DeviceNetworkPlacement.MAIN_NETWORK,
                update_status=DeviceUpdateStatus.UNKNOWN,
            )
        ])
    )

    finding = next(finding for finding in result.findings if finding.id == "device-inventory-smart-devices-main-network")
    assert finding.platform.value == "router"
    assert any(guidance.guidance_id == "isolate_untrusted_devices" for guidance in finding.d3fend_guidance)


def test_guest_device_on_main_network_creates_review_finding() -> None:
    result = analyze_device_inventory(
        submission([
            item(
                "guest",
                device_type=DeviceType.GUEST_DEVICE,
                trust_level=DeviceTrustLevel.GUEST,
                placement=DeviceNetworkPlacement.MAIN_NETWORK,
                update_status=DeviceUpdateStatus.UNKNOWN,
            )
        ])
    )

    assert "device-inventory-guest-devices-main-network" in finding_ids(result)
    assert any("guest Wi-Fi" in action for action in result.top_actions)


def test_unsupported_old_device_creates_fix_soon_finding() -> None:
    result = analyze_device_inventory(
        submission([
            item(
                "old-camera",
                device_type=DeviceType.CAMERA,
                trust_level=DeviceTrustLevel.LIMITED_TRUST,
                update_status=DeviceUpdateStatus.UNSUPPORTED_OR_OLD,
            )
        ])
    )

    finding = next(finding for finding in result.findings if finding.id == "device-inventory-unsupported-old-devices")
    assert finding.status == FindingStatus.FIX_SOON
    assert finding.severity == Severity.MEDIUM
    assert any(guidance.guidance_id == "keep_system_updated" for guidance in finding.d3fend_guidance)


def test_many_unknown_update_statuses_create_update_review_finding() -> None:
    result = analyze_device_inventory(
        submission([
            item("tv", device_type=DeviceType.SMART_TV, update_status=DeviceUpdateStatus.UNKNOWN),
            item("printer", device_type=DeviceType.PRINTER, update_status=DeviceUpdateStatus.UNKNOWN),
            item("speaker", device_type=DeviceType.SPEAKER, update_status=DeviceUpdateStatus.UNKNOWN),
        ])
    )

    assert "device-inventory-many-unknown-updates" in finding_ids(result)
    assert any("Review update settings" in action for action in result.top_actions)


def test_sensitive_trusted_devices_are_good_or_review_depending_update_status() -> None:
    up_to_date = analyze_device_inventory(
        submission([item("laptop", sensitive=True, update_status=DeviceUpdateStatus.UP_TO_DATE)])
    )
    needs_review = analyze_device_inventory(
        submission([item("phone", sensitive=True, update_status=DeviceUpdateStatus.NEEDS_REVIEW)])
    )

    up_to_date_finding = next(
        finding for finding in up_to_date.findings if finding.id == "device-inventory-sensitive-trusted-devices"
    )
    needs_review_finding = next(
        finding for finding in needs_review.findings if finding.id == "device-inventory-sensitive-trusted-devices"
    )
    assert up_to_date_finding.status == FindingStatus.GOOD
    assert needs_review_finding.status == FindingStatus.REVIEW


def test_report_contains_enriched_guidance_and_no_high_severity() -> None:
    report = build_device_inventory_report(
        submission([
            item(
                "unknown",
                device_type=DeviceType.UNKNOWN,
                recognized=False,
                trust_level=DeviceTrustLevel.UNKNOWN,
                placement=DeviceNetworkPlacement.UNKNOWN,
                update_status=DeviceUpdateStatus.UNKNOWN,
            )
        ])
    )

    assert report.mode.value == "device_inventory"
    assert all(finding.severity != Severity.HIGH for finding in report.findings)
    assert any(finding.d3fend_guidance for finding in report.findings)
    assert any("No scan is run" in note for note in report.safety_notes)
