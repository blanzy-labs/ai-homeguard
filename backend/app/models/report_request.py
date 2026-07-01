from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.models.questionnaire import QuestionnaireSubmission
from app.models.report import HomeGuardReport


class ExportFormat(str, Enum):
    NONE = "none"
    MARKDOWN = "markdown"
    JSON = "json"


class CombinedReportRequest(BaseModel):
    include_local_device: bool = False
    include_questionnaire: bool = True
    questionnaire_submission: QuestionnaireSubmission | None = None
    acknowledged_authorization: bool = False
    export_format: ExportFormat = ExportFormat.NONE


class CombinedReportResponse(BaseModel):
    report: HomeGuardReport
    export_markdown: str | None = None
    export_json: dict[str, Any] | None = None
    warnings: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
