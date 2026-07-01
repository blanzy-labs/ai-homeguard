from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.models.device_inventory import DeviceInventorySubmission
from app.models.network import NetworkAuthorization
from app.models.questionnaire import QuestionnaireSubmission
from app.models.report import HomeGuardReport


class ExportFormat(str, Enum):
    NONE = "none"
    MARKDOWN = "markdown"
    JSON = "json"


class CombinedReportRequest(BaseModel):
    include_local_device: bool = False
    include_questionnaire: bool = True
    include_network_awareness: bool = False
    include_device_inventory: bool = False
    questionnaire_submission: QuestionnaireSubmission | None = None
    acknowledged_authorization: bool = False
    network_authorization: NetworkAuthorization | None = None
    device_inventory_submission: DeviceInventorySubmission | None = None
    export_format: ExportFormat = ExportFormat.NONE


class CombinedReportResponse(BaseModel):
    report: HomeGuardReport
    export_markdown: str | None = None
    export_json: dict[str, Any] | None = None
    warnings: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
