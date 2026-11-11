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


def test_verified_references_cite_the_auction_regulation_with_a_page() -> None:
    """DEC-20261110-01: references are corrected to PMK 168/PMK.08/2019 with a page in the
    Kompilasi Peraturan SUN, while every case stays blocked from the SAVI runtime."""
    intake = _load(INTAKE)
    assert "DEC-20261110-01" in intake["referenceReview"]
    corrected = {case["id"] for case in intake["cases"] if case.get("verifiedReferences")}
    assert corrected == {"SME-001", "SME-003", "SME-005", "SME-006", "SME-007"}
    for case in intake["cases"]:
        for reference in case.get("verifiedReferences", []):
            assert reference.startswith("PMK 168/PMK.08/2019 Pasal ")
            assert "Kompilasi Peraturan SUN, hal. " in reference
        assert case["runtimeEligibility"] == "BLOCKED"
