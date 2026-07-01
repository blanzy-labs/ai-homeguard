from fastapi import APIRouter

from app.checks.local_runner import run_local_device_audit
from app.checks.linux.runner import run_linux_local_audit
from app.checks.macos.runner import run_macos_local_audit
from app.core.platform import get_runtime_context
from app.models.report import HomeGuardReport
from app.models.runtime import RuntimeContext

router = APIRouter(tags=["local platform checks"])


@router.get(
    "/runtime",
    response_model=RuntimeContext,
    summary="Return privacy-safe runtime context.",
    description=(
        "Returns minimal platform/runtime context without exposing hostname strings, usernames, "
        "personal paths, environment variables, or secrets."
    ),
)
def read_runtime_context() -> RuntimeContext:
    return get_runtime_context()


@router.get(
    "/reports/local-device",
    response_model=HomeGuardReport,
    summary="Build an auto-detected local device audit report.",
    description=(
        "Auto-detects the runtime platform and runs the matching read-only local audit. "
        "Unknown platforms return an unable-to-check report without running platform commands."
    ),
)
def read_local_device_report() -> HomeGuardReport:
    return run_local_device_audit()


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
