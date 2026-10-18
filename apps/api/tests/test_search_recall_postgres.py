"""Safety gate for running the search evaluator on an explicit PostgreSQL target."""

from __future__ import annotations

import os

import pytest

from sunovate_api.db.backup_restore_drill import DrillError
from sunovate_api.evaluation.search_recall_postgres import (
    CONFIRM_ENV,
    CONFIRM_VALUE,
    prepare_environment,
)

PASSWORD = "SIMULATED-evaluator-secret"
URL = f"postgresql+psycopg://sunovate:{PASSWORD}@127.0.0.1:5432/sunovate_restore"


def test_postgres_evaluator_requires_test_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv(CONFIRM_ENV, CONFIRM_VALUE)
    with pytest.raises(DrillError, match="APP_ENV=test"):
        prepare_environment(URL)


def test_postgres_evaluator_requires_explicit_confirmation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.delenv(CONFIRM_ENV, raising=False)
    with pytest.raises(DrillError, match=CONFIRM_ENV):
        prepare_environment(URL)


def test_postgres_evaluator_selects_postgres_after_guard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv(CONFIRM_ENV, CONFIRM_VALUE)
    monkeypatch.delenv("SUNOVATE_TEST_BACKEND", raising=False)
    prepare_environment(URL)
    assert os.environ["SUNOVATE_TEST_BACKEND"] == "postgres"


def test_postgres_evaluator_rejects_public_target_without_leaking_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv(CONFIRM_ENV, CONFIRM_VALUE)
    external = URL.replace("127.0.0.1", "database.example")
    with pytest.raises(DrillError) as info:
        prepare_environment(external)
    assert PASSWORD not in str(info.value)
