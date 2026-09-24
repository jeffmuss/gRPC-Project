from __future__ import annotations

from datetime import datetime
from typing import Protocol

from .entidades import Cidadao, EntradaHistoricoCriminal


class RepositorioCidadaos(Protocol):
    def adicionar(self, cidadao: Cidadao) -> Cidadao: ...

    def obter_por_id(self, cidadao_id: int) -> Cidadao | None: ...

    def obter_por_bi(self, numero_bi: str) -> Cidadao | None: ...

    def listar(self, *, pagina: int, tamanho_pagina: int) -> tuple[list[Cidadao], int]: ...

    def actualizar(self, cidadao: Cidadao) -> Cidadao: ...

    def ultima_actualizacao(self) -> datetime | None: ...


class LigacaoHistoricoCriminal(Protocol):
    def listar_por_bi(
        self, numero_bi: str, pagina: int, tamanho_pagina: int
    ) -> tuple[list[EntradaHistoricoCriminal], int]: ...
