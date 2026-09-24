from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum


class EstadoRegisto(StrEnum):
    ACTIVE = "ACTIVO"
    SERVED = "CUMPRIDO"
    ARCHIVED = "ARQUIVADO"


@dataclass(frozen=True, slots=True)
class RegistoCriminal:
    numero_bi: str
    numero_processo: str
    tipo_infracao: str
    descricao: str
    tribunal: str
    data_sentenca: date
    pena: str
    estado: EstadoRegisto
    id: int | None = None
    data_registo: datetime | None = None
    data_actualizacao: datetime | None = None


@dataclass(frozen=True, slots=True)
class DadosIdentidade:
    numero_bi: str
    nome_completo: str
    data_nascimento: date
    nacionalidade: str
