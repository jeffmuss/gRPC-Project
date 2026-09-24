from __future__ import annotations

from dataclasses import replace

from .dados_transferencia import DadosCidadao, PaginaCidadaos
from ..dominio.entidades import Cidadao
from ..dominio.excepcoes import CidadaoJaExiste, CidadaoNaoEncontrado, ErroValidacao
from ..dominio.repositorios import RepositorioCidadaos
from ..dominio.validacao import (
    MAX_ADDRESS_LENGTH,
    MAX_NAME_LENGTH,
    MAX_SHORT_TEXT_LENGTH,
    normalize_bi,
    optional_text,
    parse_sex,
    required_text,
    validate_birth_date,
)


DUPLICATE_BI_MESSAGE = (
    "Ja existe um cidadao registado com este numero de Bilhete de Identidade."
)


class ServicoCidadaos:
    def __init__(self, repository: RepositorioCidadaos) -> None:
        self.repositorio = repository

    def registar(self, dados: DadosCidadao) -> Cidadao:
        cidadao = self._cidadao_validado(dados)
        if self.repositorio.obter_por_bi(cidadao.numero_bi):
            raise CidadaoJaExiste(DUPLICATE_BI_MESSAGE)
        return self.repositorio.adicionar(cidadao)

    def obter(self, cidadao_id: int) -> Cidadao:
        cidadao = self.repositorio.obter_por_id(cidadao_id)
        if cidadao is None:
            raise CidadaoNaoEncontrado("Cidadao nao encontrado.")
        return cidadao

    def procurar_por_bi(self, numero_bi: str) -> Cidadao:
        citizen = self.repositorio.obter_por_bi(normalize_bi(numero_bi))
        if citizen is None:
            raise CidadaoNaoEncontrado("Nao foi encontrado um cidadao com o BI indicado.")
        return citizen

    def listar(self, pagina: int = 1, tamanho_pagina: int = 10) -> PaginaCidadaos:
        if pagina < 1:
            raise ErroValidacao("A pagina deve ser igual ou superior a 1.")
        if not 1 <= tamanho_pagina <= 100:
            raise ErroValidacao("O tamanho da pagina deve estar entre 1 e 100.")
        itens, total = self.repositorio.listar(
            pagina=pagina, tamanho_pagina=tamanho_pagina
        )
        return PaginaCidadaos(
            itens=itens, pagina=pagina, tamanho_pagina=tamanho_pagina, total=total
        )

    def actualizar(self, cidadao_id: int, dados: DadosCidadao) -> Cidadao:
        actual = self.obter(cidadao_id)
        validado = self._cidadao_validado(dados)
        duplicado = self.repositorio.obter_por_bi(validado.numero_bi)
        if duplicado is not None and duplicado.id != cidadao_id:
            raise CidadaoJaExiste(DUPLICATE_BI_MESSAGE)
        return self.repositorio.actualizar(
            replace(
                validado,
                id=actual.id,
                data_registo=actual.data_registo,
                data_actualizacao=actual.data_actualizacao,
            )
        )

    def _cidadao_validado(self, data: DadosCidadao) -> Cidadao:
        return Cidadao(
            numero_bi=normalize_bi(data.numero_bi),
            nome_completo=required_text(data.nome_completo, "Nome completo", MAX_NAME_LENGTH),
            data_nascimento=validate_birth_date(data.data_nascimento),
            sexo=parse_sex(data.sexo),
            nacionalidade=required_text(
                data.nacionalidade, "Nacionalidade", MAX_SHORT_TEXT_LENGTH
            ),
            nome_pai=optional_text(data.nome_pai, "Nome do pai", MAX_NAME_LENGTH),
            nome_mae=optional_text(data.nome_mae, "Nome da mae", MAX_NAME_LENGTH),
            residencia=optional_text(
                data.residencia, "Residencia", MAX_ADDRESS_LENGTH
            ),
        )
