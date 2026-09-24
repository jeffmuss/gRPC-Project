from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True, slots=True)
class DadosCidadao:
    numero_bi: str
    nome_completo: str
    data_nascimento: str
    sexo: str
    nacionalidade: str
    nome_pai: str = ""
    nome_mae: str = ""
    residencia: str = ""


@dataclass(frozen=True, slots=True)
class Cidadao:
    id: int
    numero_bi: str
    nome_completo: str
    data_nascimento: date
    sexo: str
    nacionalidade: str
    nome_pai: str | None
    nome_mae: str | None
    residencia: str | None
    data_registo: datetime | None
    data_actualizacao: datetime | None


@dataclass(frozen=True, slots=True)
class PaginaCidadaos:
    itens: list[Cidadao]
    pagina: int
    tamanho_pagina: int
    total: int
    total_paginas: int
    ultima_actualizacao: datetime | None


@dataclass(frozen=True, slots=True)
class EstadoServico:
    chave: str
    nome: str
    estado: str
    disponivel: bool
    mensagem: str


@dataclass(frozen=True, slots=True)
class DadosRegistoCriminal:
    numero_bi: str
    numero_processo: str
    tipo_infracao: str
    descricao: str
    tribunal: str
    data_sentenca: str
    pena: str
    estado: str


@dataclass(frozen=True, slots=True)
class RegistoCriminal:
    id: int
    numero_bi: str
    numero_processo: str
    tipo_infracao: str
    descricao: str
    tribunal: str
    data_sentenca: date
    pena: str
    estado: str
    data_registo: datetime | None
    data_actualizacao: datetime | None


@dataclass(frozen=True, slots=True)
class PaginaRegistosCriminais:
    itens: list[RegistoCriminal]
    pagina: int
    tamanho_pagina: int
    total: int
    total_paginas: int
    ultima_actualizacao: datetime | None


@dataclass(frozen=True, slots=True)
class ValidacaoIdentidade:
    existe: bool
    numero_bi: str
    nome_completo: str | None
    data_nascimento: date | None
    nacionalidade: str | None


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


@dataclass(frozen=True, slots=True)
class PaginaHistoricoCriminal:
    numero_bi: str
    itens: list[EntradaHistoricoCriminal]
    pagina: int
    tamanho_pagina: int
    total: int
    total_paginas: int


@dataclass(frozen=True, slots=True)
class DadosRecenseamentoMilitar:
    numero_bi: str
    numero_recenseamento: str
    data_recenseamento: str
    distrito: str
    posto_recenseamento: str
    ramo: str
    situacao: str
    observacoes: str = ""


@dataclass(frozen=True, slots=True)
class RecenseamentoMilitar:
    id: int
    numero_bi: str
    numero_recenseamento: str
    data_recenseamento: date
    distrito: str
    posto_recenseamento: str
    ramo: str
    situacao: str
    observacoes: str | None
    data_registo: datetime | None
    data_actualizacao: datetime | None


@dataclass(frozen=True, slots=True)
class PaginaRecenseamentosMilitares:
    itens: list[RecenseamentoMilitar]
    pagina: int
    tamanho_pagina: int
    total: int
    total_paginas: int
    ultima_actualizacao: datetime | None
