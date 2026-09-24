from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import CheckConstraint, Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


def agora_utc() -> datetime:
    return datetime.now(timezone.utc)


class ModeloCidadao(Base):
    __tablename__ = "cidadaos"
    __table_args__ = (
        CheckConstraint("sexo IN ('F', 'M', 'OUTRO')", name="ck_cidadaos_sexo"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_bi: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    nome_completo: Mapped[str] = mapped_column(String(200), nullable=False)
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    sexo: Mapped[str] = mapped_column(String(10), nullable=False)
    nacionalidade: Mapped[str] = mapped_column(String(100), nullable=False)
    nome_pai: Mapped[str | None] = mapped_column(String(200), nullable=True)
    nome_mae: Mapped[str | None] = mapped_column(String(200), nullable=True)
    residencia: Mapped[str | None] = mapped_column(String(300), nullable=True)
    data_registo: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=agora_utc, nullable=False
    )
    data_actualizacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=agora_utc, onupdate=agora_utc, nullable=False
    )
