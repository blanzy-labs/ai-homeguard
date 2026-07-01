from pydantic import BaseModel, Field

from app.models.enums import Confidence, D3FENDGuidanceCategory, Difficulty


class D3FENDGuidance(BaseModel):
    category: D3FENDGuidanceCategory
    defensive_concept: str = Field(..., min_length=1)
    home_action: str = Field(..., min_length=1)
    technical_action: str | None = None
    rationale: str = Field(..., min_length=1)
    difficulty: Difficulty
    estimated_time_minutes: int | None = Field(default=None, ge=1)


class AttackContext(BaseModel):
    tactic: str | None = None
    technique_id: str | None = None
    technique_name: str | None = None
    explanation: str = Field(..., min_length=1)
    confidence: Confidence
    educational_only: bool = True
