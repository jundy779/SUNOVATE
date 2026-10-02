"""Ordering columns: audit_logs.seq (identity) and knowledge_tags.position.

Revision ID: 0002_ordering_columns
Revises: 0001_initial_schema
Create Date: 2026-10-02

Deterministic ordering for the PostgreSQL backend: audit log insert order and knowledge
tag input order. ADD COLUMN does not fire the row-level `audit_logs_append_only` trigger;
the trigger is not changed or disabled.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_ordering_columns"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "audit_logs",
        sa.Column("seq", sa.BigInteger(), sa.Identity(always=True), nullable=False),
    )
    op.create_unique_constraint(op.f("uq_audit_logs_seq"), "audit_logs", ["seq"])
    op.add_column(
        "knowledge_tags",
        sa.Column("position", sa.Integer(), server_default="0", nullable=False),
    )
    op.create_check_constraint(
        op.f("ck_knowledge_tags_position"), "knowledge_tags", "position >= 0"
    )


def downgrade() -> None:
    op.drop_constraint(op.f("ck_knowledge_tags_position"), "knowledge_tags", type_="check")
    op.drop_column("knowledge_tags", "position")
    op.drop_constraint(op.f("uq_audit_logs_seq"), "audit_logs", type_="unique")
    op.drop_column("audit_logs", "seq")
