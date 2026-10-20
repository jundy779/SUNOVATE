"""PROPOSED development role and permission catalog.

Source: docs/06-security/permission-matrix.md. Final matrix requires mentor validation.
"""

from __future__ import annotations

PERMISSIONS: dict[str, str] = {
    "user:read": "Melihat daftar pengguna",
    "user:manage": "Mengelola pengguna",
    "team:read": "Melihat tim kerja",
    "team:manage": "Mengelola tim kerja",
    "role:read": "Melihat peran dan kewenangan",
    "role:manage": "Mengelola peran dan kewenangan",
    "knowledge:read": "Membaca pengetahuan sesuai akses",
    "knowledge:create": "Membuat draf pengetahuan",
    "knowledge:update": "Mengubah draf pengetahuan",
    "knowledge:submit": "Mengajukan pemeriksaan pengetahuan",
    "knowledge:review": "Memeriksa pengetahuan",
    "knowledge:publish": "Menyetujui penerbitan pengetahuan",
    "knowledge:archive": "Mengarsipkan pengetahuan",
    "document:read": "Melihat informasi dokumen",
    "document:create": "Mendaftarkan referensi dokumen",
    "document:update": "Mengubah informasi dokumen",
    "document:version": "Mendaftarkan versi dokumen",
    "search:query": "Melakukan pencarian",
    "work:read": "Melihat hasil kerja, tugas, dan tahapan penting",
    "work:create": "Membuat hasil kerja dan tugas",
    "work:update": "Memperbarui hasil kerja dan tugas",
    "pending:read": "Melihat hal yang perlu ditindaklanjuti",
    "pending:manage": "Mengelola hal yang perlu ditindaklanjuti",
    "audit:read": "Melihat riwayat aktivitas",
    "approval:request": "Mengajukan persetujuan",
    "approval:decide": "Memberikan keputusan",
    "hermes:query": "Bertanya kepada SAVI AI",
    "hermes:feedback": "Memberikan penilaian terhadap jawaban SAVI AI",
    "provider:read": "Melihat status layanan pendukung",
    "data_quality:read": "Melihat masalah kualitas data",
    "data_quality:manage": "Mengelola masalah kualitas data",
    "scope:all_teams": "Mengakses seluruh tim sesuai klasifikasi",
}

ROLES: dict[str, tuple[str, str]] = {
    "system_admin": ("Pengelola Sistem", "Mengelola kebutuhan teknis sistem"),
    "knowledge_coordinator": (
        "Koordinator Pengetahuan",
        "Mengelola aliran dan kualitas pengetahuan",
    ),
    "team_lead": ("Ketua Tim", "Memimpin pekerjaan tim kerja"),
    "knowledge_owner": ("Pemilik Pengetahuan", "Memiliki dan memeriksa isi pengetahuan tim"),
    "reviewer": ("Pemeriksa", "Memeriksa pengetahuan dan dokumen"),
    "staff": ("Pelaksana", "Menjalankan pekerjaan tim"),
    "auditor": ("Pemeriksa Kepatuhan", "Melihat riwayat aktivitas dan kepatuhan"),
    "read_only": ("Pembaca", "Hanya membaca"),
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
