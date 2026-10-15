"""Search quality and authorization gates for lexical and PostgreSQL FTS modes."""

from sunovate_api.evaluation.search_recall import evaluate, load_evaluation_set


def test_search_relevance_fixture_is_safe_and_unique() -> None:
    payload = load_evaluation_set()
    ids = [case["id"] for case in payload["cases"]]

    assert len(ids) == len(set(ids))
    assert all(case["query"].strip() for case in payload["cases"])
    assert all(
        not (set(case["expectedEntries"]) & set(case["forbiddenEntries"]))
        for case in payload["cases"]
    )


def test_search_hit_at_5_and_leakage_gate() -> None:
    metrics = evaluate()

    assert metrics.unauthorized_leakage == 0
    assert metrics.hit_at_5 >= 0.9
    assert metrics.passed
