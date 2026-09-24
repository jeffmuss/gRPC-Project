from datetime import date, datetime, timezone
from sqlalchemy import CheckConstraint, Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

def agora_utc() -> datetime: return datetime.now(timezone.utc)

class ModeloRegistoCriminal(Base):
    __tablename__ = "registos_criminais"
    __table_args__ = (CheckConstraint("estado IN ('ACTIVO','CUMPRIDO','ARQUIVADO')", name="ck_registos_criminais_estado"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_bi: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    numero_processo: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    tipo_infracao: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str] = mapped_column(String(500), nullable=False)
    tribunal: Mapped[str] = mapped_column(String(200), nullable=False)
    data_sentenca: Mapped[date] = mapped_column(Date, nullable=False)
    pena: Mapped[str] = mapped_column(String(300), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False)
    data_registo: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc, nullable=False)
    data_actualizacao: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc, onupdate=agora_utc, nullable=False)
