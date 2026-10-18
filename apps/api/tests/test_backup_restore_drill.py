"""Fail-closed guards for the SIMULATED_DATA backup/restore drill."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest

from sunovate_api.db.backup_restore_drill import (
    ALLOWED_HOSTS_ENV,
    ALLOWED_SOURCE_DB_ENV,
    CONFIRM_ENV,
    CONFIRM_VALUE,
    DatabaseTarget,
    DrillError,
    _outside_repository,
    _run_client,
    parse_target,
    validate_runtime,
)

PASSWORD = "SIMULATED-secret-never-print"


def target(database: str) -> DatabaseTarget:
    return DatabaseTarget("127.0.0.1", 5432, "sunovate", PASSWORD, database)


def url(database: str, *, host: str = "127.0.0.1", query: str = "") -> str:
    return f"postgresql+psycopg://sunovate:{PASSWORD}@{host}:5432/{database}{query}"


def test_parse_accepts_marked_source_and_restore() -> None:
    assert parse_target(url("sunovate_simul"), role="source").database == "sunovate_simul"
    assert parse_target(url("sunovate_restore"), role="restore").database == "sunovate_restore"


def test_unmarked_source_requires_exact_explicit_allowlist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(DrillError, match=ALLOWED_SOURCE_DB_ENV):
        parse_target(url("sunovate"), role="source")
    monkeypatch.setenv(ALLOWED_SOURCE_DB_ENV, "sunovate")
    assert parse_target(url("sunovate"), role="source").database == "sunovate"


@pytest.mark.parametrize("database", ["postgres", "template0", "template1"])
def test_system_databases_are_rejected(database: str) -> None:
    with pytest.raises(DrillError, match="Database sistem"):
        parse_target(url(database), role="source")


def test_restore_name_must_be_explicit() -> None:
    with pytest.raises(DrillError, match="kata 'restore'"):
        parse_target(url("sunovate_test"), role="restore")


def test_external_hostname_is_rejected_unless_explicitly_allowed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(DrillError, match="lokal/private"):
        parse_target(url("sunovate_simul", host="database.example"), role="source")
    monkeypatch.setenv(ALLOWED_HOSTS_ENV, "database.example")
    assert parse_target(url("sunovate_simul", host="database.example"), role="source").host == (
        "database.example"
    )


def test_query_parameters_are_rejected_without_secret_leak() -> None:
    with pytest.raises(DrillError) as info:
        parse_target(url("sunovate_simul", query="?sslmode=require"), role="source")
    assert PASSWORD not in str(info.value)


def test_runtime_requires_test_env_confirmation_and_distinct_targets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source, restore = target("sunovate_simul"), target("sunovate_restore")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv(CONFIRM_ENV, CONFIRM_VALUE)
    with pytest.raises(DrillError, match="APP_ENV=test"):
        validate_runtime(source, restore)

    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.delenv(CONFIRM_ENV)
    with pytest.raises(DrillError, match=CONFIRM_ENV):
        validate_runtime(source, restore)

    monkeypatch.setenv(CONFIRM_ENV, CONFIRM_VALUE)
    with pytest.raises(DrillError, match="harus berbeda"):
        validate_runtime(source, source)
    validate_runtime(source, restore)


def test_temporary_backup_must_be_outside_repository(tmp_path: Path) -> None:
    assert not _outside_repository(Path(__file__))
    assert _outside_repository(tmp_path / "backup.dump")


def test_client_password_is_only_passed_in_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        captured["command"] = command
        captured["env"] = kwargs["env"]
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    _run_client("pg_dump", ["--format=custom"], target("sunovate_simul"))
    assert PASSWORD not in " ".join(captured["command"])
    assert captured["env"]["PGPASSWORD"] == PASSWORD
