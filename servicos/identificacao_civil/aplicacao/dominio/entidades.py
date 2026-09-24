from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum


class Sexo(StrEnum):
    FEMALE = "F"
    MALE = "M"
    OTHER = "OUTRO"


@dataclass(frozen=True, slots=True)
class Cidadao:
    numero_bi: str
    nome_completo: str
    data_nascimento: date
    sexo: Sexo
    nacionalidade: str
    nome_pai: str | None = None
    nome_mae: str | None = None
    residencia: str | None = None
    id: int | None = None
    data_registo: datetime | None = None
    data_actualizacao: datetime | None = None


@dataclass(frozen=True, slots=True)
class EntradaHistoricoCriminal:
    id: int
    numero_processo: str
    tipo_infracao: str
    descricao: str
    tribunal: str
    data_sentenca: date
    pena: str
    estado: str
