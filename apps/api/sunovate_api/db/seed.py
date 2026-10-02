"""Seed PostgreSQL with the SIMULATED_DATA dataset (idempotent).

Usage (from apps/api): `uv run --extra dev python -m sunovate_api.db.seed`
Refuses to run when APP_ENV=production.
"""

from __future__ import annotations

import asyncio
import sys
from collections.abc import Iterable, Sequence
from dataclasses import fields
from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncConnection

from ..core.config import Settings, get_settings
from ..store.dataset import Dataset, build_dataset, sid
from . import models as m
from .session import make_engine


def _rows(model: type[m.Base], records: Iterable[object]) -> list[dict[str, Any]]:
    columns = {c.key for c in model.__table__.columns if c.computed is None}
    rows = []
    for record in records:
        values = {
            f.name: getattr(record, f.name)
            for f in fields(record)  # type: ignore[arg-type]
            if f.name in columns
        }
        rows.append(values)
    return rows


async def _insert(
    conn: AsyncConnection, model: type[m.Base], rows: Sequence[dict[str, Any]]
) -> int:
    if not rows:
        return 0
    result = await conn.execute(insert(model).values(list(rows)).on_conflict_do_nothing())
    return int(result.rowcount or 0)


def plan(ds: Dataset) -> list[tuple[type[m.Base], list[dict[str, Any]]]]:
    tag_slugs = sorted({t for entry in ds.knowledge for t in entry.tags})
    tag_rows = [{"id": sid(f"tag:{s}"), "slug": s, "label": s.title()} for s in tag_slugs]
    knowledge_tags = [
        {
            "id": sid(f"ktag:{entry.id}:{t}"),
            "knowledge_entry_id": entry.id,
            "tag_id": sid(f"tag:{t}"),
        }
        for entry in ds.knowledge
        for t in entry.tags
    ]
    role_permissions = [
        {"id": sid(f"rp:{role_id}:{perm_id}"), "role_id": role_id, "permission_id": perm_id}
        for role_id, perm_id in ds.role_permissions
    ]
    return [
        (m.DataClassification, _rows(m.DataClassification, ds.classifications)),
        (m.Team, _rows(m.Team, ds.teams)),
        (m.User, _rows(m.User, ds.users)),
        (m.TeamMembership, _rows(m.TeamMembership, ds.memberships)),
        (m.Role, _rows(m.Role, ds.roles)),
        (m.Permission, _rows(m.Permission, ds.permissions)),
        (m.RolePermission, role_permissions),
        (m.UserRole, _rows(m.UserRole, ds.user_roles)),
        (m.KnowledgeEntry, _rows(m.KnowledgeEntry, ds.knowledge)),
        (m.DocumentReference, _rows(m.DocumentReference, ds.documents)),
        (m.DocumentVersion, _rows(m.DocumentVersion, ds.versions)),
        (m.DocumentChunk, _rows(m.DocumentChunk, ds.chunks)),
        (m.Tag, tag_rows),
        (m.KnowledgeTag, knowledge_tags),
        (m.WorkOutput, _rows(m.WorkOutput, ds.work_outputs)),
        (m.Task, _rows(m.Task, ds.tasks)),
        (m.Milestone, _rows(m.Milestone, ds.milestones)),
        (m.PendingMatter, _rows(m.PendingMatter, ds.pending_matters)),
        (m.FollowUp, _rows(m.FollowUp, ds.follow_ups)),
        (m.ApprovalRequest, _rows(m.ApprovalRequest, ds.approvals)),
        (m.DataQualityIssue, _rows(m.DataQualityIssue, ds.data_quality_issues)),
    ]


async def seed(settings: Settings) -> dict[str, int]:
    if settings.app_env == "production":
        raise SystemExit("Refusing to seed SIMULATED_DATA when APP_ENV=production")
    engine = make_engine(settings.database_url)
    inserted: dict[str, int] = {}
    try:
        async with engine.begin() as conn:
            for model, rows in plan(build_dataset()):
                inserted[model.__tablename__] = await _insert(conn, model, rows)
    finally:
        await engine.dispose()
    return inserted


def main() -> None:
    result = asyncio.run(seed(get_settings()))
    for table, count in result.items():
        sys.stdout.write(f"{table}: {count} inserted (SIMULATED_DATA)\n")


if __name__ == "__main__":
    main()
