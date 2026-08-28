from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "20260829_0001"
down_revision = None
branch_labels = None
depends_on = None

_SQL_DIR = Path(__file__).resolve().parents[1] / "sql"


def _statements(filename: str) -> list[str]:
    text = (_SQL_DIR / filename).read_text(encoding="utf-8")
    # Project.cast is a canonical domain field, while CAST is reserved by PostgreSQL.
    # Quote the identifier without renaming the domain contract.
    text = text.replace("\n    cast jsonb NOT NULL,", '\n    "cast" jsonb NOT NULL,')
    return [statement.strip() for statement in text.split(";\n") if statement.strip()]


def _execute(filename: str) -> None:
    for statement in _statements(filename):
        op.execute(statement)


def upgrade() -> None:
    _execute("0001_core_schema_up.sql")
    # Content.active_version_id is mandatory in the canonical domain. The column is
    # temporarily nullable only while its cyclic ContentVersion FK is installed.
    op.execute("ALTER TABLE core.contents ALTER COLUMN active_version_id SET NOT NULL")


def downgrade() -> None:
    _execute("0001_core_schema_down.sql")
