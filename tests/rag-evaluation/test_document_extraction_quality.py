"""Quality gates for the in-memory simulated document extraction corpus."""

import pytest

from sunovate_api.evaluation.document_extraction import evaluate, load_evaluation_set, main


def test_extraction_fixture_is_simulated_unique_and_bounded() -> None:
    payload = load_evaluation_set()
    cases = payload["cases"]
    ids = [case["id"] for case in cases]

    assert len(ids) == len(set(ids))
    assert {case["format"] for case in cases} == {"txt", "md", "pdf", "docx", "xlsx", "xls"}
    assert all(case["filename"].startswith("SIMULASI") for case in cases)
    assert all(case["expectedFragments"] for case in cases)


def test_extraction_quality_gates_pass() -> None:
    metrics = evaluate()

    assert metrics.cases == 7
    assert metrics.extraction_success_rate == 1.0
    assert metrics.fragment_recall == 1.0
    assert metrics.forbidden_hits == 0
    assert metrics.structure_pass_rate == 1.0
    assert metrics.instruction_classification_accuracy == 1.0
    assert metrics.passed


def test_evaluator_output_contains_metrics_not_document_content(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main() == 0
    output = capsys.readouterr().out

    assert '"passed": true' in output
    assert "Kesimpulan setelah tabel" not in output
    assert "system prompt" not in output
    assert "SIMULASI-instruksi-tersembunyi.xlsx" not in output
