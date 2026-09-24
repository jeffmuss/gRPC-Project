from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum


class SituacaoMilitar(StrEnum):
    RECENSEADO = "RECENSEADO"
    APTO = "APTO"
    INCORPORADO = "INCORPORADO"
    RESERVA = "RESERVA"
    ISENTO = "ISENTO"


@dataclass(frozen=True, slots=True)
class RecenseamentoMilitar:
    numero_bi: str
    numero_recenseamento: str
    data_recenseamento: date
    distrito: str
    posto_recenseamento: str
    ramo: str
    situacao: SituacaoMilitar
    observacoes: str | None = None
    id: int | None = None
    data_registo: datetime | None = None
    data_actualizacao: datetime | None = None


@dataclass(frozen=True, slots=True)
class DadosIdentidade:
    numero_bi: str
    nome_completo: str
    data_nascimento: date
    nacionalidade: str


@dataclass(frozen=True, slots=True)
class AntecedenteCriminal:
    id: int
    numero_processo: str
    tipo_infracao: str
    descricao: str
    tribunal: str
    data_sentenca: date
    pena: str
    estado: str


@dataclass(frozen=True, slots=True)
class PaginaAntecedentes:
    numero_bi: str
    itens: list[AntecedenteCriminal]
    pagina: int
    tamanho_pagina: int
    total: int
    total_paginas: int
