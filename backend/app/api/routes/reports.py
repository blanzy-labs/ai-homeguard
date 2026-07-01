from fastapi import APIRouter

from app.demo.demo_report import get_demo_report
from app.models.questionnaire import QuestionnaireSubmission
from app.models.report import HomeGuardReport
from app.questionnaire.report_builder import build_questionnaire_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/demo", response_model=HomeGuardReport)
def read_demo_report_alias() -> HomeGuardReport:
    return get_demo_report()


@router.post("/questionnaire", response_model=HomeGuardReport)
def read_questionnaire_report(submission: QuestionnaireSubmission) -> HomeGuardReport:
    return build_questionnaire_report(submission)
