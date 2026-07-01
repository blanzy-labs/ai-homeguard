from fastapi import APIRouter, HTTPException, Response

from app.checks.local_runner import run_local_device_audit
from app.demo.demo_report import get_demo_report
from app.inventory.analyzer import build_device_inventory_report
from app.models.device_inventory import DeviceInventorySubmission
from app.models.questionnaire import QuestionnaireSubmission
from app.models.report import HomeGuardReport
from app.models.report_request import CombinedReportRequest, CombinedReportResponse, ExportFormat
from app.network.runner import NETWORK_AUTHORIZATION_ERROR, NETWORK_SCOPE_ERROR, run_network_awareness
from app.questionnaire.report_builder import build_questionnaire_report
from app.reports.json_export import render_json_export
from app.reports.markdown import render_markdown_report
from app.reports.merge import merge_homeguard_reports

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/demo", response_model=HomeGuardReport)
def read_demo_report_alias() -> HomeGuardReport:
    return get_demo_report()


@router.post("/questionnaire", response_model=HomeGuardReport)
def read_questionnaire_report(submission: QuestionnaireSubmission) -> HomeGuardReport:
    return build_questionnaire_report(submission)


@router.post("/device-inventory", response_model=HomeGuardReport)
def read_device_inventory_report(submission: DeviceInventorySubmission) -> HomeGuardReport:
    return build_device_inventory_report(submission)


@router.post("/combined", response_model=CombinedReportResponse)
def read_combined_report(request: CombinedReportRequest) -> CombinedReportResponse:
    if request.include_local_device and not request.acknowledged_authorization:
        raise HTTPException(
            status_code=400,
            detail="Local device audit requires authorization acknowledgement.",
        )
    if request.include_network_awareness and (
        request.network_authorization is None or not request.network_authorization.acknowledged
    ):
        raise HTTPException(
            status_code=400,
            detail="Network awareness requires authorization acknowledgement.",
        )
    if request.include_questionnaire and request.questionnaire_submission is None:
        raise HTTPException(
            status_code=400,
            detail="Questionnaire submission is required when include_questionnaire is true.",
        )
    if request.include_device_inventory and request.device_inventory_submission is None:
        raise HTTPException(
            status_code=400,
            detail="Device inventory submission is required when include_device_inventory is true.",
        )
    if (
        not request.include_questionnaire
        and not request.include_local_device
        and not request.include_network_awareness
        and not request.include_device_inventory
    ):
        raise HTTPException(status_code=400, detail="Select at least one report source.")

    reports: list[HomeGuardReport] = []
    warnings: list[str] = []
    limitations: list[str] = []

    if request.include_questionnaire and request.questionnaire_submission is not None:
        reports.append(build_questionnaire_report(request.questionnaire_submission))
    if request.include_local_device:
        local_report = run_local_device_audit()
        reports.append(local_report)
        if local_report.runtime_context:
            limitations.extend(local_report.runtime_context.limitations)
    if request.include_network_awareness and request.network_authorization is not None:
        try:
            network_report = run_network_awareness(request.network_authorization)
        except ValueError as error:
            detail = str(error)
            if detail not in {NETWORK_AUTHORIZATION_ERROR, NETWORK_SCOPE_ERROR}:
                detail = "Network awareness could not be started safely."
            raise HTTPException(status_code=400, detail=detail) from error
        reports.append(network_report)
        limitations.append("Network awareness is passive only; no active discovery or port scanning was run.")
    if request.include_device_inventory and request.device_inventory_submission is not None:
        reports.append(build_device_inventory_report(request.device_inventory_submission))
        limitations.append("Device inventory findings are based on manual/demo device information.")
        limitations.append("No automatic device discovery, network scan, router login, or router credential collection was used.")

    combined = merge_homeguard_reports(reports, mode="combined")
    combined.safety_notes = _combined_safety_notes(combined.safety_notes)
    limitations.extend(
        [
            "No active network discovery or port scanning is included in this version.",
            "Exports are generated only when requested and are not saved automatically.",
        ]
    )

    export_markdown = render_markdown_report(combined) if request.export_format == ExportFormat.MARKDOWN else None
    export_json = render_json_export(combined) if request.export_format == ExportFormat.JSON else None

    return CombinedReportResponse(
        report=combined,
        export_markdown=export_markdown,
        export_json=export_json,
        warnings=warnings,
        limitations=_unique(limitations),
    )


@router.post("/export/markdown")
def export_markdown_report(report: HomeGuardReport) -> Response:
    return Response(content=render_markdown_report(report), media_type="text/markdown")


@router.post("/export/json")
def export_json_report(report: HomeGuardReport) -> dict:
    return render_json_export(report)


def _combined_safety_notes(notes: list[str]) -> list[str]:
    return _unique(
        [
            *notes,
            "Combined reports are generated in memory and are not saved automatically.",
            "Exports are created only when you click an export button or call an export endpoint.",
            "No network scan was performed.",
            "No settings were changed.",
            "No data was uploaded.",
            "No AI provider call was performed.",
        ]
    )


def _unique(values: list[str]) -> list[str]:
    unique_values: list[str] = []
    for value in values:
        if value not in unique_values:
            unique_values.append(value)
    return unique_values
