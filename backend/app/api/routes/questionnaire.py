from fastapi import APIRouter

from app.models.questionnaire import QuestionnaireResult, QuestionnaireSection, QuestionnaireSubmission
from app.questionnaire.questions import get_questionnaire_sections
from app.questionnaire.report_builder import evaluate_questionnaire, get_demo_answers

router = APIRouter(prefix="/questionnaire", tags=["questionnaire"])


@router.get("", response_model=list[QuestionnaireSection])
def read_questionnaire() -> list[QuestionnaireSection]:
    return get_questionnaire_sections()


@router.post("/evaluate", response_model=QuestionnaireResult)
def evaluate_questionnaire_submission(submission: QuestionnaireSubmission) -> QuestionnaireResult:
    return evaluate_questionnaire(submission)


@router.get("/demo-answers", response_model=QuestionnaireSubmission)
def read_demo_answers() -> QuestionnaireSubmission:
    return get_demo_answers()
