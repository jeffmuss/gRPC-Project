from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Generic, TypeVar

T = TypeVar("T")

@dataclass(frozen=True, slots=True)
class DadosRegisto:
    numero_bi: str; numero_processo: str; tipo_infracao: str; descricao: str
    tribunal: str; data_sentenca: date; pena: str; estado: str

@dataclass(frozen=True, slots=True)
class Pagina(Generic[T]):
    itens: list[T]; pagina: int; tamanho_pagina: int; total: int
    @property
    def total_paginas(self) -> int: return max(1, (self.total + self.tamanho_pagina - 1) // self.tamanho_pagina)
