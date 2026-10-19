import json

import pytest

from sunovate_api.evaluation.demo_journey import (
    DemoJourneyError,
    main,
    require_simulated_backend,
    run_demo_journey,
)


def test_demo_journey_covers_the_private_simulated_flow() -> None:
    report = run_demo_journey(backend="simulated")

    assert report.status == "PASSED"
    assert report.scope == "SIMULATED_DATA_IN_MEMORY"
    assert [step.key for step in report.steps] == [
        "system_health",
        "staff_login",
        "scoped_dashboard",
        "work_monitoring",
        "knowledge_hub",
        "authorized_search",
        "savi_grounded_response",
        "savi_out_of_scope_refusal",
        "savi_policy_refusal",
    ]
    assert all(step.status == "PASSED" for step in report.steps)
    assert report.external_connections is False
    assert report.persistent_writes is False
    assert report.postgres_validated is False
    assert report.host_validated is False


def test_demo_journey_refuses_non_simulated_backend() -> None:
    with pytest.raises(DemoJourneyError, match="backend simulasi"):
        require_simulated_backend("postgres")


def test_demo_journey_cli_blocks_postgres_before_connecting(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("SUNOVATE_TEST_BACKEND", "postgres")

    assert main() == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "BLOCKED"
    assert "backend simulasi" in payload["reason"]


def test_demo_journey_cli_does_not_print_business_content(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main() == 0
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert payload["status"] == "PASSED"
    assert "metadata wajib" not in output.casefold()
    assert "piala dunia" not in output.casefold()
    assert "system prompt" not in output.casefold()
    assert "accessToken" not in output
    assert "answer" not in output.casefold()
    assert "citation" not in output.casefold()
