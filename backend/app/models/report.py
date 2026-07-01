from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import FindingStatus, Platform, ReportMode
from app.models.finding import Finding


class ReportSummary(BaseModel):
    overall_status: FindingStatus
    overall_score: int | None = Field(default=None, ge=0, le=100)
    good_count: int = Field(..., ge=0)
    review_count: int = Field(..., ge=0)
    fix_soon_count: int = Field(..., ge=0)
    needs_attention_count: int = Field(..., ge=0)
    unable_to_check_count: int = Field(..., ge=0)
    top_actions: list[str] = Field(default_factory=list)


class HomeGuardReport(BaseModel):
    report_id: str = Field(..., min_length=1)
    app: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    generated_at: datetime
    mode: ReportMode
    platform_scope: list[Platform] = Field(default_factory=list)
    summary: ReportSummary
    findings: list[Finding] = Field(default_factory=list)
    disclaimer: str = Field(..., min_length=1)
    safety_notes: list[str] = Field(default_factory=list)
