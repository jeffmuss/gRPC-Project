from __future__ import annotations

from datetime import date
from uuid import uuid4

import grpc

from contratos.execucao import disponibilizar_contratos_gerados
from ...configuracao.definicoes import definicoes
from ...dominio import DadosIdentidade, IdentificacaoIndisponivel

disponibilizar_contratos_gerados()
from comum.v1 import comum_pb2  # noqa: E402
from identificacao_civil.v1 import identificacao_civil_pb2, identificacao_civil_pb2_grpc  # noqa: E402


class GrpcValidadorIdentidade:
    def __init__(self, alvo: str = definicoes.alvo_grpc_identificacao_civil,
                 tempo_limite_segundos: float = definicoes.tempo_limite_grpc_segundos) -> None:
        self.alvo = alvo
        self.tempo_limite_segundos = tempo_limite_segundos
        self._ligar()

    def _ligar(self) -> None:
        self.canal = grpc.insecure_channel(self.alvo)
        self.cliente = identificacao_civil_pb2_grpc.ServicoIdentificacaoCivilStub(self.canal)

    def procurar(self, numero_bi: str) -> DadosIdentidade | None:
        pedido = identificacao_civil_pb2.PedidoProcurarCidadaoPorBi(
            contexto=comum_pb2.ContextoPedido(id_pedido=str(uuid4()), servico_chamador="servico_militar", finalidade="validar_identidade"),
            numero_bi=numero_bi,
        )
        try:
            resposta = self.cliente.ProcurarCidadaoPorBi(pedido, timeout=self.tempo_limite_segundos)
            return DadosIdentidade(resposta.numero_bi, resposta.nome_completo,
                                   date.fromisoformat(resposta.data_nascimento), resposta.nacionalidade)
        except grpc.RpcError as erro:
            if erro.code() == grpc.StatusCode.NOT_FOUND:
                return None
            self.canal.close()
            self._ligar()
            raise IdentificacaoIndisponivel("O serviço de Identificação Civil está temporariamente indisponível.") from erro

    def fechar(self) -> None:
        self.canal.close()
