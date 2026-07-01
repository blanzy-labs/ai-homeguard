from fastapi import APIRouter

from app.config import get_settings

router = APIRouter(tags=["version"])


@router.get("/version")
def read_version() -> dict[str, str]:
    settings = get_settings()
    return {
        "app": settings.app_name,
        "repo": settings.app_repo,
        "version": settings.app_version,
        "family": settings.app_family,
    }
