"""PROPOSED development role and permission catalog.

Source: docs/06-security/permission-matrix.md. Final matrix requires mentor validation.
"""

from __future__ import annotations

PERMISSIONS: dict[str, str] = {
    "user:read": "Melihat daftar pengguna",
    "user:manage": "Mengelola pengguna",
    "team:read": "Melihat tim kerja",
    "team:manage": "Mengelola tim kerja",
    "role:read": "Melihat role dan permission",
    "role:manage": "Mengelola role dan permission",
    "knowledge:read": "Membaca knowledge sesuai scope",
    "knowledge:create": "Membuat draf knowledge",
    "knowledge:update": "Mengubah draf knowledge",
    "knowledge:submit": "Mengajukan knowledge untuk review",
    "knowledge:review": "Meninjau knowledge",
    "knowledge:publish": "Menyetujui publikasi knowledge",
    "knowledge:archive": "Mengarsipkan knowledge",
    "document:read": "Membaca metadata dokumen",
    "document:create": "Mendaftarkan referensi dokumen",
    "document:update": "Mengubah metadata dokumen",
    "document:version": "Mendaftarkan versi dokumen",
    "search:query": "Melakukan pencarian",
    "work:read": "Melihat output, tugas, milestone",
    "work:create": "Membuat output dan tugas",
    "work:update": "Memperbarui output dan tugas",
    "pending:read": "Melihat pending matters dan tindak lanjut",
    "pending:manage": "Mengelola pending matters",
    "audit:read": "Membaca audit log",
    "approval:request": "Mengajukan approval",
    "approval:decide": "Memutuskan approval",
    "hermes:query": "Bertanya kepada Hermes",
    "hermes:feedback": "Memberi feedback jawaban Hermes",
    "provider:read": "Melihat status provider integrasi",
    "data_quality:read": "Melihat isu kualitas data",
    "data_quality:manage": "Mengelola isu kualitas data",
    "scope:all_teams": "Mengakses record semua tim (tetap tunduk klasifikasi)",
}

ROLES: dict[str, tuple[str, str]] = {
    "system_admin": ("System Administrator", "Administrasi teknis sistem"),
    "knowledge_coordinator": ("Knowledge Coordinator", "Mengelola aliran dan kualitas knowledge"),
    "team_lead": ("Team Lead", "Memimpin pekerjaan tim kerja"),
    "knowledge_owner": ("Knowledge Owner", "Pemilik dan validator isi knowledge tim"),
    "reviewer": ("Reviewer", "Meninjau knowledge dan dokumen"),
    "staff": ("Staff", "Pengguna operasional tim kerja"),
    "auditor": ("Auditor", "Membaca jejak audit dan kepatuhan"),
    "read_only": ("Read Only", "Hanya membaca"),
}

_READ_BASE = {
    "team:read",
    "knowledge:read",
    "document:read",
    "search:query",
    "work:read",
    "pending:read",
}
_AUTHOR = {
    "knowledge:create",
    "knowledge:update",
    "knowledge:submit",
    "document:create",
    "approval:request",
    "hermes:query",
    "hermes:feedback",
}

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "system_admin": frozenset(
        _READ_BASE
        | {
            "user:read",
            "user:manage",
            "team:manage",
            "role:read",
            "role:manage",
            "audit:read",
            "provider:read",
            "data_quality:read",
            "scope:all_teams",
        }
    ),
    "knowledge_coordinator": frozenset(
        _READ_BASE
        | _AUTHOR
        | {
            "user:read",
            "knowledge:review",
            "knowledge:publish",
            "knowledge:archive",
            "document:update",
            "document:version",
            "approval:decide",
            "data_quality:read",
            "data_quality:manage",
            "scope:all_teams",
        }
    ),
    "team_lead": frozenset(
        _READ_BASE
        | _AUTHOR
        | {
            "user:read",
            "knowledge:review",
            "document:update",
            "document:version",
            "work:create",
            "work:update",
            "pending:manage",
            "approval:decide",
        }
    ),
    "knowledge_owner": frozenset(_READ_BASE | _AUTHOR | {"document:update", "document:version"}),
    "reviewer": frozenset(
        _READ_BASE | {"knowledge:review", "approval:decide", "hermes:query", "hermes:feedback"}
    ),
    "staff": frozenset(_READ_BASE | _AUTHOR | {"work:create", "work:update"}),
    "auditor": frozenset(
        _READ_BASE
        | {
            "user:read",
            "role:read",
            "audit:read",
            "provider:read",
            "data_quality:read",
            "scope:all_teams",
        }
    ),
    "read_only": frozenset(_READ_BASE | {"hermes:query", "hermes:feedback"}),
}

assert all(p in PERMISSIONS for perms in ROLE_PERMISSIONS.values() for p in perms)
