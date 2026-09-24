from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class DadosRecenseamento:
    numero_bi: str
    numero_recenseamento: str
    data_recenseamento: date
    distrito: str
    posto_recenseamento: str
    ramo: str
    situacao: str
    observacoes: str = ""


@dataclass(frozen=True, slots=True)
class Pagina(Generic[T]):
    itens: list[T]
    pagina: int
    tamanho_pagina: int
    total: int

    @property
    def total_paginas(self) -> int:
        return max(1, (self.total + self.tamanho_pagina - 1) // self.tamanho_pagina)
