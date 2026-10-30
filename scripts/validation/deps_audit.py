"""Check web and Python dependencies against public vulnerability databases.

Runs `pnpm audit` for the workspace and a pinned `pip-audit` for the exported API lockfile, then
prints one content-free summary: package, installed version, advisory ids, and fixed versions.

Exit codes: 0 no known vulnerabilities, 1 vulnerabilities found, 2 BLOCKED (a tool or the
network was unavailable, so the result is unknown). Not part of `pnpm validate`, because the
outcome depends on the network and on advisories published after the code was written.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
API = ROOT / "apps" / "api"
PIP_AUDIT = "pip-audit==2.10.1"  # pinned tool version (released 2026-06-10)
TIMEOUT_SECONDS = 300


class AuditBlocked(RuntimeError):
    """The audit could not run; the dependency state is unknown."""


def _tool(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise AuditBlocked(f"{name} tidak ditemukan di PATH")
    return path


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AuditBlocked(f"{Path(args[0]).name} gagal dijalankan ({type(exc).__name__})") from exc


def parse_pnpm(payload: str) -> list[dict[str, Any]]:
    """Findings from `pnpm audit --json`."""
    try:
        data = json.loads(payload)
    except ValueError as exc:
        message = "Keluaran pnpm audit tidak dapat dibaca (jaringan atau registry)"
        raise AuditBlocked(message) from exc
    if not isinstance(data, dict) or "advisories" not in data:
        raise AuditBlocked("Keluaran pnpm audit tidak berisi daftar advisory")
    findings = []
    for advisory in data["advisories"].values():
        findings.append(
            {
                "ecosystem": "npm",
                "package": advisory.get("module_name"),
                "severity": advisory.get("severity"),
                "advisory": advisory.get("github_advisory_id") or advisory.get("url"),
                "vulnerable": advisory.get("vulnerable_versions"),
                "fixedIn": advisory.get("patched_versions"),
            }
        )
    return findings


def parse_pip_audit(payload: str) -> list[dict[str, Any]]:
    """Findings from `pip-audit --format json`."""
    try:
        data = json.loads(payload)
        dependencies = data["dependencies"]
    except (ValueError, KeyError, TypeError) as exc:
        raise AuditBlocked("Keluaran pip-audit tidak dapat dibaca (jaringan atau PyPI)") from exc
    findings = []
    for dependency in dependencies:
        for vuln in dependency.get("vulns", []):
            findings.append(
                {
                    "ecosystem": "pypi",
                    "package": dependency.get("name"),
                    "installed": dependency.get("version"),
                    "advisory": vuln.get("id"),
                    "fixedIn": ", ".join(vuln.get("fix_versions") or []) or None,
                }
            )
    return findings


def audit_web() -> list[dict[str, Any]]:
    # pnpm exits non-zero when it finds advisories, so the JSON body decides the result.
    result = _run([_tool("pnpm"), "audit", "--json"], ROOT)
    return parse_pnpm(result.stdout)


def audit_python() -> list[dict[str, Any]]:
    uv = _tool("uv")
    exported = _run(
        [uv, "export", "--frozen", "--no-hashes", "--no-emit-project", "--extra", "dev",
         "--format", "requirements-txt"],
        API,
    )
    if exported.returncode != 0 or not exported.stdout.strip():
        raise AuditBlocked("uv export gagal; lockfile API tidak dapat diekspor")
    with tempfile.TemporaryDirectory(prefix="sunovate-deps-") as tmp:
        requirements = Path(tmp) / "requirements.txt"
        requirements.write_text(exported.stdout, encoding="utf-8")
        result = _run(
            # The export is the complete, pinned lockfile, so pip resolution is unnecessary:
            # --no-deps --disable-pip audits exactly the locked versions and skips building a
            # temporary virtualenv (several minutes on Windows).
            [uv, "tool", "run", "--from", PIP_AUDIT, "pip-audit", "-r", str(requirements),
             "--no-deps", "--disable-pip", "--vulnerability-service", "pypi",
             "--progress-spinner", "off", "--format", "json"],
            API,
        )
    return parse_pip_audit(result.stdout)


def main() -> int:
    try:
        findings = audit_web() + audit_python()
    except AuditBlocked as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}, ensure_ascii=False))
        return 2
    report = {
        "status": "VULNERABLE" if findings else "PASSED",
        "findings": len(findings),
        "details": findings,
        "pipAudit": PIP_AUDIT,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
