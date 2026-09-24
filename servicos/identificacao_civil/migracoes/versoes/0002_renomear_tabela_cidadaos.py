"""Renomear a tabela antiga de cidadaos.

Revision ID: 0002
Revises: 0001
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = inspect(op.get_bind())
    if "citizens" not in inspector.get_table_names():
        return
    op.drop_index("ix_citizens_numero_bi", table_name="citizens")
    op.rename_table("citizens", "cidadaos")
    op.create_index("ix_cidadaos_numero_bi", "cidadaos", ["numero_bi"], unique=True)


def downgrade() -> None:
    inspector = inspect(op.get_bind())
    if "cidadaos" not in inspector.get_table_names():
        return
    op.drop_index("ix_cidadaos_numero_bi", table_name="cidadaos")
    op.rename_table("cidadaos", "citizens")
    op.create_index("ix_citizens_numero_bi", "citizens", ["numero_bi"], unique=True)
