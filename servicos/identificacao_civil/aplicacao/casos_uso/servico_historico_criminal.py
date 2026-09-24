from __future__ import annotations

from .dados_transferencia import PaginaHistoricoCriminal
from ..dominio.excepcoes import CidadaoNaoEncontrado, ErroValidacao
from ..dominio.repositorios import RepositorioCidadaos, LigacaoHistoricoCriminal
from ..dominio.validacao import normalize_bi


class ServicoHistoricoCriminal:
    def __init__(self, cidadaos: RepositorioCidadaos, registo_criminal: LigacaoHistoricoCriminal) -> None:
        self.cidadaos = cidadaos
        self.registo_criminal = registo_criminal

    def consultar(self, numero_bi: str, pagina: int = 1, tamanho_pagina: int = 10) -> PaginaHistoricoCriminal:
        bi = normalize_bi(numero_bi)
        if self.cidadaos.obter_por_bi(bi) is None:
            raise CidadaoNaoEncontrado("Nao foi encontrado um cidadao com o BI indicado.")
        if pagina < 1 or not 1 <= tamanho_pagina <= 100:
            raise ErroValidacao("Paginacao invalida.")
        itens, total = self.registo_criminal.listar_por_bi(
            bi, pagina, tamanho_pagina
        )
        return PaginaHistoricoCriminal(bi, itens, pagina, tamanho_pagina, total)
