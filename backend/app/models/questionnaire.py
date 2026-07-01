from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.models.finding import Finding


class QuestionnaireAnswerType(str, Enum):
    YES_NO = "yes_no"
    YES_NO_UNSURE = "yes_no_unsure"
    SINGLE_CHOICE = "single_choice"
    MULTI_CHOICE = "multi_choice"
    TEXT_SHORT = "text_short"


class QuestionnaireMode(str, Enum):
    DEMO = "demo"
    QUESTIONNAIRE = "questionnaire"


class QuestionnaireOption(BaseModel):
    value: str = Field(..., min_length=1)
    label: str = Field(..., min_length=1)


class QuestionnaireQuestion(BaseModel):
    id: str = Field(..., min_length=1)
    section: str = Field(..., min_length=1)
    prompt: str = Field(..., min_length=1)
    help_text: str | None = None
    answer_type: QuestionnaireAnswerType
    options: list[QuestionnaireOption] = Field(default_factory=list)
    required: bool = False
    home_user_label: str | None = None


class QuestionnaireAnswer(BaseModel):
    question_id: str = Field(..., min_length=1)
    value: str | list[str] | None = None
    skipped: bool = False


class QuestionnaireSubmission(BaseModel):
    answers: list[QuestionnaireAnswer] = Field(default_factory=list)
    mode: QuestionnaireMode = QuestionnaireMode.QUESTIONNAIRE
    generated_at: datetime | None = None


class QuestionnaireSection(BaseModel):
    id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    questions: list[QuestionnaireQuestion] = Field(default_factory=list)


class QuestionnaireResult(BaseModel):
    answered_count: int = Field(..., ge=0)
    skipped_count: int = Field(..., ge=0)
    findings: list[Finding] = Field(default_factory=list)
    top_actions: list[str] = Field(default_factory=list)


def answer_value_as_text(value: Any) -> str:
    if value is None:
        return "not answered"
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) if value else "not answered"
    return str(value)
