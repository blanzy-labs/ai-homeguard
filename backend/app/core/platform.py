import platform
from enum import Enum


class LocalPlatform(str, Enum):
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    UNKNOWN = "unknown"


def current_platform() -> LocalPlatform:
    system = platform.system().lower()
    if system == "windows":
        return LocalPlatform.WINDOWS
    if system == "darwin":
        return LocalPlatform.MACOS
    if system == "linux":
        return LocalPlatform.LINUX
    return LocalPlatform.UNKNOWN
