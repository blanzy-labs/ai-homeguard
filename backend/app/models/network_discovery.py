from enum import Enum

from pydantic import BaseModel, Field

from app.models.enums import Confidence
from app.models.finding import Finding
from app.models.network import NetworkAuthorizationScope


class DiscoveryMethod(str, Enum):
    PASSIVE_CACHE = "passive_cache"
    PRIVATE_PING = "private_ping"
    COMBINED = "combined"
    UNSUPPORTED = "unsupported"


class DiscoveryRuntimeMode(str, Enum):
    NATIVE_HOST = "native_host"
    DOCKER_LIMITED = "docker_limited"
    UNKNOWN = "unknown"


class DeviceTypeGuess(str, Enum):
    ROUTER = "router"
    COMPUTER = "computer"
    PHONE = "phone"
    TABLET = "tablet"
    PRINTER = "printer"
    SMART_TV = "smart_tv"
    CAMERA = "camera"
    IOT_DEVICE = "iot_device"
    UNKNOWN = "unknown"


class DeviceRecognition(str, Enum):
    YES = "yes"
    NO = "no"
    UNSURE = "unsure"
    NOT_ASKED = "not_asked"


class DiscoveryAuthorization(BaseModel):
    acknowledged: bool = False
    scope: NetworkAuthorizationScope = NetworkAuthorizationScope.NONE
    statement_version: str = "v0.1.0-slice-14"
    include_active_discovery: bool = False
    user_understands_private_network_only: bool = False


class DiscoveredDevice(BaseModel):
    id: str = Field(..., min_length=1)
    ip_hint: str | None = None
    mac_hint: str | None = None
    label: str | None = None
    source_methods: list[DiscoveryMethod] = Field(default_factory=list)
    confidence: Confidence = Confidence.UNKNOWN
    device_type_guess: DeviceTypeGuess = DeviceTypeGuess.UNKNOWN
    recognized: DeviceRecognition = DeviceRecognition.NOT_ASKED
    is_gateway: bool = False
    needs_review: bool = False
    notes: list[str] = Field(default_factory=list)


class NetworkDiscoveryRequest(BaseModel):
    authorization: DiscoveryAuthorization
    method: DiscoveryMethod = DiscoveryMethod.PASSIVE_CACHE
    max_hosts: int = Field(default=64, ge=1, le=256)
    timeout_ms: int = Field(default=500, ge=100, le=2000)
    include_router_gateway: bool = True


class NetworkDiscoveryResult(BaseModel):
    mode: str = "network_discovery"
    method: DiscoveryMethod
    runtime_mode: DiscoveryRuntimeMode
    discovered_count: int = Field(..., ge=0)
    gateway_detected: bool = False
    private_subnet_summary: str | None = None
    devices: list[DiscoveredDevice] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    top_actions: list[str] = Field(default_factory=list)
