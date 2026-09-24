from datetime import date, datetime, timezone

from sqlalchemy import CheckConstraint, Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


def agora_utc() -> datetime:
    return datetime.now(timezone.utc)


class ModeloRecenseamentoMilitar(Base):
    __tablename__ = "recenseamentos_militares"
    __table_args__ = (
        CheckConstraint(
            "situacao IN ('RECENSEADO','APTO','INCORPORADO','RESERVA','ISENTO')",
            name="ck_recenseamentos_militares_situacao",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_bi: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    numero_recenseamento: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    data_recenseamento: Mapped[date] = mapped_column(Date, nullable=False)
    distrito: Mapped[str] = mapped_column(String(120), nullable=False)
    posto_recenseamento: Mapped[str] = mapped_column(String(160), nullable=False)
    ramo: Mapped[str] = mapped_column(String(80), nullable=False)
    situacao: Mapped[str] = mapped_column(String(20), nullable=False)
    observacoes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    data_registo: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc, nullable=False)
    data_actualizacao: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc, onupdate=agora_utc, nullable=False)
