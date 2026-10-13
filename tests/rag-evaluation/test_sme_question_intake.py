"""Structural gates for mentor-provided SAVI question intake.

The intake is excluded from the active golden set until an SME and, where
relevant, a legal reviewer validate the answer, sources, and internal SOP.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sunovate_api.hermes.intake import load_sme_question_intake

INTAKE = (
    Path(__file__).resolve().parents[2]
    / "apps"
    / "api"
    / "sunovate_api"
    / "resources"
    / "sme_question_intake.json"
)
GOLDEN = Path(__file__).resolve().parents[1] / "fixtures" / "rag_golden_set.json"

ALLOWED_STATUSES = {
    "PENDING_SME_VALIDATION",
    "PENDING_LEGAL_VALIDATION",
    "NEEDS_REVISION",
    "VERIFIED",
    "REJECTED",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_sme_intake_is_explicitly_excluded_from_runtime() -> None:
    intake = _load(INTAKE)

    assert intake["dataLabel"] == "MENTOR_PROVIDED_DRAFT"
    assert intake["activationStatus"] == "EXCLUDED_FROM_RUNTIME"
    assert len(intake["cases"]) == 8
    assert len(load_sme_question_intake().cases) == 8


def test_sme_intake_has_review_evidence_and_no_active_cases() -> None:
    cases: list[dict[str, Any]] = _load(INTAKE)["cases"]
    ids = [case["id"] for case in cases]

    assert len(ids) == len(set(ids))
    for case in cases:
        assert case["validationStatus"] in ALLOWED_STATUSES
        assert case["validationStatus"] != "VERIFIED"
        assert case["runtimeEligibility"] == "BLOCKED"
        assert case["question"].strip()
        assert case["draftAnswer"].strip()
        assert case["suppliedReferences"]
        assert case["validationNotes"]


def test_sme_intake_is_not_silently_promoted_to_golden_set() -> None:
    intake_questions = {case["question"] for case in _load(INTAKE)["cases"]}
    golden_questions = {case["question"] for case in _load(GOLDEN)["cases"]}

    assert intake_questions.isdisjoint(golden_questions)
