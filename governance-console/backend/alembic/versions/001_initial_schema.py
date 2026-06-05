"""Initial schema bootstrap (parity with db/bootstrap init_schema).

Revision ID: 001_initial
Revises:
Create Date: 2026-06-04

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect

from db.models import Base

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    for table in reversed(Base.metadata.sorted_tables):
        if inspect(bind).has_table(table.name):
            op.drop_table(table.name)
