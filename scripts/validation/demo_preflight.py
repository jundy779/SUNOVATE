"""Fail-closed static and environment preflight for the private demo package.

The checker never prints environment values. It validates tracked deployment files by
default and can additionally validate a real, git-ignored demo.env with ``--env-file``.
It does not start containers or activate Cloudflare Tunnel.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
DEMO_DIR = ROOT / "deploy" / "demo"
ALLOWED_ENV_KEYS = frozenset(
    {
        "APP_ENV",
        "LOG_LEVEL",
        "DEMO_HTTP_PORT",
        "DEMO_ORIGIN",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "DATABASE_URL",
        "DEV_AUTH_ENABLED",
        "DEV_AUTH_SECRET",
    }
)
REQUIRED_ENV_KEYS = ALLOWED_ENV_KEYS
PLACEHOLDER_MARKERS = ("change_me", "placeholder", "example.invalid")
SAFE_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,62}$")
RAW_REQUEST_TOKEN = re.compile(r"(?<![A-Za-z0-9_])\$request(?![A-Za-z0-9_])")


class PreflightError(RuntimeError):
    """A credential-free validation error."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PreflightError(message)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PreflightError(f"Berkas wajib tidak dapat dibaca: {path.relative_to(ROOT)}") from exc


def validate_scaffold(root: Path = ROOT) -> tuple[str, ...]:
    demo_dir = root / "deploy" / "demo"
    compose = _read(demo_dir / "docker-compose.demo.yml")
    nginx = _read(demo_dir / "nginx" / "nginx.conf")
    headers = _read(demo_dir / "nginx" / "includes" / "security-headers.conf")
    cloudflared = _read(demo_dir / "cloudflared.example.yml")
    docker_api = _read(demo_dir / "Dockerfile.api")
    docker_web = _read(demo_dir / "Dockerfile.web")
    gitignore = _read(root / ".gitignore")
    example = _read(demo_dir / "demo.env.example")

    _require(compose.count("ports:") == 1, "Hanya proxy yang boleh memiliki blok ports")
    _require(
        '"127.0.0.1:${DEMO_HTTP_PORT:-8080}:8080"' in compose,
        "Port proxy wajib terikat ke 127.0.0.1",
    )
    _require(not re.search(r"^\s{2}cloudflared\s*:", compose, re.MULTILINE),
             "Service cloudflared tidak boleh aktif di Compose")
    _require(compose.count("internal: true") == 2,
             "Network aplikasi dan data wajib internal")
    for port in ("3000", "8000", "5432"):
        _require(f'- "{port}"' in compose, f"Port internal {port} wajib memakai expose")
    for lock in (
        'PRIVATE_DATA_MODE: "true"',
        'PUBLIC_INDEXING_ENABLED: "false"',
        'EXTERNAL_AI_DATA_EGRESS_ENABLED: "false"',
        'EXTERNAL_AGENT_ACCESS_ENABLED: "false"',
        'TELEMETRY_DATA_EGRESS_ENABLED: "false"',
        "DATA_BACKEND: postgres",
        "NOTIFICATION_PROVIDER: disabled",
        "EMBEDDING_PROVIDER: disabled",
        "API_TRUSTED_PROXY_CIDRS: 172.30.0.10/32",
    ):
        _require(lock in compose, f"Kunci konfigurasi privat hilang: {lock.split(':')[0]}")
    _require(compose.count("read_only: true") >= 3,
             "Proxy, web, dan API wajib memakai filesystem read-only")
    _require(compose.count("no-new-privileges:true") >= 4,
             "Semua container wajib menolak privilege escalation")

    _require("server_tokens off;" in nginx, "Versi Nginx wajib disembunyikan")
    _require("client_max_body_size 3m;" in nginx, "Batas body Nginx wajib 3 MiB")
    _require("$request_method $uri" in nginx,
             "Access log wajib memakai method dan path tanpa query")
    _require(not RAW_REQUEST_TOKEN.search(nginx),
             "Access log tidak boleh memakai $request karena memuat query string")
    for unsafe_token in ("$args", "$query_string", "$request_uri"):
        _require(unsafe_token not in nginx,
                 f"Access log tidak boleh memuat token query {unsafe_token}")
    for header in (
        'Cache-Control "no-store, private, max-age=0, must-revalidate"',
        'Referrer-Policy "no-referrer"',
        'X-Frame-Options "DENY"',
        'X-Robots-Tag "noindex, nofollow, noarchive, nosnippet, noimageindex"',
    ):
        _require(header in headers, f"Header privat wajib hilang atau berubah: {header.split()[0]}")

    _require("example.invalid" in cloudflared,
             "Contoh tunnel wajib memakai domain .invalid")
    _require("<APPROVED_TUNNEL_UUID>" in cloudflared,
             "Contoh tunnel wajib mempertahankan placeholder ID")
    _require("service: http://127.0.0.1:8080" in cloudflared,
             "Origin contoh tunnel wajib loopback")
    _require("token:" not in cloudflared.casefold(),
             "Contoh tunnel tidak boleh memuat token")
    _require("USER sunovate" in docker_api and "USER node" in docker_web,
             "Container aplikasi wajib memakai user non-root")
    _require("deploy/demo/demo.env" in gitignore,
             "Berkas demo.env wajib diabaikan Git")
    for marker in ("CHANGE_ME_DEMO_DATABASE_PASSWORD", "CHANGE_ME_AT_LEAST_32_RANDOM_CHARACTERS"):
        _require(marker in example, "Contoh environment wajib mempertahankan placeholder")

    return (
        "compose_private_networks",
        "compose_localhost_binding",
        "compose_private_runtime_locks",
        "compose_container_hardening",
        "nginx_limits_and_safe_logging",
        "private_response_headers",
        "tunnel_template_inactive",
        "non_root_images",
        "environment_file_gitignored",
        "example_contains_placeholders_only",
    )


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(_read(path).splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export ") or "=" not in line:
            raise PreflightError(f"Format environment tidak valid pada baris {line_number}")
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if key in values:
            raise PreflightError(f"Variabel environment ganda: {key}")
        if key not in ALLOWED_ENV_KEYS:
            raise PreflightError(f"Variabel environment tidak diizinkan: {key}")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        values[key] = value
    missing = sorted(REQUIRED_ENV_KEYS - values.keys())
    if missing:
        raise PreflightError("Variabel environment wajib belum lengkap: " + ", ".join(missing))
    return values


def _not_placeholder(value: str, *, label: str, minimum: int) -> None:
    _require(len(value) >= minimum, f"{label} terlalu pendek; minimum {minimum} karakter")
    folded = value.casefold()
    _require(not any(marker in folded for marker in PLACEHOLDER_MARKERS),
             f"{label} masih memakai nilai contoh")


def validate_environment(path: Path) -> tuple[str, ...]:
    _require(path.name != "demo.env.example", "Gunakan salinan demo.env, bukan file contoh")
    _require(path.is_file(), "Berkas environment demo tidak ditemukan")
    if os.name != "nt":
        mode = stat.S_IMODE(path.stat().st_mode)
        _require(mode & 0o077 == 0, "Izin demo.env terlalu luas; gunakan chmod 600")

    values = parse_env_file(path)
    _require(values["APP_ENV"] == "development",
             "Demo dengan login simulasi wajib memakai APP_ENV=development")
    _require(values["LOG_LEVEL"] in {"INFO", "WARNING", "ERROR"},
             "LOG_LEVEL demo tidak boleh DEBUG")
    _require(values["DEV_AUTH_ENABLED"].casefold() == "true",
             "Paket demo saat ini hanya mendukung login simulasi yang aktif")

    try:
        port = int(values["DEMO_HTTP_PORT"])
    except ValueError as exc:
        raise PreflightError("DEMO_HTTP_PORT wajib berupa angka") from exc
    _require(1024 <= port <= 65535, "DEMO_HTTP_PORT harus antara 1024 dan 65535")
    _require(values["DEMO_ORIGIN"] == f"http://127.0.0.1:{port}",
             "DEMO_ORIGIN wajib loopback dan sesuai DEMO_HTTP_PORT")

    database = values["POSTGRES_DB"]
    username = values["POSTGRES_USER"]
    _require(bool(SAFE_NAME.fullmatch(database)), "Nama database demo tidak valid")
    _require(bool(SAFE_NAME.fullmatch(username)), "Nama pengguna database demo tidak valid")
    _require(database.casefold() not in {"postgres", "template0", "template1"},
             "Database sistem tidak boleh dipakai untuk demo")
    _not_placeholder(values["POSTGRES_PASSWORD"], label="POSTGRES_PASSWORD", minimum=24)
    _not_placeholder(values["DEV_AUTH_SECRET"], label="DEV_AUTH_SECRET", minimum=32)
    _require(values["POSTGRES_PASSWORD"] != values["DEV_AUTH_SECRET"],
             "Secret autentikasi dan password database wajib berbeda")

    parsed = urlsplit(values["DATABASE_URL"])
    _require(parsed.scheme in {"postgresql+asyncpg", "postgresql+psycopg"},
             "DATABASE_URL memakai skema yang tidak diizinkan")
    _require(parsed.hostname == "postgres" and parsed.port == 5432,
             "DATABASE_URL wajib menuju service postgres internal")
    _require(unquote(parsed.username or "") == username,
             "Pengguna DATABASE_URL tidak cocok dengan POSTGRES_USER")
    _require(unquote(parsed.password or "") == values["POSTGRES_PASSWORD"],
             "Password DATABASE_URL tidak cocok dengan POSTGRES_PASSWORD")
    _require(parsed.path == f"/{database}",
             "Nama database pada DATABASE_URL tidak cocok dengan POSTGRES_DB")
    _require(not parsed.query and not parsed.fragment,
             "DATABASE_URL demo tidak boleh memuat query atau fragment")

    return (
        "environment_keys_allowlisted",
        "environment_file_private_permissions",
        "development_mode_locked",
        "loopback_origin",
        "database_internal_only",
        "secrets_non_placeholder_and_distinct",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preflight keamanan paket demo privat SUNOVATE")
    parser.add_argument("--env-file", type=Path,
                        help="Validasi tambahan terhadap demo.env yang tidak di-commit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        checks = list(validate_scaffold())
        environment_status = "NOT_CHECKED"
        if args.env_file is not None:
            checks.extend(validate_environment(args.env_file.resolve()))
            environment_status = "PASSED"
    except PreflightError as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}, ensure_ascii=False))
        return 1
    print(
        json.dumps(
            {
                "status": "PASSED",
                "scope": "SIMULATED_DATA_PRIVATE_DEMO",
                "checks": checks,
                "environmentFile": environment_status,
                "containersStarted": False,
                "tunnelActivated": False,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
