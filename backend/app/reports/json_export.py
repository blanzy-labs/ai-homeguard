from typing import Any

from app.models.report import HomeGuardReport


def render_json_export(report: HomeGuardReport) -> dict[str, Any]:
    validated = HomeGuardReport.model_validate(report)
    return validated.model_dump(mode="json")
