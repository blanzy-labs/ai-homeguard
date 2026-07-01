from typing import Any

from app.checks.windows.base import (
    WindowsCheckContext,
    as_list,
    guidance,
    make_windows_finding,
    parse_json_output,
    powershell_args,
    unable_to_check_finding,
)
from app.models.enums import Category, Confidence, D3FENDGuidanceCategory, Difficulty, FindingStatus, Severity
from app.models.evidence import Evidence
from app.models.finding import Finding


def check_windows_bitlocker(context: WindowsCheckContext) -> Finding:
    result = context.runner.run(
        "windows_bitlocker_status",
        powershell_args("Get-BitLockerVolume | ConvertTo-Json -Depth 3"),
        timeout_seconds=15,
        platform_name=context.platform_name,
    )
    data = parse_json_output(result)
    volumes = [item for item in as_list(data) if isinstance(item, dict)]
    if not volumes and result.return_code != 0:
        fallback = context.runner.run(
            "windows_manage_bde_status",
            ["manage-bde", "-status"],
            timeout_seconds=15,
            platform_name=context.platform_name,
        )
        if fallback.return_code == 0 and fallback.stdout:
            return bitlocker_finding_from_manage_bde(fallback.stdout)
    if not volumes:
        return unable_to_check_finding(
            finding_id="windows-bitlocker-unable-to-check",
            home_title="Device encryption status could not be checked",
            technical_title="BitLocker status unavailable",
            category=Category.DATA_PROTECTION,
            summary="AI HomeGuard could not read BitLocker or device encryption status.",
            result=result,
        )
    return bitlocker_finding_from_volumes(volumes)


def bitlocker_finding_from_volumes(volumes: list[dict[str, Any]]) -> Finding:
    system_volume = _system_volume(volumes)
    protection_status = str(system_volume.get("ProtectionStatus", "")).lower()
    volume_status = str(system_volume.get("VolumeStatus", "")).lower()
    encrypted = protection_status in {"on", "1", "true"} or "fullyencrypted" in volume_status

    return _bitlocker_finding(
        encrypted=encrypted,
        observed=(
            f"Mount point: {system_volume.get('MountPoint', 'system drive')}; "
            f"protection: {system_volume.get('ProtectionStatus', 'unknown')}; "
            f"volume status: {system_volume.get('VolumeStatus', 'unknown')}"
        ),
        method="Get-BitLockerVolume",
    )


def bitlocker_finding_from_manage_bde(output: str) -> Finding:
    lowered = output.lower()
    encrypted = "protection status:    protection on" in lowered or "conversion status:    fully encrypted" in lowered
    return _bitlocker_finding(
        encrypted=encrypted,
        observed="manage-bde status indicates protection on" if encrypted else "manage-bde status does not indicate protection on",
        method="manage-bde -status",
    )


def _system_volume(volumes: list[dict[str, Any]]) -> dict[str, Any]:
    for volume in volumes:
        if str(volume.get("MountPoint", "")).upper().startswith("C:"):
            return volume
    return volumes[0]


def _bitlocker_finding(*, encrypted: bool, observed: str, method: str) -> Finding:
    return make_windows_finding(
        finding_id="windows-bitlocker-status",
        title="Windows device encryption status",
        home_title="Device encryption is on" if encrypted else "Device encryption should be reviewed",
        technical_title="BitLocker or device encryption protection status",
        status=FindingStatus.GOOD if encrypted else FindingStatus.FIX_SOON,
        severity=Severity.INFO if encrypted else Severity.MEDIUM,
        confidence=Confidence.MEDIUM,
        category=Category.DATA_PROTECTION,
        summary=(
            "The system drive appears protected by device encryption."
            if encrypted
            else "The system drive does not appear protected by device encryption."
        ),
        why_it_matters="Device encryption helps protect personal files if a computer is lost, stolen, or repaired.",
        evidence=[
            Evidence(
                source="windows local check",
                method=method,
                observed_value=observed,
                expected_value="system drive encryption protection on",
                notes="Read-only encryption status check. BitLocker was not enabled, disabled, or modified.",
            )
        ],
        d3fend_guidance=[
            guidance(
                D3FENDGuidanceCategory.HARDEN,
                "Data-at-rest protection",
                "Enable full-disk encryption if the device supports it.",
                "Encryption helps keep files private when the device is not in use.",
                Difficulty.MEDIUM,
                30,
            ),
            guidance(
                D3FENDGuidanceCategory.RECOVER,
                "Recovery key management",
                "Store the recovery key safely before relying on encryption.",
                "A saved recovery key helps avoid accidental lockout.",
                Difficulty.EASY,
                10,
            ),
        ],
        recommended_action=(
            "No immediate action from this check."
            if encrypted
            else "Review Windows device encryption or BitLocker settings and save the recovery key before making changes."
        ),
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=30,
        requires_admin=True,
        safe_to_ignore=encrypted,
        tags=["bitlocker", "encryption"],
    )
