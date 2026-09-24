from __future__ import annotations

from datetime import date
from uuid import uuid4

import grpc

from contratos.execucao import disponibilizar_contratos_gerados
from ...configuracao.definicoes import definicoes
from ...dominio import AntecedenteCriminal, PaginaAntecedentes, RegistoCriminalIndisponivel

disponibilizar_contratos_gerados()
from comum.v1 import comum_pb2  # noqa: E402
from registo_criminal.v1 import registo_criminal_pb2, registo_criminal_pb2_grpc  # noqa: E402


class GrpcConsultorAntecedentes:
    def __init__(self, alvo: str = definicoes.alvo_grpc_registo_criminal,
                 tempo_limite_segundos: float = definicoes.tempo_limite_grpc_segundos) -> None:
        self.alvo = alvo
        self.tempo_limite_segundos = tempo_limite_segundos
        self._ligar()

    def _ligar(self) -> None:
        self.canal = grpc.insecure_channel(self.alvo)
        self.cliente = registo_criminal_pb2_grpc.ServicoRegistoCriminalStub(self.canal)

    def consultar(self, numero_bi: str, pagina: int, tamanho_pagina: int) -> PaginaAntecedentes:
        pedido = registo_criminal_pb2.PedidoListarRegistos(
            contexto=comum_pb2.ContextoPedido(id_pedido=str(uuid4()), servico_chamador="servico_militar", finalidade="consultar_antecedentes"),
            numero_bi=numero_bi, pagina=pagina, tamanho_pagina=tamanho_pagina,
        )
        try:
            resposta = self.cliente.ListarRegistos(pedido, timeout=self.tempo_limite_segundos)
            itens = [AntecedenteCriminal(
                item.id, item.numero_processo, item.tipo_infracao, item.descricao,
                item.tribunal, date.fromisoformat(item.data_sentenca), item.pena, item.estado,
            ) for item in resposta.itens]
            return PaginaAntecedentes(numero_bi, itens, resposta.pagina, resposta.tamanho_pagina,
                                      resposta.total, resposta.total_paginas)
        except grpc.RpcError as erro:
            self.canal.close()
            self._ligar()
            raise RegistoCriminalIndisponivel("O serviço de Registo Criminal está temporariamente indisponível.") from erro

    def fechar(self) -> None:
        self.canal.close()
