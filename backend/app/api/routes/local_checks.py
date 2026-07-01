from fastapi import APIRouter

from app.checks.linux.runner import run_linux_local_audit
from app.checks.macos.runner import run_macos_local_audit
from app.models.report import HomeGuardReport

router = APIRouter(tags=["local platform checks"])


@router.get(
    "/reports/macos-local",
    response_model=HomeGuardReport,
    summary="Build a macOS local audit report.",
    description=(
        "Runs read-only local macOS posture checks when executed on macOS. "
        "On non-macOS platforms, returns unsupported-platform findings without running macOS commands."
    ),
)
def read_macos_local_report() -> HomeGuardReport:
    return run_macos_local_audit()


@router.get(
    "/reports/linux-local",
    response_model=HomeGuardReport,
    summary="Build a Linux local audit report.",
    description=(
        "Runs read-only local Linux posture checks when executed on Linux. "
        "On non-Linux platforms, returns unsupported-platform findings without running Linux commands."
    ),
)
def read_linux_local_report() -> HomeGuardReport:
    return run_linux_local_audit()
