from __future__ import annotations

from collections.abc import Generator
from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient

from portal.aplicacao.dominio import (
    Cidadao, DadosCidadao, PaginaCidadaos, EntradaHistoricoCriminal, PaginaHistoricoCriminal,
    RegistoCriminal, DadosRegistoCriminal, PaginaRegistosCriminais, ValidacaoIdentidade,
    EstadoServico,
    DadosRecenseamentoMilitar, RecenseamentoMilitar, PaginaRecenseamentosMilitares,
)
from portal.aplicacao.infraestrutura.grpc import (
    ErroOperacaoPortal, obter_ligacao_registo_criminal, obter_ligacao_identificacao_civil,
    obter_ligacao_servico_militar,
)
from portal.aplicacao.principal_web import aplicacao


class FakeLigacaoIdentificacaoCivil:
    def __init__(self) -> None:
        self.itens: dict[int, Cidadao] = {}
        self.proximo_id = 1

    def saude(self) -> EstadoServico:
        return EstadoServico(
            chave="identificacao_civil",
            nome="Identificacao Civil",
            estado="operacional",
            disponivel=True,
            mensagem="Servico operacional",
        )

    def registar(self, data: DadosCidadao) -> Cidadao:
        if any(item.numero_bi == data.numero_bi.upper() for item in self.itens.values()):
            raise ErroOperacaoPortal("Ja existe um cidadao registado com este numero de Bilhete de Identidade.")
        now = datetime.now(timezone.utc)
        cidadao = Cidadao(
            id=self.proximo_id,
            numero_bi=data.numero_bi.upper(),
            nome_completo=data.nome_completo,
            data_nascimento=date.fromisoformat(data.data_nascimento),
            sexo=data.sexo,
            nacionalidade=data.nacionalidade,
            nome_pai=data.nome_pai or None,
            nome_mae=data.nome_mae or None,
            residencia=data.residencia or None,
            data_registo=now,
            data_actualizacao=now,
        )
        self.itens[cidadao.id] = cidadao
        self.proximo_id += 1
        return cidadao

    def obter(self, cidadao_id: int) -> Cidadao:
        try:
            return self.itens[cidadao_id]
        except KeyError as error:
            raise ErroOperacaoPortal("Cidadao nao encontrado.") from error

    def procurar_por_bi(self, numero_bi: str) -> Cidadao:
        for cidadao in self.itens.values():
            if cidadao.numero_bi == numero_bi.upper():
                return cidadao
        raise ErroOperacaoPortal("Nao foi encontrado um cidadao com o BI indicado.")

    def listar(self, pagina: int = 1, tamanho_pagina: int = 10) -> PaginaCidadaos:
        values = sorted(self.itens.values(), key=lambda item: item.nome_completo)
        start = (pagina - 1) * tamanho_pagina
        items = values[start : start + tamanho_pagina]
        total = len(values)
        return PaginaCidadaos(
            itens=items,
            pagina=pagina,
            tamanho_pagina=tamanho_pagina,
            total=total,
            total_paginas=max(1, (total + tamanho_pagina - 1) // tamanho_pagina),
            ultima_actualizacao=max(
                (item.data_actualizacao for item in values), default=None
            ),
        )

    def actualizar(self, cidadao_id: int, data: DadosCidadao) -> Cidadao:
        current = self.obter(cidadao_id)
        updated = Cidadao(
            id=current.id,
            numero_bi=data.numero_bi.upper(),
            nome_completo=data.nome_completo,
            data_nascimento=date.fromisoformat(data.data_nascimento),
            sexo=data.sexo,
            nacionalidade=data.nacionalidade,
            nome_pai=data.nome_pai or None,
            nome_mae=data.nome_mae or None,
            residencia=data.residencia or None,
            data_registo=current.data_registo,
            data_actualizacao=datetime.now(timezone.utc),
        )
        self.itens[cidadao_id] = updated
        return updated

    def historico_criminal(self, numero_bi: str, pagina: int = 1, tamanho_pagina: int = 10) -> PaginaHistoricoCriminal:
        item = EntradaHistoricoCriminal(
            1, "PROC-INTEROP-001", "Infraccao ficticia", "Descricao ficticia",
            "Tribunal ficticio", date(2025, 1, 10), "Pena ficticia", "ACTIVO"
        )
        return PaginaHistoricoCriminal(numero_bi.upper(), [item], pagina, tamanho_pagina, 1, 1)


class FakeLigacaoRegistoCriminal:
    def __init__(self) -> None:
        self.registos: dict[int, RegistoCriminal] = {}

    def saude(self) -> EstadoServico:
        return EstadoServico("registo_criminal", "Registo Criminal", "operacional", True, "Servico operacional")

    def criar_registo(self, data: DadosRegistoCriminal) -> RegistoCriminal:
        now = datetime.now(timezone.utc)
        item = RegistoCriminal(len(self.registos) + 1, data.numero_bi.upper(), data.numero_processo.upper(),
                              data.tipo_infracao, data.descricao, data.tribunal,
                              date.fromisoformat(data.data_sentenca), data.pena, data.estado, now, now)
        self.registos[item.id] = item
        return item

    def obter_registo(self, registo_id: int) -> RegistoCriminal:
        if registo_id not in self.registos:
            raise ErroOperacaoPortal("Registo registo_criminal nao encontrado.")
        return self.registos[registo_id]

    def listar_registos(self, pagina: int = 1, tamanho_pagina: int = 10, numero_bi: str = "") -> PaginaRegistosCriminais:
        values = [item for item in self.registos.values() if not numero_bi or item.numero_bi == numero_bi.upper()]
        start = (pagina - 1) * tamanho_pagina
        return PaginaRegistosCriminais(values[start:start + tamanho_pagina], pagina, tamanho_pagina, len(values),
                                  max(1, (len(values) + tamanho_pagina - 1) // tamanho_pagina),
                                  max((item.data_actualizacao for item in values), default=None))

    def actualizar_registo(self, registo_id: int, data: DadosRegistoCriminal) -> RegistoCriminal:
        current = self.obter_registo(registo_id)
        item = RegistoCriminal(registo_id, data.numero_bi.upper(), data.numero_processo.upper(),
                              data.tipo_infracao, data.descricao, data.tribunal,
                              date.fromisoformat(data.data_sentenca), data.pena, data.estado,
                              current.data_registo, datetime.now(timezone.utc))
        self.registos[registo_id] = item
        return item

    def validar_identidade(self, numero_bi: str) -> ValidacaoIdentidade:
        if numero_bi.upper() != "BI-TEST-001":
            return ValidacaoIdentidade(False, numero_bi.upper(), None, None, None)
        return ValidacaoIdentidade(True, "BI-TEST-001", "Cidadao de Teste",
                                  date(1990, 1, 1), "Ficticia")


class FakeLigacaoServicoMilitar:
    def __init__(self) -> None:
        self.itens: dict[int, RecenseamentoMilitar] = {}

    def saude(self) -> EstadoServico:
        return EstadoServico("servico_militar", "Serviço Militar", "operacional", True, "Serviço operacional")

    def criar(self, dados: DadosRecenseamentoMilitar) -> RecenseamentoMilitar:
        agora = datetime.now(timezone.utc)
        item = RecenseamentoMilitar(len(self.itens) + 1, dados.numero_bi.upper(),
            dados.numero_recenseamento.upper(), date.fromisoformat(dados.data_recenseamento),
            dados.distrito, dados.posto_recenseamento, dados.ramo, dados.situacao,
            dados.observacoes or None, agora, agora)
        self.itens[item.id] = item
        return item

    def obter(self, item_id: int) -> RecenseamentoMilitar:
        if item_id not in self.itens:
            raise ErroOperacaoPortal("Recenseamento militar não encontrado.")
        return self.itens[item_id]

    def consultar_situacao(self, numero_bi: str) -> RecenseamentoMilitar:
        for item in self.itens.values():
            if item.numero_bi == numero_bi.upper():
                return item
        raise ErroOperacaoPortal("Não existe recenseamento militar para o BI indicado.")

    def listar(self, pagina: int = 1, tamanho_pagina: int = 10, numero_bi: str = "") -> PaginaRecenseamentosMilitares:
        itens = [item for item in self.itens.values() if not numero_bi or item.numero_bi == numero_bi.upper()]
        inicio = (pagina - 1) * tamanho_pagina
        return PaginaRecenseamentosMilitares(itens[inicio:inicio + tamanho_pagina], pagina,
            tamanho_pagina, len(itens), max(1, (len(itens) + tamanho_pagina - 1) // tamanho_pagina),
            max((item.data_actualizacao for item in itens), default=None))

    def actualizar(self, item_id: int, dados: DadosRecenseamentoMilitar) -> RecenseamentoMilitar:
        actual = self.obter(item_id)
        item = RecenseamentoMilitar(item_id, dados.numero_bi.upper(), dados.numero_recenseamento.upper(),
            date.fromisoformat(dados.data_recenseamento), dados.distrito, dados.posto_recenseamento,
            dados.ramo, dados.situacao, dados.observacoes or None, actual.data_registo,
            datetime.now(timezone.utc))
        self.itens[item_id] = item
        return item

    def validar_identidade(self, numero_bi: str) -> ValidacaoIdentidade:
        if numero_bi.upper() != "BI-TEST-001":
            return ValidacaoIdentidade(False, numero_bi.upper(), None, None, None)
        return ValidacaoIdentidade(True, "BI-TEST-001", "Cidadao de Teste", date(1990, 1, 1), "Ficticia")

    def consultar_antecedentes(self, numero_bi: str, pagina: int = 1, tamanho_pagina: int = 10) -> PaginaHistoricoCriminal:
        item = EntradaHistoricoCriminal(1, "PROC-MILITAR-001", "Infraccao ficticia",
            "Descricao ficticia", "Tribunal ficticio", date(2025, 1, 10), "Pena ficticia", "ACTIVO")
        return PaginaHistoricoCriminal(numero_bi.upper(), [item], pagina, tamanho_pagina, 1, 1)


@pytest.fixture()
def fake_gateway() -> FakeLigacaoIdentificacaoCivil:
    return FakeLigacaoIdentificacaoCivil()


@pytest.fixture()
def fake_registo_criminal_gateway() -> FakeLigacaoRegistoCriminal:
    return FakeLigacaoRegistoCriminal()


@pytest.fixture()
def fake_servico_militar_gateway() -> FakeLigacaoServicoMilitar:
    return FakeLigacaoServicoMilitar()


@pytest.fixture()
def portal_client(fake_gateway: FakeLigacaoIdentificacaoCivil, fake_registo_criminal_gateway: FakeLigacaoRegistoCriminal,
                  fake_servico_militar_gateway: FakeLigacaoServicoMilitar) -> Generator[TestClient, None, None]:
    aplicacao.dependency_overrides[obter_ligacao_identificacao_civil] = lambda: fake_gateway
    aplicacao.dependency_overrides[obter_ligacao_registo_criminal] = lambda: fake_registo_criminal_gateway
    aplicacao.dependency_overrides[obter_ligacao_servico_militar] = lambda: fake_servico_militar_gateway
    with TestClient(aplicacao) as client:
        yield client
    aplicacao.dependency_overrides.clear()
