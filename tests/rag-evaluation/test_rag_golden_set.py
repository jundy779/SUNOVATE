"""RAG evaluation against tests/fixtures/rag_golden_set.json (SIMULATED_DATA).

Hard gates: unauthorized leakage = 0, citation validity = 100%.
PROPOSED gates for this deterministic provider: decision accuracy = 100%, hit rate = 100%.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from sunovate_api.store.dataset import sid
from sunovate_api.testing import login, make_client

GOLDEN = Path(__file__).resolve().parents[1] / "fixtures" / "rag_golden_set.json"
CASES: list[dict[str, Any]] = json.loads(GOLDEN.read_text(encoding="utf-8"))["cases"]


def _run(case: dict[str, Any]) -> dict[str, Any]:
    client = make_client()
    response = client.post("/api/v1/hermes/query", json={"question": case["question"]},
                           headers=login(client, case["user"]))
    assert response.status_code == 200, response.text
    data: dict[str, Any] = response.json()["data"]
    return data


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_golden_case(case: dict[str, Any]) -> None:
    data = _run(case)
    cited = {c["knowledgeEntryId"] for c in data["citations"]}
    expected = {str(sid(f"knowledge:{k}")) for k in case["expectedEntries"]}
    forbidden = {str(sid(f"knowledge:{k}")) for k in case["forbiddenEntries"]}

    assert data["decision"] == case["expectedDecision"]
    assert not cited & forbidden, "unauthorized or ineligible source leaked"
    assert expected <= cited
    if data["decision"] != "ANSWERED":
        assert data["citations"] == []


def test_aggregate_metrics() -> None:
    results = [(case, _run(case)) for case in CASES]
    leakage = sum(
        bool({c["knowledgeEntryId"] for c in d["citations"]}
             & {str(sid(f"knowledge:{k}")) for k in case["forbiddenEntries"]})
        for case, d in results
    )
    answered = [d for _, d in results if d["decision"] == "ANSWERED"]
    citation_valid = sum(
        bool(d["citations"]) and all(f"[{c['index']}]" in d["answer"] for c in d["citations"])
        for d in answered
    )
    accuracy = sum(d["decision"] == c["expectedDecision"] for c, d in results) / len(results)
    assert leakage == 0
    assert citation_valid == len(answered)
    assert accuracy == 1.0
