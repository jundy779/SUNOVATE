"""Structural gates for the controlled SAVI glossary intake."""

from __future__ import annotations

from sunovate_api.hermes.glossary import load_savi_glossary_intake
from sunovate_api.hermes.text import limited_retry_variants, terms


def test_glossary_ids_and_runtime_states_are_consistent() -> None:
    entries = load_savi_glossary_intake().entries
    ids = [entry.id for entry in entries]

    assert len(entries) == 12
    assert len(ids) == len(set(ids))
    assert sum(entry.runtime_eligibility == "LIMITED_SPELLING_RETRY" for entry in entries) == 5
    for entry in entries:
        if entry.runtime_eligibility == "LIMITED_SPELLING_RETRY":
            assert entry.validation_status == "IMPLEMENTED_SPELLING_ONLY"
            assert entry.category == "SPELLING_VARIANT"
        else:
            assert entry.validation_status != "IMPLEMENTED_SPELLING_ONLY"


def test_active_glossary_variants_match_the_runtime_allowlist() -> None:
    active = [
        entry
        for entry in load_savi_glossary_intake().entries
        if entry.runtime_eligibility == "LIMITED_SPELLING_RETRY"
    ]

    for entry in active:
        canonical_terms = terms(entry.canonical_term)
        assert len(canonical_terms) == 1
        canonical = next(iter(canonical_terms))
        expected = terms(" ".join([entry.canonical_term, *entry.variants]))
        assert limited_retry_variants(canonical_terms)[canonical] == expected


def test_blocked_domain_candidates_do_not_expand_runtime_terms() -> None:
    blocked = [
        entry
        for entry in load_savi_glossary_intake().entries
        if entry.runtime_eligibility == "BLOCKED"
    ]

    for entry in blocked:
        for term in terms(" ".join(entry.variants)):
            assert limited_retry_variants(frozenset({term}))[term] == frozenset({term})
