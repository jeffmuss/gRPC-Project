from __future__ import annotations

from fastapi.testclient import TestClient

from portal.aplicacao.dominio import EstadoServico
from portal.aplicacao.infraestrutura.grpc import (
    ServicoIndisponivel, obter_ligacao_registo_criminal,
    obter_ligacao_identificacao_civil, obter_ligacao_servico_militar,
)
from portal.aplicacao.principal_web import aplicacao


FORMULARIO_VALIDO = {
    "numero_bi": "BI-PORTAL-001",
    "nome_completo": "Cidadao Portal",
    "data_nascimento": "1990-06-12",
    "sexo": "M",
    "nacionalidade": "Ficticia",
    "nome_pai": "Pai Portal",
    "nome_mae": "Mae Portal",
    "residencia": "Endereco ficticio",
}


def test_portal_is_the_single_entry_point(portal_client: TestClient) -> None:
    response = portal_client.get("/")
    assert response.status_code == 200
    assert "Simulação de Plataforma Governamental" in response.text
    assert "Identificação Civil" in response.text
    assert "Registo Criminal" in response.text
    assert "Serviço Militar" in response.text


def test_saude_portal(portal_client: TestClient) -> None:
    response = portal_client.get("/saude")
    assert response.json() == {"servico": "portal", "estado": "operacional"}


def test_identificacao_civil_crud_through_portal(portal_client: TestClient) -> None:
    created = portal_client.post(
        "/identificacao/cidadaos", data=FORMULARIO_VALIDO, follow_redirects=False
    )
    assert created.status_code == 303
    detail_url = created.headers["location"]
    detail = portal_client.get(detail_url)
    assert "Cidadao Portal" in detail.text
    search = portal_client.get(
        "/identificacao/cidadaos/pesquisar", params={"numero_bi": "bi-portal-001"}
    )
    assert search.status_code == 200
    assert "Cidadao Portal" in search.text
    updated = portal_client.post(
        "/identificacao/cidadaos/1",
        data={**FORMULARIO_VALIDO, "residencia": "Nova residencia pelo Portal"},
        follow_redirects=False,
    )
    assert updated.status_code == 303
    assert "Nova residencia pelo Portal" in portal_client.get("/identificacao/cidadaos/1").text


def test_duplicate_bi_is_presented_without_technical_error(portal_client: TestClient) -> None:
    portal_client.post("/identificacao/cidadaos", data=FORMULARIO_VALIDO)
    duplicate = portal_client.post("/identificacao/cidadaos", data=FORMULARIO_VALIDO)
    assert duplicate.status_code == 400
    assert "Ja existe um cidadao" in duplicate.text


def test_registo_criminal_and_servico_militar_are_active(portal_client: TestClient) -> None:
    registo_criminal = portal_client.get("/registo_criminal")
    servico_militar = portal_client.get("/servico_militar")
    assert registo_criminal.status_code == servico_militar.status_code == 200
    assert "Registo e consulta local de antecedentes" in registo_criminal.text
    assert "Histórico de recenseamentos militares" in servico_militar.text


def test_other_modules_remain_visible_when_identificacao_civil_is_down() -> None:
    class OfflineGateway:
        def saude(self):
            raise ServicoIndisponivel("Identificacao indisponivel")

        def fechar(self):
            pass

    class OnlineLigacaoRegistoCriminal:
        def saude(self):
            return EstadoServico("registo_criminal", "Registo Criminal", "operacional", True, "Servico operacional")

    class OnlineLigacaoServicoMilitar:
        def saude(self):
            return EstadoServico("servico_militar", "Serviço Militar", "operacional", True, "Serviço operacional")

    aplicacao.dependency_overrides[obter_ligacao_identificacao_civil] = lambda: OfflineGateway()
    aplicacao.dependency_overrides[obter_ligacao_registo_criminal] = lambda: OnlineLigacaoRegistoCriminal()
    aplicacao.dependency_overrides[obter_ligacao_servico_militar] = lambda: OnlineLigacaoServicoMilitar()
    try:
        with TestClient(aplicacao) as client:
            response = client.get("/")
            assert response.status_code == 200
            assert "Identificacao indisponivel" in response.text
            assert "Registo Criminal" in response.text
            assert "Serviço Militar" in response.text
    finally:
        aplicacao.dependency_overrides.clear()


def test_registo_criminal_keeps_functionalities_visible_when_down() -> None:
    class OnlineLigacaoIdentificacaoCivil:
        def saude(self):
            return EstadoServico("identificacao_civil", "Identificação Civil", "operacional", True, "Serviço operacional")

    class OfflineLigacaoRegistoCriminal:
        def saude(self):
            raise ServicoIndisponivel("Registo Criminal indisponível")

    class OnlineLigacaoServicoMilitar:
        def saude(self):
            return EstadoServico("servico_militar", "Serviço Militar", "operacional", True, "Serviço operacional")

    aplicacao.dependency_overrides[obter_ligacao_identificacao_civil] = lambda: OnlineLigacaoIdentificacaoCivil()
    aplicacao.dependency_overrides[obter_ligacao_registo_criminal] = lambda: OfflineLigacaoRegistoCriminal()
    aplicacao.dependency_overrides[obter_ligacao_servico_militar] = lambda: OnlineLigacaoServicoMilitar()
    try:
        with TestClient(aplicacao) as client:
            response = client.get("/")
            assert response.status_code == 200
            assert "Registar antecedentes criminais" in response.text
            assert "Consultar histórico criminal" in response.text
            assert "Validar identidade do cidadão" in response.text
            assert "etiqueta-grpc" in response.text
            assert "Estado do serviço" not in response.text
    finally:
        aplicacao.dependency_overrides.clear()
