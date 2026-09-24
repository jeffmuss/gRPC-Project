from __future__ import annotations

import grpc
import pytest
from datetime import date
from sqlalchemy.orm import Session, sessionmaker

from contratos.execucao import disponibilizar_contratos_gerados
from servicos.identificacao_civil.aplicacao.infraestrutura.grpc import criar_servidor
from servicos.identificacao_civil.aplicacao.dominio import EntradaHistoricoCriminal


disponibilizar_contratos_gerados()
from comum.v1 import comum_pb2  # noqa: E402
from identificacao_civil.v1 import identificacao_civil_pb2, identificacao_civil_pb2_grpc  # noqa: E402


class FakeLigacaoHistoricoCriminal:
    def listar_por_bi(self, numero_bi: str, page: int, page_size: int):
        return [EntradaHistoricoCriminal(
            10, "PROC-INTEROP-001", "Infraccao ficticia", "Descricao ficticia",
            "Tribunal ficticio", date(2025, 2, 1), "Pena ficticia", "ACTIVO"
        )], 1


@pytest.fixture()
def grpc_stub(session_factory: sessionmaker[Session]):
    server, port = criar_servidor("127.0.0.1:0", session_factory, FakeLigacaoHistoricoCriminal())
    server.start()
    channel = grpc.insecure_channel(f"127.0.0.1:{port}")
    try:
        grpc.channel_ready_future(channel).result(timeout=3)
        yield identificacao_civil_pb2_grpc.ServicoIdentificacaoCivilStub(channel)
    finally:
        channel.close()
        server.stop(grace=0).wait()


def context(finalidade: str) -> comum_pb2.ContextoPedido:
    return comum_pb2.ContextoPedido(
        id_pedido="test-request", servico_chamador="portal-test", finalidade=finalidade
    )


def citizen_input(numero_bi: str = "BI-GRPC-001") -> identificacao_civil_pb2.DadosCidadao:
    return identificacao_civil_pb2.DadosCidadao(
        numero_bi=numero_bi,
        nome_completo="Cidadao gRPC",
        data_nascimento="1991-05-10",
        sexo="F",
        nacionalidade="Ficticia",
    )


def test_grpc_health_and_crud(grpc_stub) -> None:
    health = grpc_stub.VerificarSaude(
        identificacao_civil_pb2.PedidoSaude(contexto=context("health"))
    )
    assert health.estado == "operacional"
    created = grpc_stub.RegistarCidadao(
        identificacao_civil_pb2.PedidoRegistarCidadao(
            contexto=context("create"), cidadao=citizen_input()
        )
    )
    found = grpc_stub.ProcurarCidadaoPorBi(
        identificacao_civil_pb2.PedidoProcurarCidadaoPorBi(
            contexto=context("find"), numero_bi="bi-grpc-001"
        )
    )
    assert found.id == created.id
    listed = grpc_stub.ListarCidadaos(
        identificacao_civil_pb2.PedidoListarCidadaos(
            contexto=context("list"), pagina=1, tamanho_pagina=10
        )
    )
    assert listed.total == 1
    updated_input = citizen_input()
    updated_input.residencia = "Residencia via gRPC"
    updated = grpc_stub.ActualizarCidadao(
        identificacao_civil_pb2.PedidoActualizarCidadao(
            contexto=context("update"), cidadao_id=created.id, cidadao=updated_input
        )
    )
    assert updated.residencia == "Residencia via gRPC"


def test_grpc_maps_dominio_errors(grpc_stub) -> None:
    grpc_stub.RegistarCidadao(
        identificacao_civil_pb2.PedidoRegistarCidadao(
            contexto=context("create"), cidadao=citizen_input()
        )
    )
    with pytest.raises(grpc.RpcError) as duplicate:
        grpc_stub.RegistarCidadao(
            identificacao_civil_pb2.PedidoRegistarCidadao(
                contexto=context("duplicate"), cidadao=citizen_input()
            )
        )
    assert duplicate.value.code() == grpc.StatusCode.ALREADY_EXISTS
    with pytest.raises(grpc.RpcError) as missing:
        grpc_stub.ObterCidadao(
            identificacao_civil_pb2.PedidoObterCidadao(
                contexto=context("missing"), cidadao_id=9999
            )
        )
    assert missing.value.code() == grpc.StatusCode.NOT_FOUND


def test_identificacao_civil_consults_registo_historico_criminal_through_gateway(grpc_stub) -> None:
    grpc_stub.RegistarCidadao(
        identificacao_civil_pb2.PedidoRegistarCidadao(
            contexto=context("create"), cidadao=citizen_input("BI-HISTORY-001")
        )
    )
    result = grpc_stub.ObterHistoricoCriminal(
        identificacao_civil_pb2.PedidoHistoricoCriminal(
            contexto=context("history"), numero_bi="BI-HISTORY-001", pagina=1, tamanho_pagina=10
        )
    )
    assert result.total == 1
    assert result.itens[0].numero_processo == "PROC-INTEROP-001"
