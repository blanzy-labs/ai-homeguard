from fastapi import APIRouter

from app.knowledge.router_guidance import RouterGuidanceResponse, get_router_guidance

router = APIRouter(prefix="/router", tags=["router guidance"])


@router.get("/guidance", response_model=RouterGuidanceResponse)
def read_router_guidance() -> RouterGuidanceResponse:
    return get_router_guidance()
