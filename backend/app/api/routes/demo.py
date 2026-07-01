from fastapi import APIRouter

from app.demo.demo_report import get_demo_report
from app.models.finding import Finding
from app.models.report import HomeGuardReport

router = APIRouter(prefix="/demo", tags=["demo"])


@router.get("/report", response_model=HomeGuardReport)
def read_demo_report() -> HomeGuardReport:
    return get_demo_report()


@router.get("/findings", response_model=list[Finding])
def read_demo_findings() -> list[Finding]:
    return get_demo_report().findings
