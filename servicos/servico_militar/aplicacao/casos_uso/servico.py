from __future__ import annotations

from dataclasses import replace

from .dados_transferencia import DadosRecenseamento, Pagina
from ..dominio.entidades import DadosIdentidade, PaginaAntecedentes, RecenseamentoMilitar
from ..dominio.excepcoes import ErroValidacao, JaExiste, NaoEncontrado
from ..dominio.repositorios import ConsultorAntecedentes, RepositorioRecenseamentoMilitar, ValidadorIdentidade
from ..dominio.validacao import normalizar_bi, normalizar_numero, obrigatorio, validar_data, validar_situacao


class ServicoRecenseamentoMilitar:
    def __init__(self, repositorio: RepositorioRecenseamentoMilitar,
                 identidade: ValidadorIdentidade, antecedentes: ConsultorAntecedentes) -> None:
        self.repositorio = repositorio
        self.identidade = identidade
        self.antecedentes = antecedentes

    def _validar(self, dados: DadosRecenseamento) -> RecenseamentoMilitar:
        observacoes = " ".join(dados.observacoes.split()) or None
        if observacoes and len(observacoes) > 500:
            raise ErroValidacao("Observações não podem exceder 500 caracteres.")
        return RecenseamentoMilitar(
            numero_bi=normalizar_bi(dados.numero_bi),
            numero_recenseamento=normalizar_numero(dados.numero_recenseamento),
            data_recenseamento=validar_data(dados.data_recenseamento),
            distrito=obrigatorio(dados.distrito, "Distrito", 120),
            posto_recenseamento=obrigatorio(dados.posto_recenseamento, "Posto de recenseamento", 160),
            ramo=obrigatorio(dados.ramo, "Ramo", 80),
            situacao=validar_situacao(dados.situacao),
            observacoes=observacoes,
        )

    def criar(self, dados: DadosRecenseamento) -> RecenseamentoMilitar:
        item = self._validar(dados)
        if self.repositorio.obter_por_bi(item.numero_bi):
            raise JaExiste("Já existe um recenseamento associado a este BI.")
        if self.repositorio.obter_por_numero(item.numero_recenseamento):
            raise JaExiste("Já existe este número de recenseamento.")
        return self.repositorio.adicionar(item)

    def obter(self, item_id: int) -> RecenseamentoMilitar:
        item = self.repositorio.obter(item_id)
        if not item:
            raise NaoEncontrado("Recenseamento militar não encontrado.")
        return item

    def consultar_situacao(self, numero_bi: str) -> RecenseamentoMilitar:
        item = self.repositorio.obter_por_bi(normalizar_bi(numero_bi))
        if not item:
            raise NaoEncontrado("Não existe recenseamento militar para o BI indicado.")
        return item

    def listar(self, pagina: int = 1, tamanho_pagina: int = 10,
               numero_bi: str | None = None) -> Pagina[RecenseamentoMilitar]:
        if pagina < 1 or not 1 <= tamanho_pagina <= 100:
            raise ErroValidacao("Paginação inválida.")
        bi = normalizar_bi(numero_bi) if numero_bi else None
        itens, total = self.repositorio.listar(pagina, tamanho_pagina, bi)
        return Pagina(itens, pagina, tamanho_pagina, total)

    def actualizar(self, item_id: int, dados: DadosRecenseamento) -> RecenseamentoMilitar:
        actual = self.obter(item_id)
        validado = self._validar(dados)
        por_bi = self.repositorio.obter_por_bi(validado.numero_bi)
        por_numero = self.repositorio.obter_por_numero(validado.numero_recenseamento)
        if por_bi and por_bi.id != item_id:
            raise JaExiste("Já existe um recenseamento associado a este BI.")
        if por_numero and por_numero.id != item_id:
            raise JaExiste("Já existe este número de recenseamento.")
        return self.repositorio.actualizar(replace(
            validado, id=actual.id, data_registo=actual.data_registo,
            data_actualizacao=actual.data_actualizacao,
        ))

    def validar_identidade(self, numero_bi: str) -> DadosIdentidade | None:
        return self.identidade.procurar(normalizar_bi(numero_bi))

    def consultar_antecedentes(self, numero_bi: str, pagina: int = 1,
                               tamanho_pagina: int = 10) -> PaginaAntecedentes:
        if pagina < 1 or not 1 <= tamanho_pagina <= 100:
            raise ErroValidacao("Paginação inválida.")
        bi = normalizar_bi(numero_bi)
        return self.antecedentes.consultar(bi, pagina, tamanho_pagina)
