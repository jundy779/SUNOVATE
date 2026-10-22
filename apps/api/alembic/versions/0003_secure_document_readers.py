"""Reader grants for RAHASIA documents.

Revision ID: 0003_secure_document_readers
Revises: 0002_ordering_columns
Create Date: 2026-10-21

ADR-020 and DEC-20261021-02: the owning team lead decides who may read a RAHASIA document.
Grants survive restarts; the sealed content itself stays in the vault (no foreign key).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_secure_document_readers"
down_revision: str | None = "0002_ordering_columns"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "secure_document_readers",
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("granted_by", sa.UUID(), nullable=True),
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "data_origin", sa.String(length=32), server_default="SIMULATED_DATA", nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["granted_by"],
            ["users.id"],
            name=op.f("fk_secure_document_readers_granted_by_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_secure_document_readers_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_secure_document_readers")),
        sa.UniqueConstraint(
            "document_id", "user_id", name="uq_secure_document_readers_document_user"
        ),
    )
    op.create_index(
        op.f("ix_secure_document_readers_document_id"),
        "secure_document_readers",
        ["document_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_secure_document_readers_granted_by"),
        "secure_document_readers",
        ["granted_by"],
        unique=False,
    )
    op.create_index(
        op.f("ix_secure_document_readers_user_id"),
        "secure_document_readers",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_secure_document_readers_user_id"), table_name="secure_document_readers")
    op.drop_index(
        op.f("ix_secure_document_readers_granted_by"), table_name="secure_document_readers"
    )
    op.drop_index(
        op.f("ix_secure_document_readers_document_id"), table_name="secure_document_readers"
    )
    op.drop_table("secure_document_readers")
