"""Reject TRUNCATE on audit_logs.

Revision ID: 0004_audit_logs_no_truncate
Revises: 0003_secure_document_readers
Create Date: 2026-10-28

AUD-04: the row trigger from 0001 rejects UPDATE and DELETE but not TRUNCATE, so the audit
trail could still be emptied by the table owner. A statement-level BEFORE TRUNCATE trigger closes
that path. 0001 is not changed. A runtime database role limited to INSERT/SELECT on audit_logs
remains a deployment task (KL-21).
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0004_audit_logs_no_truncate"
down_revision: str | None = "0003_secure_document_readers"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

REJECT_TRUNCATE_FUNCTION = """
CREATE OR REPLACE FUNCTION audit_logs_reject_truncate() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'audit_logs is append-only: TRUNCATE is rejected';
END;
$$ LANGUAGE plpgsql;
"""

NO_TRUNCATE_TRIGGER = """
CREATE TRIGGER audit_logs_no_truncate
BEFORE TRUNCATE ON audit_logs
FOR EACH STATEMENT EXECUTE FUNCTION audit_logs_reject_truncate();
"""


def upgrade() -> None:
    op.execute(REJECT_TRUNCATE_FUNCTION)
    op.execute(NO_TRUNCATE_TRIGGER)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS audit_logs_no_truncate ON audit_logs")
    op.execute("DROP FUNCTION IF EXISTS audit_logs_reject_truncate()")
