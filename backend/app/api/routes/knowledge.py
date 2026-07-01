from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.knowledge.d3fend_catalog import (
    CATALOG_DISCLAIMER,
    CATALOG_SOURCE_NOTE,
    CATALOG_VERSION,
    D3FENDCatalogEntry,
    D3FEND_GUIDANCE_CATALOG,
)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class D3FENDGuidanceCatalogResponse(BaseModel):
    version: str
    source_note: str
    disclaimer: str
    remote_fetch_performed: bool = False
    guidance: list[D3FENDCatalogEntry]


@router.get("/d3fend-guidance", response_model=D3FENDGuidanceCatalogResponse)
def read_d3fend_guidance_catalog() -> D3FENDGuidanceCatalogResponse:
    return D3FENDGuidanceCatalogResponse(
        version=CATALOG_VERSION,
        source_note=CATALOG_SOURCE_NOTE,
        disclaimer=CATALOG_DISCLAIMER,
        remote_fetch_performed=False,
        guidance=list(D3FEND_GUIDANCE_CATALOG),
    )


@router.get("/d3fend-guidance/{guidance_id}", response_model=D3FENDCatalogEntry)
def read_d3fend_guidance_entry(guidance_id: str) -> D3FENDCatalogEntry:
    for entry in D3FEND_GUIDANCE_CATALOG:
        if entry.guidance_id == guidance_id:
            return entry
    raise HTTPException(status_code=404, detail="D3FEND-informed guidance entry not found.")
