"""Fail-closed preflight for the proposed isolated RAG-Anything pilot.

This script does not import or execute RAG-Anything and does not read file contents.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from importlib import metadata
from pathlib import Path

MINIMUM_VERSION = (1, 4, 2)
BLOCKED_VERSIONS = {"1.4.1"}
ALLOWED_SUFFIXES = {".doc", ".docx", ".md", ".pdf", ".ppt", ".pptx", ".xls", ".xlsx"}


@dataclass(frozen=True)
class PreflightResult:
    ready: bool
    package_version: str | None
    files_checked: int
    errors: tuple[str, ...]


def _version_tuple(value: str) -> tuple[int, ...]:
    parts: list[int] = []
    for part in value.split("."):
        digits = "".join(character for character in part if character.isdigit())
        if not digits:
            break
        parts.append(int(digits))
    return tuple(parts)


def _installed_version() -> str | None:
    for distribution in ("raganything", "rag-anything"):
        try:
            return metadata.version(distribution)
        except metadata.PackageNotFoundError:
            continue
    return None


def check(input_dir: Path, output_dir: Path, *, allow_network: bool = False) -> PreflightResult:
    errors: list[str] = []
    input_path = input_dir.resolve()
    output_path = output_dir.resolve()

    if allow_network:
        errors.append("Jaringan eksternal harus nonaktif pada pilot awal.")
    if not input_dir.exists() or not input_dir.is_dir():
        errors.append("Direktori input pilot tidak tersedia.")
    if input_dir.is_symlink():
        errors.append("Direktori input tidak boleh berupa symlink.")
    if output_dir.exists() and output_dir.is_symlink():
        errors.append("Direktori output tidak boleh berupa symlink.")
    if input_path == output_path:
        errors.append("Direktori input dan output harus berbeda.")
    if input_path.parent != output_path.parent:
        errors.append("Direktori input dan output harus berada di bawah root pilot yang sama.")

    files: list[Path] = []
    if input_dir.exists() and input_dir.is_dir() and not input_dir.is_symlink():
        files = sorted(path for path in input_dir.iterdir() if path.is_file())
        for path in files:
            if path.is_symlink():
                errors.append(f"Symlink ditolak: {path.name}")
            if not path.name.upper().startswith("SIMULASI"):
                errors.append(f"Fixture tanpa label SIMULASI ditolak: {path.name}")
            if path.suffix.lower() not in ALLOWED_SUFFIXES:
                errors.append(f"Format tidak diizinkan: {path.name}")

    version = _installed_version()
    if version is None:
        errors.append("Paket RAG-Anything belum terpasang; preflight integrasi belum lengkap.")
    elif version in BLOCKED_VERSIONS or _version_tuple(version) < MINIMUM_VERSION:
        errors.append(f"Versi RAG-Anything {version} tidak diizinkan; gunakan minimal 1.4.2.")

    return PreflightResult(
        ready=not errors,
        package_version=version,
        files_checked=len(files),
        errors=tuple(errors),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="SUNOVATE RAG-Anything pilot preflight")
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--allow-network", action="store_true")
    args = parser.parse_args()

    result = check(args.input_dir, args.output_dir, allow_network=args.allow_network)
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    return 0 if result.ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
