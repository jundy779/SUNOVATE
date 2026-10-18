"""Safety checks for the private single-computer demo package."""

from __future__ import annotations

import importlib.util
import os
import shutil
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "validation" / "demo_preflight.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("demo_preflight", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


preflight = load_module()
PreflightError = preflight.PreflightError


def valid_environment() -> str:
    password = "SIMULATED-db-password-4U8k9z"
    secret = "SIMULATED-auth-secret-2nB9vP6xQ4mL8sT1"
    return "\n".join(
        (
            "APP_ENV=development",
            "LOG_LEVEL=INFO",
            "DEMO_HTTP_PORT=8080",
            "DEMO_ORIGIN=http://127.0.0.1:8080",
            "POSTGRES_DB=sunovate",
            "POSTGRES_USER=sunovate",
            f"POSTGRES_PASSWORD={password}",
            "DATABASE_URL=postgresql+asyncpg://"
            f"sunovate:{password}@postgres:5432/sunovate",
            "DEV_AUTH_ENABLED=true",
            f"DEV_AUTH_SECRET={secret}",
            "",
        )
    )


def write_env(tmp_path: Path, content: str | None = None) -> Path:
    path = tmp_path / "demo.env"
    path.write_text(content or valid_environment(), encoding="utf-8")
    path.chmod(0o600)
    return path


def test_tracked_demo_scaffold_passes() -> None:
    checks = preflight.validate_scaffold(ROOT)
    assert "nginx_limits_and_safe_logging" in checks
    assert "tunnel_template_inactive" in checks


def copied_root(tmp_path: Path) -> Path:
    root = tmp_path / "repository"
    shutil.copytree(ROOT / "deploy" / "demo", root / "deploy" / "demo")
    (root / ".gitignore").write_text("deploy/demo/demo.env\n", encoding="utf-8")
    return root


def test_scaffold_rejects_query_string_logging(tmp_path: Path) -> None:
    root = copied_root(tmp_path)
    config = root / "deploy" / "demo" / "nginx" / "nginx.conf"
    config.write_text(
        config.read_text(encoding="utf-8").replace("$request_method $uri", "$request"),
        encoding="utf-8",
    )
    with pytest.raises(PreflightError, match="query"):
        preflight.validate_scaffold(root)


def test_scaffold_rejects_active_cloudflared_service(tmp_path: Path) -> None:
    root = copied_root(tmp_path)
    compose = root / "deploy" / "demo" / "docker-compose.demo.yml"
    compose.write_text(
        compose.read_text(encoding="utf-8").replace(
            "services:\n", "services:\n  cloudflared:\n    image: cloudflare/cloudflared:latest\n"
        ),
        encoding="utf-8",
    )
    with pytest.raises(PreflightError, match="cloudflared"):
        preflight.validate_scaffold(root)


def test_valid_private_environment_passes(tmp_path: Path) -> None:
    checks = preflight.validate_environment(write_env(tmp_path))
    assert "database_internal_only" in checks
    assert "secrets_non_placeholder_and_distinct" in checks


def test_placeholder_is_rejected_without_printing_value(tmp_path: Path) -> None:
    content = valid_environment().replace(
        "SIMULATED-db-password-4U8k9z", "CHANGE_ME_DEMO_DATABASE_PASSWORD"
    )
    with pytest.raises(PreflightError) as info:
        preflight.validate_environment(write_env(tmp_path, content))
    assert "nilai contoh" in str(info.value)
    assert "CHANGE_ME_DEMO_DATABASE_PASSWORD" not in str(info.value)


def test_non_loopback_origin_is_rejected(tmp_path: Path) -> None:
    content = valid_environment().replace(
        "DEMO_ORIGIN=http://127.0.0.1:8080", "DEMO_ORIGIN=http://0.0.0.0:8080"
    )
    with pytest.raises(PreflightError, match="loopback"):
        preflight.validate_environment(write_env(tmp_path, content))


def test_external_database_host_is_rejected(tmp_path: Path) -> None:
    content = valid_environment().replace("@postgres:5432", "@database.example:5432")
    with pytest.raises(PreflightError, match="service postgres internal"):
        preflight.validate_environment(write_env(tmp_path, content))


def test_database_password_mismatch_is_rejected_without_leak(tmp_path: Path) -> None:
    mismatched = "SIMULATED-other-password-1x2y3z"
    content = valid_environment().replace(
        "SIMULATED-db-password-4U8k9z@postgres", f"{mismatched}@postgres"
    )
    with pytest.raises(PreflightError) as info:
        preflight.validate_environment(write_env(tmp_path, content))
    assert "tidak cocok" in str(info.value)
    assert mismatched not in str(info.value)


def test_unknown_environment_key_is_rejected(tmp_path: Path) -> None:
    content = valid_environment() + "EXTERNAL_AI_DATA_EGRESS_ENABLED=true\n"
    with pytest.raises(PreflightError, match="tidak diizinkan"):
        preflight.validate_environment(write_env(tmp_path, content))


@pytest.mark.skipif(os.name == "nt", reason="POSIX permission bits are not available")
def test_group_readable_environment_is_rejected(tmp_path: Path) -> None:
    path = write_env(tmp_path)
    path.chmod(0o640)
    with pytest.raises(PreflightError, match="chmod 600"):
        preflight.validate_environment(path)
