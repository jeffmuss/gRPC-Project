"""Criar tabelas de registos criminais e pedidos de certidao.

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
        "registos_criminais",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("numero_bi", sa.String(length=50), nullable=False),
        sa.Column("numero_processo", sa.String(length=80), nullable=False),
        sa.Column("tipo_infracao", sa.String(length=150), nullable=False),
        sa.Column("descricao", sa.String(length=500), nullable=False),
        sa.Column("tribunal", sa.String(length=200), nullable=False),
        sa.Column("data_sentenca", sa.Date(), nullable=False),
        sa.Column("pena", sa.String(length=300), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("data_registo", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data_actualizacao", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("estado IN ('ACTIVO','CUMPRIDO','ARQUIVADO')", name="ck_registos_criminais_estado"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_registos_criminais_numero_bi", "registos_criminais", ["numero_bi"])
    op.create_index("ix_registos_criminais_numero_processo", "registos_criminais", ["numero_processo"], unique=True)
    op.create_table(
        "pedidos_certidao",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("codigo", sa.String(length=40), nullable=False),
        sa.Column("numero_bi", sa.String(length=50), nullable=False),
        sa.Column("finalidade", sa.String(length=300), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("resultado", sa.String(length=30), nullable=True),
        sa.Column("data_pedido", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data_emissao", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("estado IN ('PENDENTE','EMITIDA')", name="ck_pedidos_certidao_estado"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pedidos_certidao_codigo", "pedidos_certidao", ["codigo"], unique=True)
    op.create_index("ix_pedidos_certidao_numero_bi", "pedidos_certidao", ["numero_bi"])


def downgrade() -> None:
    op.drop_index("ix_pedidos_certidao_numero_bi", table_name="pedidos_certidao")
    op.drop_index("ix_pedidos_certidao_codigo", table_name="pedidos_certidao")
    op.drop_table("pedidos_certidao")
    op.drop_index("ix_registos_criminais_numero_processo", table_name="registos_criminais")
    op.drop_index("ix_registos_criminais_numero_bi", table_name="registos_criminais")
    op.drop_table("registos_criminais")
