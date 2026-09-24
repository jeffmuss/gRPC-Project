"""Renomear a tabela antiga de registos criminais.

Revision ID: 0003
Revises: 0002
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = inspect(op.get_bind())
    if "criminal_records" not in inspector.get_table_names():
        return
    op.drop_index("ix_criminal_records_numero_processo", table_name="criminal_records")
    op.drop_index("ix_criminal_records_numero_bi", table_name="criminal_records")
    op.rename_table("criminal_records", "registos_criminais")
    op.create_index(
        "ix_registos_criminais_numero_processo",
        "registos_criminais",
        ["numero_processo"],
        unique=True,
    )
    op.create_index(
        "ix_registos_criminais_numero_bi", "registos_criminais", ["numero_bi"]
    )


def downgrade() -> None:
    inspector = inspect(op.get_bind())
    if "registos_criminais" not in inspector.get_table_names():
        return
    op.drop_index(
        "ix_registos_criminais_numero_processo", table_name="registos_criminais"
    )
    op.drop_index("ix_registos_criminais_numero_bi", table_name="registos_criminais")
    op.rename_table("registos_criminais", "criminal_records")
    op.create_index(
        "ix_criminal_records_numero_processo",
        "criminal_records",
        ["numero_processo"],
        unique=True,
    )
    op.create_index(
        "ix_criminal_records_numero_bi", "criminal_records", ["numero_bi"]
    )
