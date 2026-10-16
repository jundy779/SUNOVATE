from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _load_preflight() -> ModuleType:
    path = (
        Path(__file__).parents[3]
        / "scripts"
        / "experiments"
        / "rag_anything"
        / "preflight.py"
    )
    spec = importlib.util.spec_from_file_location("rag_anything_preflight", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_preflight_fails_closed_when_package_is_not_installed(tmp_path: Path) -> None:
    module = _load_preflight()
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "SIMULASI-regulasi.pdf").touch()

    module._installed_version = lambda: None
    result = module.check(input_dir, tmp_path / "output")

    assert result.ready is False
    assert result.files_checked == 1
    assert any("belum terpasang" in error for error in result.errors)


def test_preflight_rejects_unlabelled_fixture_and_blocked_version(tmp_path: Path) -> None:
    module = _load_preflight()
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "dokumen.pdf").touch()

    module._installed_version = lambda: "1.4.1"
    result = module.check(input_dir, tmp_path / "output")

    assert result.ready is False
    assert any("SIMULASI" in error for error in result.errors)
    assert any("1.4.1" in error for error in result.errors)


def test_preflight_accepts_safe_manifest_with_supported_version(tmp_path: Path) -> None:
    module = _load_preflight()
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "SIMULASI-tabel.xlsx").touch()

    module._installed_version = lambda: "1.4.2"
    result = module.check(input_dir, tmp_path / "output")

    assert result.ready is True
    assert result.errors == ()


def test_preflight_rejects_network_and_path_outside_pilot_root(tmp_path: Path) -> None:
    module = _load_preflight()
    input_dir = tmp_path / "pilot-a" / "input"
    input_dir.mkdir(parents=True)
    (input_dir / "SIMULASI-playbook.docx").touch()

    module._installed_version = lambda: "1.4.2"
    result = module.check(input_dir, tmp_path / "pilot-b" / "output", allow_network=True)

    assert result.ready is False
    assert any("Jaringan eksternal" in error for error in result.errors)
    assert any("root pilot yang sama" in error for error in result.errors)
