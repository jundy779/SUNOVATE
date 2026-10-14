"""Read-only SAVI glossary intake with explicit runtime eligibility."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field

from ..core.responses import ApiModel

GlossaryStatus = Literal[
    "IMPLEMENTED_SPELLING_ONLY",
    "PENDING_MENTOR_VALIDATION",
    "PENDING_SME_VALIDATION",
    "PENDING_LEGAL_VALIDATION",
    "REJECTED",
]


class GlossaryEntry(ApiModel):
    id: str = Field(pattern=r"^GLS-[0-9]{3}$")
    canonical_term: str = Field(min_length=2)
    variants: list[str] = Field(min_length=1)
    category: Literal["SPELLING_VARIANT", "DOMAIN_MAPPING", "ABBREVIATION", "HISTORICAL_NAME"]
    definition: str = Field(min_length=3)
    source_references: list[str] = Field(min_length=1)
    validation_status: GlossaryStatus
    runtime_eligibility: Literal["LIMITED_SPELLING_RETRY", "BLOCKED"]
    validation_notes: list[str] = Field(min_length=1)


class SaviGlossaryIntake(ApiModel):
    data_label: Literal["CONTROLLED_GLOSSARY_DRAFT"]
    source: str
    purpose: str
    entries: list[GlossaryEntry] = Field(min_length=1)


@lru_cache(maxsize=1)
def load_savi_glossary_intake() -> SaviGlossaryIntake:
    path = Path(__file__).resolve().parents[1] / "resources" / "savi_glossary_intake.json"
    return SaviGlossaryIntake.model_validate_json(path.read_text(encoding="utf-8"))
