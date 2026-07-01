from fastapi import APIRouter

from app.checks.windows.runner import run_windows_check_findings, run_windows_local_audit
from app.models.finding import Finding
from app.models.report import HomeGuardReport

router = APIRouter(tags=["windows local checks"])


@router.get(
    "/checks/windows",
    response_model=list[Finding],
    summary="Run read-only Windows posture checks when executed on Windows.",
)
def read_windows_check_findings() -> list[Finding]:
    return run_windows_check_findings()


@router.get(
    "/reports/windows-local",
    response_model=HomeGuardReport,
    summary="Build a Windows local audit report.",
    description=(
        "Runs read-only local Windows posture checks when executed on Windows. "
        "On non-Windows platforms, returns unsupported-platform findings without running Windows commands."
    ),
)
def read_windows_local_report() -> HomeGuardReport:
    return run_windows_local_audit()
