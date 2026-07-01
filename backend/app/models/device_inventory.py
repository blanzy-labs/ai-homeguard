from enum import Enum
import ipaddress
import re

from pydantic import BaseModel, Field, field_validator

from app.models.finding import Finding


class DeviceType(str, Enum):
    COMPUTER = "computer"
    PHONE = "phone"
    TABLET = "tablet"
    ROUTER = "router"
    PRINTER = "printer"
    SMART_TV = "smart_tv"
    CAMERA = "camera"
    DOORBELL = "doorbell"
    SPEAKER = "speaker"
    GAME_CONSOLE = "game_console"
    NAS_STORAGE = "nas_storage"
    IOT_DEVICE = "iot_device"
    GUEST_DEVICE = "guest_device"
    UNKNOWN = "unknown"
    OTHER = "other"


class DeviceTrustLevel(str, Enum):
    TRUSTED = "trusted"
    LIMITED_TRUST = "limited_trust"
    GUEST = "guest"
    UNKNOWN = "unknown"


class DeviceUpdateStatus(str, Enum):
    UP_TO_DATE = "up_to_date"
    NEEDS_REVIEW = "needs_review"
    UNSUPPORTED_OR_OLD = "unsupported_or_old"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"


class DeviceNetworkPlacement(str, Enum):
    MAIN_NETWORK = "main_network"
    GUEST_NETWORK = "guest_network"
    ISOLATED_NETWORK = "isolated_network"
    WIRED = "wired"
    UNKNOWN = "unknown"


class DeviceInventoryMode(str, Enum):
    DEMO = "demo"
    MANUAL = "manual"


MAC_PATTERN = re.compile(r"\b(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}\b")


class DeviceInventoryItem(BaseModel):
    id: str = Field(..., min_length=1, max_length=80)
    label: str = Field(..., min_length=1, max_length=120)
    device_type: DeviceType
    recognized: bool
    trust_level: DeviceTrustLevel
    network_placement: DeviceNetworkPlacement
    update_status: DeviceUpdateStatus
    used_by: str | None = Field(default=None, max_length=40)
    notes: str | None = Field(default=None, max_length=240)
    ip_hint: str | None = Field(default=None, max_length=80)
    mac_hint: str | None = Field(default=None, max_length=80)
    last_seen_hint: str | None = Field(default=None, max_length=80)
    sensitive: bool = False

    @field_validator("id", "label", "used_by", "notes", "ip_hint", "mac_hint", "last_seen_hint")
    @classmethod
    def _strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("mac_hint")
    @classmethod
    def _mask_mac_hint(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return mask_mac_hint(value)

    @field_validator("ip_hint")
    @classmethod
    def _mask_ip_hint(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return mask_ip_hint(value)


class DeviceInventorySubmission(BaseModel):
    mode: DeviceInventoryMode
    devices: list[DeviceInventoryItem] = Field(default_factory=list)
    user_notes: str | None = Field(default=None, max_length=500)
    acknowledged_manual: bool = False

    @field_validator("user_notes")
    @classmethod
    def _strip_user_notes(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class DeviceInventoryResult(BaseModel):
    device_count: int = Field(..., ge=0)
    recognized_count: int = Field(..., ge=0)
    unknown_count: int = Field(..., ge=0)
    sensitive_count: int = Field(..., ge=0)
    iot_count: int = Field(..., ge=0)
    guest_or_limited_trust_count: int = Field(..., ge=0)
    findings: list[Finding] = Field(default_factory=list)
    top_actions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


def mask_mac_hint(value: str) -> str:
    def replacement(match: re.Match[str]) -> str:
        normalized = match.group(0).replace("-", ":").lower()
        parts = normalized.split(":")
        return ":".join([*parts[:3], "xx", "xx", "xx"])

    masked = MAC_PATTERN.sub(replacement, value.strip())
    if masked != value.strip():
        return masked
    if value.strip():
        return "MAC hint provided"
    return ""


def mask_ip_hint(value: str) -> str:
    stripped = value.strip()
    try:
        address = ipaddress.ip_address(stripped)
    except ValueError:
        return stripped
    if address.version == 4:
        octets = str(address).split(".")
        return f"{octets[0]}.{octets[1]}.{octets[2]}.x"
    return "IPv6 address hint provided"
