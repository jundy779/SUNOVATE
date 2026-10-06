"""Providers (including HermesClient) never reach the database or a data store (AC-08.1)."""

import ast
from dataclasses import fields
from pathlib import Path

import pytest

from sunovate_api.providers import interfaces
from sunovate_api.providers.interfaces import ContextPassage, GenerationRequest

PROVIDERS_DIR = Path(interfaces.__file__).resolve().parent
PACKAGE = "sunovate_api.providers"
FORBIDDEN = (
    "sqlalchemy",
    "sunovate_api.db",
    "sunovate_api.store.postgres",
    "sunovate_api.store.simulated",
)


def _imported_modules(path: Path) -> set[str]:
    """Absolute module names imported by a file; relative imports are resolved."""
    modules: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = ".".join(PACKAGE.split(".")[: len(PACKAGE.split(".")) - node.level + 1])
            else:
                base = ""
            target = ".".join(part for part in (base, node.module or "") if part)
            modules.add(target)
            # `from .. import db` imports a submodule by name.
            modules.update(f"{target}.{alias.name}" for alias in node.names)
    return modules


def _is_forbidden(module: str) -> bool:
    return any(module == f or module.startswith(f"{f}.") for f in FORBIDDEN)


PROVIDER_FILES = sorted(PROVIDERS_DIR.glob("*.py"))


def test_provider_files_are_scanned() -> None:
    names = {p.name for p in PROVIDER_FILES}
    assert {"development.py", "interfaces.py", "registry.py"} <= names


@pytest.mark.parametrize("path", PROVIDER_FILES, ids=lambda p: p.name)
def test_providers_do_not_import_data_access(path: Path) -> None:
    offending = sorted(m for m in _imported_modules(path) if _is_forbidden(m))
    assert offending == []


def test_relative_imports_are_resolved() -> None:
    modules = _imported_modules(PROVIDERS_DIR / "development.py")
    assert "sunovate_api.store.records" in modules  # plain dataclass: allowed
    assert _is_forbidden("sunovate_api.db.session")
    assert _is_forbidden("sqlalchemy.orm")
    assert not _is_forbidden("sunovate_api.store.records")


def test_generation_request_shape_is_unchanged() -> None:
    assert [f.name for f in fields(GenerationRequest)] == ["question", "passages", "query_terms"]
    assert [f.name for f in fields(ContextPassage)] == ["index", "title", "section_label", "text"]
