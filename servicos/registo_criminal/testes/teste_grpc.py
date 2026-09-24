from __future__ import annotations

import grpc
import pytest

from contratos.execucao import disponibilizar_contratos_gerados
from servicos.registo_criminal.aplicacao.infraestrutura.grpc import criar_servidor

disponibilizar_contratos_gerados()
from comum.v1 import comum_pb2  # noqa: E402
from registo_criminal.v1 import registo_criminal_pb2, registo_criminal_pb2_grpc  # noqa: E402


@pytest.fixture()
def grpc_stub(session_factory, identity_verifier):
    server, port = criar_servidor("127.0.0.1:0", session_factory, identity_verifier)
    server.start()
    channel = grpc.insecure_channel(f"127.0.0.1:{port}")
    try:
        grpc.channel_ready_future(channel).result(timeout=3)
        yield registo_criminal_pb2_grpc.ServicoRegistoCriminalStub(channel)
    finally:
        channel.close()
        server.stop(grace=0).wait()


def context(finalidade: str):
    return comum_pb2.ContextoPedido(id_pedido="registo_criminal-test", servico_chamador="portal-test", finalidade=finalidade)


def record_input(process: str = "PROC-GRPC-001"):
    return registo_criminal_pb2.DadosRegistoCriminal(
        numero_bi="BI-TEST-001", numero_processo=process, tipo_infracao="Teste",
        descricao="Descricao ficticia", tribunal="Tribunal ficticio",
        data_sentenca="2025-01-10", pena="Pena ficticia", estado="ACTIVO")


def test_grpc_local_record_and_identity_validation_flow(grpc_stub) -> None:
    assert grpc_stub.VerificarSaude(registo_criminal_pb2.PedidoSaude(contexto=context("health"))).estado == "operacional"
    created = grpc_stub.CriarRegisto(registo_criminal_pb2.PedidoCriarRegisto(contexto=context("create"), registo=record_input()))
    listed = grpc_stub.ListarRegistos(registo_criminal_pb2.PedidoListarRegistos(contexto=context("list"), pagina=1, tamanho_pagina=10, numero_bi="BI-TEST-001"))
    assert listed.total == 1 and listed.itens[0].id == created.id
    identity = grpc_stub.ValidarIdentidade(registo_criminal_pb2.PedidoValidarIdentidade(
        contexto=context("validate"), numero_bi="BI-TEST-001"))
    assert identity.existe and identity.nome_completo == "Cidadao de Teste"


def test_grpc_maps_duplicate_and_reports_missing_identity(grpc_stub) -> None:
    grpc_stub.CriarRegisto(registo_criminal_pb2.PedidoCriarRegisto(contexto=context("create"), registo=record_input()))
    with pytest.raises(grpc.RpcError) as duplicate:
        grpc_stub.CriarRegisto(registo_criminal_pb2.PedidoCriarRegisto(contexto=context("duplicate"), registo=record_input()))
    assert duplicate.value.code() == grpc.StatusCode.ALREADY_EXISTS
    invalid = record_input("PROC-GRPC-002")
    invalid.numero_bi = "BI-INEXISTENTE"
    assert grpc_stub.CriarRegisto(registo_criminal_pb2.PedidoCriarRegisto(
        contexto=context("local-create"), registo=invalid)).numero_bi == "BI-INEXISTENTE"
    missing = grpc_stub.ValidarIdentidade(registo_criminal_pb2.PedidoValidarIdentidade(
        contexto=context("missing"), numero_bi="BI-INEXISTENTE"))
    assert not missing.existe
