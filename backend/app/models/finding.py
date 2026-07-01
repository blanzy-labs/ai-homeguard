from pydantic import BaseModel, Field

from app.models.enums import Category, Confidence, Difficulty, FindingStatus, Platform, Severity
from app.models.evidence import Evidence
from app.models.guidance import AttackContext, D3FENDGuidance


class Finding(BaseModel):
    id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    home_title: str = Field(..., min_length=1)
    technical_title: str | None = None
    status: FindingStatus
    severity: Severity
    confidence: Confidence
    platform: Platform
    category: Category
    summary: str = Field(..., min_length=1)
    why_it_matters: str = Field(..., min_length=1)
    evidence: list[Evidence] = Field(default_factory=list)
    d3fend_guidance: list[D3FENDGuidance] = Field(default_factory=list)
    attack_context: list[AttackContext] = Field(default_factory=list)
    recommended_action: str = Field(..., min_length=1)
    difficulty: Difficulty
    estimated_time_minutes: int | None = Field(default=None, ge=1)
    user_can_fix: bool
    requires_admin: bool
    safe_to_ignore: bool = False
    docs_url: str | None = None
    tags: list[str] = Field(default_factory=list)
