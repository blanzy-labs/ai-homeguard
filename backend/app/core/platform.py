import platform
from enum import Enum
from pathlib import Path

from app.models.enums import Platform
from app.models.runtime import RuntimeContext, RuntimeEnvironment


class LocalPlatform(str, Enum):
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    UNKNOWN = "unknown"


def current_platform() -> LocalPlatform:
    return detect_platform()


def detect_platform() -> LocalPlatform:
    system = platform.system().lower()
    if system == "windows":
        return LocalPlatform.WINDOWS
    if system == "darwin":
        return LocalPlatform.MACOS
    if system == "linux":
        return LocalPlatform.LINUX
    return LocalPlatform.UNKNOWN


def detect_runtime_environment() -> RuntimeEnvironment:
    try:
        if _path_exists("/.dockerenv"):
            return RuntimeEnvironment.DOCKER
        cgroup_text = _read_text("/proc/1/cgroup").lower()
    except OSError:
        return RuntimeEnvironment.UNKNOWN

    if any(hint in cgroup_text for hint in ["docker", "containerd", "kubepods", "podman"]):
        return RuntimeEnvironment.DOCKER
    return RuntimeEnvironment.NATIVE


def get_runtime_context() -> RuntimeContext:
    detected = detect_platform()
    environment = detect_runtime_environment()
    architecture = platform.machine() or None
    hostname_present = bool(platform.node())
    platform_notes = [
        f"Detected platform: {detected.value}",
        f"Runtime environment: {environment.value}",
    ]
    limitations: list[str] = []

    if environment == RuntimeEnvironment.DOCKER:
        limitations.append(
            "AI HomeGuard appears to be running inside a container. Local checks may reflect the "
            "container environment rather than the host computer. For host-level checks, run the "
            "backend natively with uv on the computer you want to audit."
        )
    elif environment == RuntimeEnvironment.UNKNOWN:
        limitations.append("AI HomeGuard could not confidently identify the runtime environment.")

    if detected == LocalPlatform.UNKNOWN:
        limitations.append("AI HomeGuard could not match this runtime to Windows, macOS, or Linux.")

    return RuntimeContext(
        detected_platform=_model_platform(detected),
        runtime_environment=environment,
        architecture=architecture,
        hostname_present=hostname_present,
        platform_notes=platform_notes,
        limitations=limitations,
    )


def _model_platform(local_platform: LocalPlatform) -> Platform:
    if local_platform == LocalPlatform.WINDOWS:
        return Platform.WINDOWS
    if local_platform == LocalPlatform.MACOS:
        return Platform.MACOS
    if local_platform == LocalPlatform.LINUX:
        return Platform.LINUX
    return Platform.UNKNOWN


def _path_exists(path: str) -> bool:
    return Path(path).exists()


def _read_text(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8", errors="ignore")[:20000]
    except FileNotFoundError:
        return ""
