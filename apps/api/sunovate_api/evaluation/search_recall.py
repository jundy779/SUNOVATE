"""Evaluate authorized search against the SIMULATED_DATA relevance set.

Run from the repository root with ``pnpm search:eval``. When the test runtime is
configured for PostgreSQL, the same evaluator exercises GIN-backed FTS.
"""

from __future__ import annotations

import json
import warnings
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

warnings.filterwarnings("ignore", message=r"Using `httpx` with `starlette\.testclient`.*")

from ..store.dataset import sid  # noqa: E402
from ..testing import TEST_BACKEND, login, make_client  # noqa: E402

FIXTURE = Path(__file__).resolve().parents[4] / "tests" / "fixtures" / "search_relevance_set.json"
TOP_K = 5


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    first_expected_rank: int | None
    forbidden_hits: int


@dataclass(frozen=True)
class SearchMetrics:
    backend: str
    cases: int
    recall_cases: int
    hit_at_5: float
    mean_reciprocal_rank: float
    unauthorized_leakage: int
    passed: bool
    case_results: tuple[CaseResult, ...]


def load_evaluation_set() -> dict[str, Any]:
    payload: dict[str, Any] = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if payload.get("dataLabel") != "SIMULATED_DATA":
        raise ValueError("Dataset evaluasi pencarian wajib berlabel SIMULATED_DATA")
    return payload


def evaluate() -> SearchMetrics:
    payload = load_evaluation_set()
    results: list[CaseResult] = []
    reciprocal_ranks: list[float] = []
    leakage = 0

    for case in payload["cases"]:
        client = make_client()
        response = client.get(
            "/api/v1/search",
            params={"q": case["query"], "pageSize": TOP_K},
            headers=login(client, case["user"]),
        )
        if response.status_code != 200:
            raise RuntimeError(f"{case['id']} gagal dengan status {response.status_code}")

        found = [item["knowledgeEntryId"] for item in response.json()["data"]]
        expected = {str(sid(f"knowledge:{key}")) for key in case["expectedEntries"]}
        forbidden = {str(sid(f"knowledge:{key}")) for key in case["forbiddenEntries"]}
        first_rank = next(
            (index for index, entry_id in enumerate(found, start=1) if entry_id in expected),
            None,
        )
        forbidden_hits = len(set(found) & forbidden)
        leakage += forbidden_hits
        if expected:
            reciprocal_ranks.append(0.0 if first_rank is None else 1 / first_rank)
        results.append(CaseResult(case["id"], first_rank, forbidden_hits))

    hits = sum(result.first_expected_rank is not None for result in results)
    recall_cases = len(reciprocal_ranks)
    hit_at_5 = hits / recall_cases if recall_cases else 0.0
    mrr = sum(reciprocal_ranks) / recall_cases if recall_cases else 0.0
    thresholds = payload["thresholds"]
    passed = hit_at_5 >= thresholds["hitAt5"] and leakage == thresholds["unauthorizedLeakage"]
    return SearchMetrics(
        backend=TEST_BACKEND,
        cases=len(results),
        recall_cases=recall_cases,
        hit_at_5=round(hit_at_5, 4),
        mean_reciprocal_rank=round(mrr, 4),
        unauthorized_leakage=leakage,
        passed=passed,
        case_results=tuple(results),
    )


def main() -> int:
    metrics = evaluate()
    print(json.dumps(asdict(metrics), indent=2, ensure_ascii=False))
    return 0 if metrics.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
