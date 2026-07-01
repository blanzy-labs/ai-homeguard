from dataclasses import dataclass
import os

from app.version import APP_FAMILY, APP_NAME, APP_REPO, APP_VERSION


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", APP_NAME)
    app_repo: str = APP_REPO
    app_version: str = os.getenv("APP_VERSION", APP_VERSION)
    app_family: str = APP_FAMILY
    app_env: str = os.getenv("APP_ENV", "local")
    enable_network_checks: bool = _env_bool("ENABLE_NETWORK_CHECKS", False)
    enable_ai_summary: bool = _env_bool("ENABLE_AI_SUMMARY", False)


def get_settings() -> Settings:
    return Settings()
