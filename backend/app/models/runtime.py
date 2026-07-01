from enum import Enum

from pydantic import BaseModel, Field

from app.models.enums import Platform


class RuntimeEnvironment(str, Enum):
    NATIVE = "native"
    DOCKER = "docker"
    UNKNOWN = "unknown"


class RuntimeContext(BaseModel):
    detected_platform: Platform
    runtime_environment: RuntimeEnvironment
    architecture: str | None = None
    hostname_present: bool
    platform_notes: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
