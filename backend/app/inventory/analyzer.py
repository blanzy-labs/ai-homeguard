from datetime import UTC, datetime

from app.knowledge.guidance_service import enrich_finding_guidance, enrich_report_guidance
from app.models.device_inventory import (
    DeviceInventoryItem,
    DeviceInventoryMode,
    DeviceInventoryResult,
    DeviceInventorySubmission,
    DeviceNetworkPlacement,
    DeviceTrustLevel,
    DeviceType,
    DeviceUpdateStatus,
)
from app.models.enums import Category, Confidence, Difficulty, FindingStatus, Platform, ReportMode, Severity
from app.models.evidence import Evidence
from app.models.finding import Finding
from app.models.report import HomeGuardReport
from app.reports.merge import summary_from_findings
from app.version import APP_NAME, APP_VERSION

DEVICE_INVENTORY_DISCLAIMER = (
    "Device inventory findings are based on manual or demo device information. AI HomeGuard does "
    "not discover devices, scan the network, send packets, fingerprint devices, log in to routers, "
    "ask for router credentials, upload data, call an AI provider, persist the inventory, or save "
    "this report automatically."
)

SMART_OR_IOT_TYPES = {
    DeviceType.PRINTER,
    DeviceType.SMART_TV,
    DeviceType.CAMERA,
    DeviceType.DOORBELL,
    DeviceType.SPEAKER,
    DeviceType.GAME_CONSOLE,
    DeviceType.IOT_DEVICE,
}


def analyze_device_inventory(submission: DeviceInventorySubmission) -> DeviceInventoryResult:
    devices = submission.devices
    findings = [enrich_finding_guidance(finding) for finding in _build_findings(submission)]

    return DeviceInventoryResult(
        device_count=len(devices),
        recognized_count=sum(1 for device in devices if device.recognized),
        unknown_count=sum(1 for device in devices if _is_unknown_device(device)),
        sensitive_count=sum(1 for device in devices if device.sensitive),
        iot_count=sum(1 for device in devices if device.device_type in SMART_OR_IOT_TYPES),
        guest_or_limited_trust_count=sum(
            1
            for device in devices
            if device.trust_level in {DeviceTrustLevel.GUEST, DeviceTrustLevel.LIMITED_TRUST}
        ),
        findings=findings,
        top_actions=_top_actions(findings),
        limitations=_limitations(submission),
    )


def build_device_inventory_report(
    submission: DeviceInventorySubmission,
    *,
    generated_at: datetime | None = None,
) -> HomeGuardReport:
    report_time = generated_at or datetime.now(UTC)
    result = analyze_device_inventory(submission)
    findings = result.findings
    report = HomeGuardReport(
        report_id=f"device-inventory-report-{report_time.strftime('%Y%m%d%H%M%S')}",
        app=APP_NAME,
        version=APP_VERSION,
        generated_at=report_time,
        mode=ReportMode.DEVICE_INVENTORY,
        platform_scope=_platform_scope(findings),
        summary=summary_from_findings(findings),
        findings=findings,
        disclaimer=DEVICE_INVENTORY_DISCLAIMER,
        safety_notes=_safety_notes(submission),
    )
    return enrich_report_guidance(report)


def _build_findings(submission: DeviceInventorySubmission) -> list[Finding]:
    devices = submission.devices
    findings: list[Finding] = []

    unknown_devices = [device for device in devices if _is_unknown_device(device)]
    if unknown_devices:
        findings.append(_unknown_device_finding(submission, unknown_devices))

    smart_main_devices = [
        device
        for device in devices
        if device.device_type in SMART_OR_IOT_TYPES
        and device.network_placement == DeviceNetworkPlacement.MAIN_NETWORK
    ]
    if smart_main_devices:
        findings.append(_smart_main_network_finding(submission, smart_main_devices))

    guest_main_devices = [
        device
        for device in devices
        if (device.device_type == DeviceType.GUEST_DEVICE or device.trust_level == DeviceTrustLevel.GUEST)
        and device.network_placement == DeviceNetworkPlacement.MAIN_NETWORK
    ]
    if guest_main_devices:
        findings.append(_guest_main_network_finding(submission, guest_main_devices))

    sensitive_devices = [
        device
        for device in devices
        if device.sensitive and device.trust_level == DeviceTrustLevel.TRUSTED
    ]
    if sensitive_devices:
        findings.append(_sensitive_devices_finding(submission, sensitive_devices))

    unsupported_devices = [
        device for device in devices if device.update_status == DeviceUpdateStatus.UNSUPPORTED_OR_OLD
    ]
    if unsupported_devices:
        findings.append(_unsupported_devices_finding(submission, unsupported_devices))

    unknown_update_devices = [
        device for device in devices if device.update_status == DeviceUpdateStatus.UNKNOWN
    ]
    if len(unknown_update_devices) >= 3:
        findings.append(_unknown_updates_finding(submission, unknown_update_devices))

    if not findings:
        findings.append(_inventory_baseline_finding(submission))

    return findings


def _unknown_device_finding(
    submission: DeviceInventorySubmission,
    devices: list[DeviceInventoryItem],
) -> Finding:
    return _inventory_finding(
        finding_id="device-inventory-unknown-devices",
        home_title="Unknown devices need review",
        status=FindingStatus.REVIEW,
        severity=Severity.LOW,
        confidence=Confidence.MEDIUM,
        platform=Platform.NETWORK,
        category=Category.NETWORK_AWARENESS,
        summary="The manual/demo inventory includes devices that are not recognized yet.",
        why_it_matters="Unknown devices in a router list are worth calmly checking before assuming they are unsafe.",
        evidence=[_evidence(submission, f"unknown or unrecognized devices: {len(devices)}", "all devices recognized")],
        recommended_action="Review your router app/device list and identify or remove unknown devices.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=10,
        tags=["device-inventory", "network-awareness", "identify_assets", "isolate_untrusted_devices"],
    )


def _smart_main_network_finding(
    submission: DeviceInventorySubmission,
    devices: list[DeviceInventoryItem],
) -> Finding:
    return _inventory_finding(
        finding_id="device-inventory-smart-devices-main-network",
        home_title="Smart devices are listed on the main network",
        status=FindingStatus.REVIEW,
        severity=Severity.LOW,
        confidence=Confidence.MEDIUM,
        platform=Platform.ROUTER,
        category=Category.NETWORK_AWARENESS,
        summary="Some smart-home or consumer devices are marked as being on the main network.",
        why_it_matters="Guest Wi-Fi or isolation can reduce how much less-trusted devices can reach.",
        evidence=[_evidence(submission, f"smart or IoT devices on main network: {len(devices)}", "guest or isolated network where practical")],
        recommended_action="Consider placing smart devices on guest Wi-Fi or an isolated network if your router supports it.",
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=20,
        tags=["device-inventory", "network-awareness", "smart-devices", "isolate_untrusted_devices"],
    )


def _guest_main_network_finding(
    submission: DeviceInventorySubmission,
    devices: list[DeviceInventoryItem],
) -> Finding:
    return _inventory_finding(
        finding_id="device-inventory-guest-devices-main-network",
        home_title="Guest devices are listed on the main network",
        status=FindingStatus.REVIEW,
        severity=Severity.LOW,
        confidence=Confidence.MEDIUM,
        platform=Platform.ROUTER,
        category=Category.NETWORK_AWARENESS,
        summary="One or more guest devices are marked as using the main network.",
        why_it_matters="Keeping visitor devices on guest Wi-Fi helps separate them from household devices.",
        evidence=[_evidence(submission, f"guest devices on main network: {len(devices)}", "guest devices on guest Wi-Fi where practical")],
        recommended_action="Use guest Wi-Fi for visitors where practical.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=10,
        tags=["device-inventory", "network-awareness", "guest-devices", "isolate_untrusted_devices"],
    )


def _sensitive_devices_finding(
    submission: DeviceInventorySubmission,
    devices: list[DeviceInventoryItem],
) -> Finding:
    needs_review = any(
        device.update_status in {
            DeviceUpdateStatus.NEEDS_REVIEW,
            DeviceUpdateStatus.UNKNOWN,
            DeviceUpdateStatus.UNSUPPORTED_OR_OLD,
        }
        for device in devices
    )
    return _inventory_finding(
        finding_id="device-inventory-sensitive-trusted-devices",
        home_title="Sensitive trusted devices are documented",
        status=FindingStatus.REVIEW if needs_review else FindingStatus.GOOD,
        severity=Severity.INFO,
        confidence=Confidence.MEDIUM,
        platform=Platform.CROSS_PLATFORM,
        category=Category.UPDATES if needs_review else Category.DATA_PROTECTION,
        summary="The inventory marks important household devices such as computers or phones.",
        why_it_matters="Sensitive devices often hold personal files, accounts, or photos and deserve update and encryption review.",
        evidence=[_evidence(submission, f"sensitive trusted devices: {len(devices)}", "important devices identified and kept updated")],
        recommended_action="Review updates and disk encryption on sensitive trusted devices.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=15,
        tags=["device-inventory", "updates", "keep_system_updated", "enable_full_disk_encryption"],
        safe_to_ignore=not needs_review,
    )


def _unsupported_devices_finding(
    submission: DeviceInventorySubmission,
    devices: list[DeviceInventoryItem],
) -> Finding:
    return _inventory_finding(
        finding_id="device-inventory-unsupported-old-devices",
        home_title="Old or unsupported devices need a plan",
        status=FindingStatus.FIX_SOON,
        severity=Severity.MEDIUM,
        confidence=Confidence.MEDIUM,
        platform=Platform.NETWORK,
        category=Category.UPDATES,
        summary="The inventory marks one or more devices as unsupported or old.",
        why_it_matters="Devices that no longer receive updates can become harder to protect over time.",
        evidence=[_evidence(submission, f"unsupported or old devices: {len(devices)}", "devices updated, retired, replaced, or isolated")],
        recommended_action="Retire, update, replace, or isolate devices that no longer receive updates.",
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=30,
        tags=["device-inventory", "updates", "unsupported-devices", "keep_system_updated", "isolate_untrusted_devices"],
    )


def _unknown_updates_finding(
    submission: DeviceInventorySubmission,
    devices: list[DeviceInventoryItem],
) -> Finding:
    return _inventory_finding(
        finding_id="device-inventory-many-unknown-updates",
        home_title="Several device update statuses are unknown",
        status=FindingStatus.REVIEW,
        severity=Severity.LOW,
        confidence=Confidence.LOW,
        platform=Platform.NETWORK,
        category=Category.UPDATES,
        summary="Several devices have unknown update status in the manual/demo inventory.",
        why_it_matters="Smart TVs, cameras, printers, routers, and similar devices often have separate update settings.",
        evidence=[_evidence(submission, f"devices with unknown update status: {len(devices)}", "update status reviewed for connected devices")],
        recommended_action="Check update settings for smart TVs, cameras, printers, routers, and other connected devices.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=20,
        tags=["device-inventory", "updates", "keep_system_updated"],
    )


def _inventory_baseline_finding(submission: DeviceInventorySubmission) -> Finding:
    return _inventory_finding(
        finding_id="device-inventory-manual-baseline",
        home_title="Manual device inventory is ready",
        status=FindingStatus.GOOD,
        severity=Severity.INFO,
        confidence=Confidence.MEDIUM if submission.mode == DeviceInventoryMode.MANUAL else Confidence.HIGH,
        platform=Platform.NETWORK,
        category=Category.NETWORK_AWARENESS,
        summary="The inventory did not surface unknown, guest, isolated-device, or update-review findings.",
        why_it_matters="A simple device list helps you compare what you recognize against your router app.",
        evidence=[_evidence(submission, f"devices reviewed: {len(submission.devices)}", "manual inventory available")],
        recommended_action="Keep this inventory updated when devices are added or removed.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=5,
        tags=["device-inventory", "network-awareness", "identify_assets"],
        safe_to_ignore=True,
    )


def _inventory_finding(
    *,
    finding_id: str,
    home_title: str,
    status: FindingStatus,
    severity: Severity,
    confidence: Confidence,
    platform: Platform,
    category: Category,
    summary: str,
    why_it_matters: str,
    evidence: list[Evidence],
    recommended_action: str,
    difficulty: Difficulty,
    estimated_time_minutes: int,
    tags: list[str],
    safe_to_ignore: bool = False,
) -> Finding:
    return Finding(
        id=finding_id,
        title=f"Device inventory: {home_title}",
        home_title=home_title,
        technical_title=f"Manual/demo device inventory finding for {finding_id}",
        status=status,
        severity=severity,
        confidence=confidence,
        platform=platform,
        category=category,
        summary=summary,
        why_it_matters=why_it_matters,
        evidence=evidence,
        d3fend_guidance=[],
        recommended_action=recommended_action,
        difficulty=difficulty,
        estimated_time_minutes=estimated_time_minutes,
        user_can_fix=True,
        requires_admin=False,
        safe_to_ignore=safe_to_ignore,
        tags=tags,
    )


def _evidence(submission: DeviceInventorySubmission, observed_value: str, expected_value: str) -> Evidence:
    return Evidence(
        source="demo_inventory" if submission.mode == DeviceInventoryMode.DEMO else "manual_inventory",
        method="device_inventory_submission",
        observed_value=observed_value,
        expected_value=expected_value,
        notes=(
            "Device inventory is based on user-provided or demo data only. "
            "No scan, router login, packet capture, or external lookup was performed."
        ),
    )


def _top_actions(findings: list[Finding]) -> list[str]:
    actions: list[str] = []
    finding_ids = {finding.id for finding in findings}
    if "device-inventory-unknown-devices" in finding_ids:
        actions.append("Review your router app/device list and identify or remove unknown devices.")
    if finding_ids.intersection(
        {
            "device-inventory-smart-devices-main-network",
            "device-inventory-guest-devices-main-network",
            "device-inventory-unsupported-old-devices",
        }
    ):
        actions.append("Move guest and smart devices to guest Wi-Fi or an isolated network where practical.")
    if finding_ids.intersection(
        {
            "device-inventory-many-unknown-updates",
            "device-inventory-sensitive-trusted-devices",
            "device-inventory-unsupported-old-devices",
        }
    ):
        actions.append("Review update settings for smart devices and sensitive devices.")
    actions.append("Check your router app/admin page device list and compare it with this manual inventory.")
    if "device-inventory-unknown-devices" in finding_ids:
        actions.append("Change your Wi-Fi password if an unknown device cannot be identified.")
    return _unique(actions)[:5]


def _limitations(submission: DeviceInventorySubmission) -> list[str]:
    limitations = [
        "Device inventory is manual/demo only in this version.",
        "AI HomeGuard does not automatically discover devices.",
        "Router app/admin page device lists remain the source of truth.",
        "Manual inventory can be incomplete or out of date.",
    ]
    if submission.mode == DeviceInventoryMode.MANUAL and not submission.acknowledged_manual:
        limitations.append("Manual inventory acknowledgement was not provided.")
    return limitations


def _safety_notes(submission: DeviceInventorySubmission) -> list[str]:
    return [
        "Device inventory is manual/demo in this version.",
        "No scan is run.",
        "No packets are sent to other devices.",
        "No Nmap command is run.",
        "No ping sweep is run.",
        "No port scan is run.",
        "No device fingerprinting is performed.",
        "No router login is performed.",
        "Do not enter router passwords into AI HomeGuard.",
        "No credentials are collected.",
        "No packet capture is performed.",
        "No public IP scanning is performed.",
        "No external upload is performed.",
        "No AI provider call is performed.",
        "No database or persistence is used.",
        "No report is saved automatically.",
        "No sudo or administrator requirement is introduced.",
        "Full MAC addresses are masked if provided.",
        "Hostnames, personal names, exact rooms, serial numbers, IP addresses, and MAC addresses are not required.",
        "Use your router app/admin page as the source of truth.",
        *_limitations(submission),
    ]


def _platform_scope(findings: list[Finding]) -> list[Platform]:
    platforms: list[Platform] = []
    for finding in findings:
        if finding.platform not in platforms:
            platforms.append(finding.platform)
    return platforms or [Platform.NETWORK]


def _is_unknown_device(device: DeviceInventoryItem) -> bool:
    return (
        not device.recognized
        or device.device_type == DeviceType.UNKNOWN
        or device.trust_level == DeviceTrustLevel.UNKNOWN
    )


def _unique(values: list[str]) -> list[str]:
    unique_values: list[str] = []
    for value in values:
        if value not in unique_values:
            unique_values.append(value)
    return unique_values
