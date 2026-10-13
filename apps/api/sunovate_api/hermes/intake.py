"""Read-only mentor/SME question intake, excluded from SAVI answer runtime."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field

from ..core.responses import ApiModel

ValidationStatus = Literal[
    "PENDING_SME_VALIDATION",
    "PENDING_LEGAL_VALIDATION",
    "NEEDS_REVISION",
    "VERIFIED",
    "REJECTED",
]


class SmeQuestionCase(ApiModel):
    id: str = Field(pattern=r"^SME-[0-9]{3}$")
    question: str = Field(min_length=3)
    draft_answer: str = Field(min_length=3)
    supplied_references: list[str] = Field(min_length=1)
    candidate_references: list[str] = Field(default_factory=list)
    validation_notes: list[str] = Field(min_length=1)
    validation_status: ValidationStatus
    runtime_eligibility: Literal["BLOCKED"]


class SmeQuestionIntake(ApiModel):
    data_label: Literal["MENTOR_PROVIDED_DRAFT"]
    source: str
    purpose: str
    activation_status: Literal["EXCLUDED_FROM_RUNTIME"]
    cases: list[SmeQuestionCase] = Field(min_length=1)


@lru_cache(maxsize=1)
def load_sme_question_intake() -> SmeQuestionIntake:
    path = Path(__file__).resolve().parents[1] / "resources" / "sme_question_intake.json"
    return SmeQuestionIntake.model_validate_json(path.read_text(encoding="utf-8"))
