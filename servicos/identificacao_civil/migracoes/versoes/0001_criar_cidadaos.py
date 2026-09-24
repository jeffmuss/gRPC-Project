"""Criar tabela de cidadaos.

Revision ID: 0001
Revises:
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
        "cidadaos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("numero_bi", sa.String(length=50), nullable=False),
        sa.Column("nome_completo", sa.String(length=200), nullable=False),
        sa.Column("data_nascimento", sa.Date(), nullable=False),
        sa.Column("sexo", sa.String(length=10), nullable=False),
        sa.Column("nacionalidade", sa.String(length=100), nullable=False),
        sa.Column("nome_pai", sa.String(length=200), nullable=True),
        sa.Column("nome_mae", sa.String(length=200), nullable=True),
        sa.Column("residencia", sa.String(length=300), nullable=True),
        sa.Column("data_registo", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data_actualizacao", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("sexo IN ('F', 'M', 'OUTRO')", name="ck_cidadaos_sexo"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("numero_bi"),
    )
    op.create_index("ix_cidadaos_numero_bi", "cidadaos", ["numero_bi"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_cidadaos_numero_bi", table_name="cidadaos")
    op.drop_table("cidadaos")
