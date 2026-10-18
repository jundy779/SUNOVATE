"""Fail-closed backup/restore drill for a throwaway SIMULATED_DATA database.

This is validation tooling, not a production backup scheduler. Connection URLs are
read from environment variables and are never printed or passed in process arguments.
"""

from __future__ import annotations

import ipaddress
import json
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final

import psycopg
from psycopg import sql

from .urls import parse_database_url

SOURCE_URL_ENV: Final = "SUNOVATE_BACKUP_SOURCE_URL"
RESTORE_URL_ENV: Final = "SUNOVATE_BACKUP_RESTORE_URL"
CONFIRM_ENV: Final = "SUNOVATE_BACKUP_DRILL_CONFIRM"
ALLOWED_HOSTS_ENV: Final = "SUNOVATE_BACKUP_ALLOWED_HOSTS"
ALLOWED_SOURCE_DB_ENV: Final = "SUNOVATE_BACKUP_ALLOWED_SOURCE_DATABASE"
CONFIRM_VALUE: Final = "SIMULATED_DATA_ONLY"
SYSTEM_DATABASES: Final = frozenset({"postgres", "template0", "template1"})
SOURCE_NAME_MARKERS: Final = ("test", "simul", "demo", "restore")
ROOT = Path(__file__).resolve().parents[4]


class DrillError(RuntimeError):
    """A safe, credential-free drill failure."""


@dataclass(frozen=True, repr=False)
class DatabaseTarget:
    host: str
    port: int
    user: str
    password: str | None
    database: str

    @property
    def identity(self) -> tuple[str, int, str]:
        return (self.host.casefold(), self.port, self.database.casefold())

    def connect_kwargs(self) -> dict[str, Any]:
        values: dict[str, Any] = {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "dbname": self.database,
            "connect_timeout": 5,
        }
        if self.password is not None:
            values["password"] = self.password
        return values

    def client_env(self) -> dict[str, str]:
        values = {
            **os.environ,
            "PGHOST": self.host,
            "PGPORT": str(self.port),
            "PGUSER": self.user,
            "PGDATABASE": self.database,
            "PGCONNECT_TIMEOUT": "5",
        }
        if self.password is not None:
            values["PGPASSWORD"] = self.password
        else:
            values.pop("PGPASSWORD", None)
        return values


@dataclass(frozen=True)
class DrillReport:
    status: str
    tables_checked: int
    rows_checked: int
    simulated_columns_checked: int
    backup_bytes: int
    dump_seconds: float
    restore_seconds: float
    verification_seconds: float
    alembic_revision: str
    audit_trigger_enabled: bool


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise DrillError(f"{name} wajib diisi")
    return value


def _allowed_hosts() -> set[str]:
    return {
        item.strip().casefold()
        for item in os.environ.get(ALLOWED_HOSTS_ENV, "").split(",")
        if item.strip()
    }


def _host_is_private(host: str) -> bool:
    if host.casefold() == "localhost":
        return True
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return host.casefold() in _allowed_hosts()
    return (address.is_loopback or address.is_private) and not (
        address.is_multicast or address.is_unspecified
    )


def parse_target(raw_url: str, *, role: str) -> DatabaseTarget:
    """Parse and validate a test-only target without rendering the secret URL."""
    url = parse_database_url(raw_url)
    if url.query:
        raise DrillError(f"URL database {role} tidak boleh memuat parameter query")
    if not url.host or not url.username or not url.database:
        raise DrillError(f"URL database {role} harus memuat host, pengguna, dan nama database")
    if url.database.casefold() in SYSTEM_DATABASES:
        raise DrillError(f"Database sistem tidak boleh menjadi target {role}")
    if not _host_is_private(url.host):
        raise DrillError(
            f"Host database {role} harus lokal/private atau tercantum pada {ALLOWED_HOSTS_ENV}"
        )
    if role == "restore" and "restore" not in url.database.casefold():
        raise DrillError("Nama database restore wajib memuat kata 'restore'")
    if role == "source":
        allowed_source = os.environ.get(ALLOWED_SOURCE_DB_ENV, "").strip().casefold()
        marked = any(marker in url.database.casefold() for marker in SOURCE_NAME_MARKERS)
        if not marked and allowed_source != url.database.casefold():
            raise DrillError(
                "Nama database sumber wajib bertanda test/simul/demo atau diizinkan secara tepat "
                f"melalui {ALLOWED_SOURCE_DB_ENV}"
            )
    return DatabaseTarget(
        host=url.host,
        port=url.port or 5432,
        user=url.username,
        password=url.password,
        database=url.database,
    )


def validate_runtime(source: DatabaseTarget, restore: DatabaseTarget) -> None:
    if os.environ.get("APP_ENV") != "test":
        raise DrillError("Latihan backup-restore hanya boleh berjalan dengan APP_ENV=test")
    if os.environ.get(CONFIRM_ENV) != CONFIRM_VALUE:
        raise DrillError(f"{CONFIRM_ENV} harus bernilai {CONFIRM_VALUE}")
    if source.identity == restore.identity:
        raise DrillError("Database sumber dan restore harus berbeda")


def _table_names(connection: psycopg.Connection[Any]) -> list[str]:
    rows = connection.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """
    ).fetchall()
    return [str(row[0]) for row in rows]


def _table_counts(connection: psycopg.Connection[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for table in _table_names(connection):
        row = connection.execute(
            sql.SQL("SELECT count(*) FROM {}").format(sql.Identifier(table))
        ).fetchone()
        counts[table] = int(row[0]) if row else 0
    return counts


def _assert_simulated_only(connection: psycopg.Connection[Any]) -> int:
    rows = connection.execute(
        """
        SELECT table_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND column_name = 'data_origin'
        ORDER BY table_name
        """
    ).fetchall()
    tables = [str(row[0]) for row in rows]
    if not tables:
        raise DrillError("Tidak ditemukan kolom data_origin untuk membuktikan data simulasi")
    for table in tables:
        statement = sql.SQL(
            "SELECT count(*) FROM {} WHERE data_origin <> %s OR data_origin IS NULL"
        ).format(sql.Identifier(table))
        row = connection.execute(
            statement,
            ("SIMULATED_DATA",),
        ).fetchone()
        if row and int(row[0]) > 0:
            raise DrillError("Latihan dihentikan karena ditemukan data non-simulasi")
    return len(tables)


def _alembic_revision(connection: psycopg.Connection[Any]) -> str:
    try:
        row = connection.execute("SELECT version_num FROM alembic_version").fetchone()
    except psycopg.Error as exc:
        raise DrillError("Revision Alembic tidak dapat diverifikasi") from exc
    if not row or not row[0]:
        raise DrillError("Revision Alembic tidak ditemukan")
    return str(row[0])


def _audit_trigger_enabled(connection: psycopg.Connection[Any]) -> bool:
    row = connection.execute(
        """
        SELECT pg_get_triggerdef(t.oid), t.tgenabled
        FROM pg_trigger AS t
        JOIN pg_class AS c ON c.oid = t.tgrelid
        JOIN pg_namespace AS n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public'
          AND c.relname = 'audit_logs'
          AND t.tgname = 'audit_logs_append_only'
          AND NOT t.tgisinternal
        """
    ).fetchone()
    if not row:
        return False
    definition, enabled = str(row[0]).upper(), str(row[1])
    return enabled != "D" and "BEFORE UPDATE OR DELETE" in definition


def _assert_empty_restore(connection: psycopg.Connection[Any]) -> None:
    if _table_names(connection):
        raise DrillError(
            "Database restore harus kosong; tidak ada objek yang akan dihapus otomatis"
        )


def _run_client(executable: str, args: list[str], target: DatabaseTarget) -> float:
    started = time.monotonic()
    try:
        subprocess.run(  # noqa: S603
            [executable, *args],
            env=target.client_env(),
            capture_output=True,
            text=True,
            timeout=300,
            check=True,
        )
    except FileNotFoundError as exc:
        raise DrillError("Klien PostgreSQL yang diperlukan tidak tersedia") from exc
    except subprocess.TimeoutExpired as exc:
        raise DrillError("Klien PostgreSQL melewati batas waktu 300 detik") from exc
    except subprocess.CalledProcessError as exc:
        raise DrillError(
            "Klien PostgreSQL gagal; detail disembunyikan untuk melindungi data"
        ) from exc
    return time.monotonic() - started


def _outside_repository(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return True
    return False


def run_drill(source: DatabaseTarget, restore: DatabaseTarget) -> DrillReport:
    validate_runtime(source, restore)
    pg_dump = shutil.which("pg_dump")
    pg_restore = shutil.which("pg_restore")
    if not pg_dump or not pg_restore:
        raise DrillError("pg_dump dan pg_restore wajib tersedia pada PATH")

    with psycopg.connect(**source.connect_kwargs()) as source_connection:
        source_counts = _table_counts(source_connection)
        if not source_counts or sum(source_counts.values()) == 0:
            raise DrillError("Database sumber kosong; latihan tidak membuktikan pemulihan data")
        simulated_columns = _assert_simulated_only(source_connection)
        source_revision = _alembic_revision(source_connection)
        if not _audit_trigger_enabled(source_connection):
            raise DrillError("Trigger append-only audit tidak aktif pada database sumber")

    with psycopg.connect(**restore.connect_kwargs()) as restore_connection:
        _assert_empty_restore(restore_connection)

    with tempfile.TemporaryDirectory(prefix="sunovate-backup-drill-") as temp_dir:
        backup_file = Path(temp_dir) / "sunovate-simulated.dump"
        if not _outside_repository(backup_file):
            raise DrillError("File sementara backup harus berada di luar repository")
        dump_seconds = _run_client(
            pg_dump,
            ["--format=custom", "--no-owner", "--no-privileges", "--file", str(backup_file)],
            source,
        )
        backup_bytes = backup_file.stat().st_size
        if backup_bytes <= 0:
            raise DrillError("File backup kosong")
        restore_seconds = _run_client(
            pg_restore,
            [
                "--exit-on-error",
                "--no-owner",
                "--no-privileges",
                "--dbname",
                restore.database,
                str(backup_file),
            ],
            restore,
        )

        verification_started = time.monotonic()
        with psycopg.connect(**restore.connect_kwargs()) as restored_connection:
            restored_counts = _table_counts(restored_connection)
            if restored_counts != source_counts:
                raise DrillError("Jumlah baris hasil restore berbeda dari database sumber")
            if _alembic_revision(restored_connection) != source_revision:
                raise DrillError("Revision Alembic hasil restore berbeda dari database sumber")
            if not _audit_trigger_enabled(restored_connection):
                raise DrillError("Trigger append-only audit tidak aktif setelah restore")
            _assert_simulated_only(restored_connection)
        verification_seconds = time.monotonic() - verification_started

    return DrillReport(
        status="PASSED",
        tables_checked=len(source_counts),
        rows_checked=sum(source_counts.values()),
        simulated_columns_checked=simulated_columns,
        backup_bytes=backup_bytes,
        dump_seconds=round(dump_seconds, 3),
        restore_seconds=round(restore_seconds, 3),
        verification_seconds=round(verification_seconds, 3),
        alembic_revision=source_revision,
        audit_trigger_enabled=True,
    )


def main() -> int:
    try:
        source = parse_target(_required_env(SOURCE_URL_ENV), role="source")
        restore = parse_target(_required_env(RESTORE_URL_ENV), role="restore")
        report = run_drill(source, restore)
    except DrillError as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}, ensure_ascii=False))
        return 1
    except psycopg.Error:
        print(
            json.dumps(
                {"status": "BLOCKED", "reason": "Koneksi atau pemeriksaan PostgreSQL gagal"},
                ensure_ascii=False,
            )
        )
        return 1
    print(json.dumps(asdict(report), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
