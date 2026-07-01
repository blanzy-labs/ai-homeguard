from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from app.models.enums import Platform, ReportMode
from app.models.finding import Finding
from app.models.runtime import RuntimeEnvironment


class NetworkAuthorizationScope(str, Enum):
    NONE = "none"
    HOME_NETWORK = "home_network"
    DEVICE_ONLY = "device_only"
    DEMO = "demo"


class NetworkScopeType(str, Enum):
    NONE = "none"
    PRIVATE_LOCAL = "private_local"
    PUBLIC_OR_UNKNOWN = "public_or_unknown"
    DOCKER_OR_CONTAINER_LIMITED = "docker_or_container_limited"
    UNSUPPORTED = "unsupported"


class NetworkAuthorization(BaseModel):
    acknowledged: bool = False
    scope: NetworkAuthorizationScope = NetworkAuthorizationScope.NONE
    statement_version: str = "v0.1.0-network-awareness"
    timestamp: datetime | None = None
    notes: str | None = None


class NetworkScope(BaseModel):
    scope_type: NetworkScopeType = NetworkScopeType.NONE
    detected_platform: Platform | None = None
    runtime_environment: RuntimeEnvironment | None = None
    local_interface_count: int | None = Field(default=None, ge=0)
    private_network_count: int | None = Field(default=None, ge=0)
    gateway_detected: bool = False
    gateway_private: bool = False
    limitations: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)


class NetworkAwarenessReport(BaseModel):
    mode: ReportMode = ReportMode.NETWORK_AWARENESS
    authorization: NetworkAuthorization
    scope: NetworkScope
    findings: list[Finding] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    disclaimer: str
    generated_at: datetime


class NetworkContext(BaseModel):
    runtime_platform: Platform
    runtime_environment: RuntimeEnvironment
    possible_private_ranges: list[str] = Field(default_factory=list)
    gateway_present: bool = False
    gateway_private: bool = False
    passive_neighbor_count: int | None = Field(default=None, ge=0)
    passive_neighbor_summary: str | None = None
    local_interface_count: int | None = Field(default=None, ge=0)
    limitations: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)


class NetworkScopeValidation(BaseModel):
    allowed: bool
    classifications: dict[str, str] = Field(default_factory=dict)
    rejected_targets: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
