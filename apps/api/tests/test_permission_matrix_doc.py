"""The permission matrix document must match the code (implementation-master-plan Tahap 1).

Guards docs/06-security/permission-matrix.md against drift: the permission list, the
role-to-permission matrix, and the endpoint table must cover exactly what the API enforces.
"""

from __future__ import annotations

import re
from pathlib import Path

from sunovate_api.authz.catalog import PERMISSIONS, ROLE_PERMISSIONS
from sunovate_api.testing import make_client

DOC = Path(__file__).resolve().parents[3] / "docs" / "06-security" / "permission-matrix.md"
TEXT = DOC.read_text(encoding="utf-8")


def _section(title: str) -> str:
    return TEXT.split(f"## {title}", 1)[1].split("\n## ", 1)[0]


def _normalize(path: str) -> str:
    return re.sub(r"\{[^}]+\}", "{}", path.split("?")[0])


def test_permission_list_matches_catalog() -> None:
    pattern = r"^\| `([a-z_]+:[a-z_]+)` \|"
    documented = set(re.findall(pattern, _section("Daftar permission"), re.M))
    assert documented == set(PERMISSIONS)


def test_role_matrix_matches_catalog() -> None:
    section = _section("Matriks role ke permission")
    lines = [line for line in section.splitlines() if line.startswith("| ")]
    roles = [cell.strip() for cell in lines[0].split("|")[2:-1]]
    documented: dict[str, set[str]] = {role: set() for role in roles}
    for line in lines[1:]:  # the "|---|" separator row is not matched by "| "
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        for role, value in zip(roles, cells[1:], strict=True):
            if value == "Y":
                documented[role].add(cells[0])
    assert set(roles) == set(ROLE_PERMISSIONS)
    for role in roles:
        assert documented[role] == set(ROLE_PERMISSIONS[role]), role


def test_endpoint_table_covers_every_api_route() -> None:
    documented: set[tuple[str, str]] = set()
    for line in _section("Endpoint ke permission").splitlines():
        if not line.startswith("| ") or "`/" not in line:
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        for method in (m.strip() for m in cells[0].split(",")):
            for path in re.findall(r"`(/[^`]*)`", cells[1]):
                documented.add((method, _normalize(path)))
    paths = make_client().app.openapi()["paths"]
    implemented = {
        (method.upper(), _normalize(path.removeprefix("/api/v1")))
        for path, operations in paths.items()
        for method in operations
    }
    assert implemented - documented == set(), "endpoint belum ada di matriks"
    assert documented - implemented == set(), "matriks memuat endpoint yang tidak ada"
