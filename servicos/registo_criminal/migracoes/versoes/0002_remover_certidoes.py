"""Remover funcionalidade de certidoes fora do ambito definido.

Revision ID: 0002
Revises: 0001
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_pedidos_certidao_numero_bi", table_name="pedidos_certidao")
    op.drop_index("ix_pedidos_certidao_codigo", table_name="pedidos_certidao")
    op.drop_table("pedidos_certidao")


def downgrade() -> None:
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
