from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "20260829_0003"
down_revision = "20260829_0002"
branch_labels = None
depends_on = None

_SQL_DIR = Path(__file__).resolve().parents[1] / "sql"


def _statements(filename: str) -> list[str]:
    text = (_SQL_DIR / filename).read_text(encoding="utf-8")
    return [statement.strip() for statement in text.split(";\n") if statement.strip()]


def _execute(filename: str) -> None:
    for statement in _statements(filename):
        op.execute(statement)


def upgrade() -> None:
    _execute("0003_job_control_up.sql")


def downgrade() -> None:
    _execute("0003_job_control_down.sql")
