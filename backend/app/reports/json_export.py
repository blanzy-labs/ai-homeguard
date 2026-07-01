from typing import Any

from app.knowledge.guidance_service import enrich_report_guidance
from app.models.report import HomeGuardReport


def render_json_export(report: HomeGuardReport) -> dict[str, Any]:
    validated = HomeGuardReport.model_validate(enrich_report_guidance(report))
    return validated.model_dump(mode="json")
