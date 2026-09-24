from __future__ import annotations

from datetime import date
from uuid import uuid4

import grpc

from contratos.execucao import disponibilizar_contratos_gerados
from ...configuracao.definicoes import definicoes
from ...dominio.entidades import EntradaHistoricoCriminal
from ...dominio.excepcoes import HistoricoCriminalIndisponivel

disponibilizar_contratos_gerados()
from comum.v1 import comum_pb2  # noqa: E402
from registo_criminal.v1 import registo_criminal_pb2, registo_criminal_pb2_grpc  # noqa: E402


class GrpcLigacaoHistoricoCriminal:
    def __init__(self, alvo: str = definicoes.alvo_grpc_registo_criminal,
                 tempo_limite_segundos: float = definicoes.tempo_limite_grpc_segundos) -> None:
        self.alvo = alvo
        self.tempo_limite_segundos = tempo_limite_segundos
        self._ligar()

    def _ligar(self) -> None:
        self.canal = grpc.insecure_channel(self.alvo)
        self.cliente = registo_criminal_pb2_grpc.ServicoRegistoCriminalStub(self.canal)

    def listar_por_bi(self, numero_bi: str, pagina: int, tamanho_pagina: int) -> tuple[list[EntradaHistoricoCriminal], int]:
        pedido = registo_criminal_pb2.PedidoListarRegistos(
            contexto=comum_pb2.ContextoPedido(
                id_pedido=str(uuid4()), servico_chamador="identificacao_civil",
                finalidade="consultar_historico_criminal"
            ),
            numero_bi=numero_bi,
            pagina=pagina,
            tamanho_pagina=tamanho_pagina,
        )
        try:
            resposta = self.cliente.ListarRegistos(pedido, timeout=self.tempo_limite_segundos)
        except grpc.RpcError as erro:
            self.canal.close()
            self._ligar()
            raise HistoricoCriminalIndisponivel(
                "O servico de Registo Criminal esta temporariamente indisponivel."
            ) from erro
        return [
            EntradaHistoricoCriminal(
                id=item.id,
                numero_processo=item.numero_processo,
                tipo_infracao=item.tipo_infracao,
                descricao=item.descricao,
                tribunal=item.tribunal,
                data_sentenca=date.fromisoformat(item.data_sentenca),
                pena=item.pena,
                estado=item.estado,
            )
            for item in resposta.itens
        ], resposta.total

    def fechar(self) -> None:
        self.canal.close()
