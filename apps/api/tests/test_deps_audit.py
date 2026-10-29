"""`pnpm deps:audit` summarises dependency advisories without network access in tests."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "validation" / "deps_audit.py"


def _module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("deps_audit", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AUDIT = _module()

PNPM_SAMPLE = json.dumps(
    {
        "advisories": {
            "1": {
                "module_name": "next",
                "severity": "critical",
                "github_advisory_id": "GHSA-uji-0001",
                "vulnerable_versions": ">=16.0.0 <=16.4.0",
                "patched_versions": ">=16.4.1",
            }
        },
        "metadata": {"vulnerabilities": {"critical": 1}},
    }
)
PIP_SAMPLE = json.dumps(
    {
        "dependencies": [
            {
                "name": "pypdf",
                "version": "6.20.1",
                "vulns": [{"id": "CVE-UJI-1", "fix_versions": ["6.21.0"]}],
            },
            {"name": "alembic", "version": "1.20.0", "vulns": []},
        ],
        "fixes": [],
    }
)


def test_parsers_report_package_version_advisory_and_fix() -> None:
    web = AUDIT.parse_pnpm(PNPM_SAMPLE)
    assert web == [
        {
            "ecosystem": "npm",
            "package": "next",
            "severity": "critical",
            "advisory": "GHSA-uji-0001",
            "vulnerable": ">=16.0.0 <=16.4.0",
            "fixedIn": ">=16.4.1",
        }
    ]
    python = AUDIT.parse_pip_audit(PIP_SAMPLE)
    assert python == [
        {"ecosystem": "pypi", "package": "pypdf", "installed": "6.20.1",
         "advisory": "CVE-UJI-1", "fixedIn": "6.21.0"}
    ]


@pytest.mark.parametrize("payload", ["", "bukan json", json.dumps({"error": "offline"})])
def test_unreadable_output_is_blocked_not_passed(payload: str) -> None:
    with pytest.raises(AUDIT.AuditBlocked):
        AUDIT.parse_pnpm(payload)
    with pytest.raises(AUDIT.AuditBlocked):
        AUDIT.parse_pip_audit(payload)


def test_exit_codes(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(AUDIT, "audit_web", lambda: [])
    monkeypatch.setattr(AUDIT, "audit_python", lambda: [])
    assert AUDIT.main() == 0
    assert json.loads(capsys.readouterr().out)["status"] == "PASSED"

    monkeypatch.setattr(AUDIT, "audit_python", lambda: AUDIT.parse_pip_audit(PIP_SAMPLE))
    assert AUDIT.main() == 1
    assert json.loads(capsys.readouterr().out)["status"] == "VULNERABLE"

    def missing() -> list[dict[str, object]]:
        raise AUDIT.AuditBlocked("pnpm tidak ditemukan di PATH")

    monkeypatch.setattr(AUDIT, "audit_web", missing)
    assert AUDIT.main() == 2
    assert json.loads(capsys.readouterr().out)["status"] == "BLOCKED"


def test_missing_tool_is_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(AUDIT.shutil, "which", lambda name: None)
    with pytest.raises(AUDIT.AuditBlocked):
        AUDIT.audit_web()
