from fastapi import APIRouter

from app.demo.demo_report import get_demo_report
from app.models.report import HomeGuardReport

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/demo", response_model=HomeGuardReport)
def read_demo_report_alias() -> HomeGuardReport:
    return get_demo_report()
