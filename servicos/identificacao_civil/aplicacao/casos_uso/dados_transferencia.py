from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..dominio.entidades import Cidadao, EntradaHistoricoCriminal, Sexo


@dataclass(frozen=True, slots=True)
class DadosCidadao:
    numero_bi: str
    nome_completo: str
    data_nascimento: date
    sexo: str | Sexo
    nacionalidade: str
    nome_pai: str | None = None
    nome_mae: str | None = None
    residencia: str | None = None


@dataclass(frozen=True, slots=True)
class PaginaCidadaos:
    itens: list[Cidadao]
    pagina: int
    tamanho_pagina: int
    total: int

    @property
    def total_paginas(self) -> int:
        return max(1, (self.total + self.tamanho_pagina - 1) // self.tamanho_pagina)


@dataclass(frozen=True, slots=True)
class PaginaHistoricoCriminal:
    numero_bi: str
    itens: list[EntradaHistoricoCriminal]
    pagina: int
    tamanho_pagina: int
    total: int

    @property
    def total_paginas(self) -> int:
        return max(1, (self.total + self.tamanho_pagina - 1) // self.tamanho_pagina)
