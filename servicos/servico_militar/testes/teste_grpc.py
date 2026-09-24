from concurrent import futures

import grpc

from contratos.execucao import disponibilizar_contratos_gerados
from servicos.servico_militar.aplicacao.infraestrutura.grpc.servico import ServicoGrpcMilitar

disponibilizar_contratos_gerados()
from comum.v1 import comum_pb2
from servico_militar.v1 import servico_militar_pb2, servico_militar_pb2_grpc


def test_grpc_saude_criacao_situacao_e_interoperabilidade(fabrica_sessoes, identidade_falsa, antecedentes_falsos) -> None:
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    servico_militar_pb2_grpc.add_ServicoMilitarServicer_to_server(
        ServicoGrpcMilitar(fabrica_sessoes, identidade_falsa, antecedentes_falsos), servidor)
    porta = servidor.add_insecure_port("127.0.0.1:0")
    servidor.start()
    canal = grpc.insecure_channel(f"127.0.0.1:{porta}")
    cliente = servico_militar_pb2_grpc.ServicoMilitarStub(canal)
    contexto = comum_pb2.ContextoPedido(id_pedido="teste", servico_chamador="testes", finalidade="teste")
    try:
        assert cliente.VerificarSaude(servico_militar_pb2.PedidoSaude(contexto=contexto)).estado == "operacional"
        criado = cliente.CriarRecenseamento(servico_militar_pb2.PedidoCriarRecenseamento(
            contexto=contexto, recenseamento=servico_militar_pb2.DadosRecenseamentoMilitar(
                numero_bi="BI-TEST-001", numero_recenseamento="RM-GRPC-001",
                data_recenseamento="2026-03-10", distrito="KaMpfumo",
                posto_recenseamento="Posto de Teste", ramo="Exército", situacao="RECENSEADO")))
        assert criado.id == 1
        assert cliente.ConsultarSituacao(servico_militar_pb2.PedidoConsultarSituacao(contexto=contexto, numero_bi="BI-TEST-001")).situacao == "RECENSEADO"
        assert cliente.ValidarIdentidade(servico_militar_pb2.PedidoValidarIdentidade(contexto=contexto, numero_bi="BI-TEST-001")).existe
        assert cliente.ConsultarAntecedentes(servico_militar_pb2.PedidoConsultarAntecedentes(contexto=contexto, numero_bi="BI-TEST-001", pagina=1, tamanho_pagina=10)).total == 1
    finally:
        canal.close()
        servidor.stop(0).wait()
