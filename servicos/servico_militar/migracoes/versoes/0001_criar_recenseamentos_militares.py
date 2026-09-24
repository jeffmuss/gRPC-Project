"""Criar recenseamentos militares.

Revision ID: 0001
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "recenseamentos_militares",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("numero_bi", sa.String(50), nullable=False),
        sa.Column("numero_recenseamento", sa.String(80), nullable=False),
        sa.Column("data_recenseamento", sa.Date(), nullable=False),
        sa.Column("distrito", sa.String(120), nullable=False),
        sa.Column("posto_recenseamento", sa.String(160), nullable=False),
        sa.Column("ramo", sa.String(80), nullable=False),
        sa.Column("situacao", sa.String(20), nullable=False),
        sa.Column("observacoes", sa.String(500), nullable=True),
        sa.Column("data_registo", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data_actualizacao", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("situacao IN ('RECENSEADO','APTO','INCORPORADO','RESERVA','ISENTO')", name="ck_recenseamentos_militares_situacao"),
    )
    op.create_index("ix_recenseamentos_militares_numero_bi", "recenseamentos_militares", ["numero_bi"], unique=True)
    op.create_index("ix_recenseamentos_militares_numero_recenseamento", "recenseamentos_militares", ["numero_recenseamento"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_recenseamentos_militares_numero_recenseamento", table_name="recenseamentos_militares")
    op.drop_index("ix_recenseamentos_militares_numero_bi", table_name="recenseamentos_militares")
    op.drop_table("recenseamentos_militares")
