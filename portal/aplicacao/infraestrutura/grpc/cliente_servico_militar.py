from __future__ import annotations

from datetime import date, datetime
from uuid import uuid4

import grpc

from contratos.execucao import disponibilizar_contratos_gerados
from ...configuracao.definicoes import definicoes
from ...dominio import (
    DadosRecenseamentoMilitar, EstadoServico, PaginaHistoricoCriminal,
    PaginaRecenseamentosMilitares, RecenseamentoMilitar,
    EntradaHistoricoCriminal, ValidacaoIdentidade,
)
from .cliente_identificacao_civil import ErroOperacaoPortal, ServicoIndisponivel

disponibilizar_contratos_gerados()
from comum.v1 import comum_pb2  # noqa: E402
from servico_militar.v1 import servico_militar_pb2, servico_militar_pb2_grpc  # noqa: E402


def _data_hora(valor: str) -> datetime | None:
    return datetime.fromisoformat(valor) if valor else None


def _item(mensagem) -> RecenseamentoMilitar:
    return RecenseamentoMilitar(
        mensagem.id, mensagem.numero_bi, mensagem.numero_recenseamento,
        date.fromisoformat(mensagem.data_recenseamento), mensagem.distrito,
        mensagem.posto_recenseamento, mensagem.ramo, mensagem.situacao,
        mensagem.observacoes or None, _data_hora(mensagem.data_registo),
        _data_hora(mensagem.data_actualizacao),
    )


def _dados(dados: DadosRecenseamentoMilitar):
    return servico_militar_pb2.DadosRecenseamentoMilitar(
        numero_bi=dados.numero_bi, numero_recenseamento=dados.numero_recenseamento,
        data_recenseamento=dados.data_recenseamento, distrito=dados.distrito,
        posto_recenseamento=dados.posto_recenseamento, ramo=dados.ramo,
        situacao=dados.situacao, observacoes=dados.observacoes,
    )


class LigacaoServicoMilitar:
    def __init__(self, alvo: str, tempo_limite_segundos: float = 3.0) -> None:
        self.alvo = alvo
        self.tempo_limite_segundos = tempo_limite_segundos
        self._ligar()

    def _ligar(self) -> None:
        self.canal = grpc.insecure_channel(self.alvo)
        self.cliente = servico_militar_pb2_grpc.ServicoMilitarStub(self.canal)

    @staticmethod
    def _contexto(finalidade: str):
        return comum_pb2.ContextoPedido(id_pedido=str(uuid4()), servico_chamador="portal", finalidade=finalidade)

    def _chamar(self, metodo, pedido):
        try:
            return metodo(pedido, timeout=self.tempo_limite_segundos)
        except grpc.RpcError as erro:
            detalhes = erro.details() or "Operação remota sem resposta."
            if erro.code() in (grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.DEADLINE_EXCEEDED):
                self.canal.close()
                self._ligar()
                raise ServicoIndisponivel("O Serviço Militar está temporariamente indisponível.") from erro
            if erro.code() in (grpc.StatusCode.ALREADY_EXISTS, grpc.StatusCode.INVALID_ARGUMENT,
                               grpc.StatusCode.NOT_FOUND, grpc.StatusCode.FAILED_PRECONDITION):
                raise ErroOperacaoPortal(detalhes) from erro
            raise ErroOperacaoPortal("Não foi possível concluir a operação.") from erro

    def saude(self) -> EstadoServico:
        resposta = self._chamar(self.cliente.VerificarSaude, servico_militar_pb2.PedidoSaude(contexto=self._contexto("verificar_saude")))
        return EstadoServico("servico_militar", "Serviço Militar", resposta.estado,
                             resposta.estado == "operacional", "Serviço operacional")

    def criar(self, dados: DadosRecenseamentoMilitar) -> RecenseamentoMilitar:
        resposta = self._chamar(self.cliente.CriarRecenseamento,
            servico_militar_pb2.PedidoCriarRecenseamento(contexto=self._contexto("criar_recenseamento"), recenseamento=_dados(dados)))
        return _item(resposta)

    def obter(self, item_id: int) -> RecenseamentoMilitar:
        return _item(self._chamar(self.cliente.ObterRecenseamento,
            servico_militar_pb2.PedidoObterRecenseamento(contexto=self._contexto("obter_recenseamento"), recenseamento_id=item_id)))

    def consultar_situacao(self, numero_bi: str) -> RecenseamentoMilitar:
        return _item(self._chamar(self.cliente.ConsultarSituacao,
            servico_militar_pb2.PedidoConsultarSituacao(contexto=self._contexto("consultar_situacao"), numero_bi=numero_bi)))

    def listar(self, pagina: int = 1, tamanho_pagina: int = 10, numero_bi: str = "") -> PaginaRecenseamentosMilitares:
        resposta = self._chamar(self.cliente.ListarRecenseamentos,
            servico_militar_pb2.PedidoListarRecenseamentos(contexto=self._contexto("listar_recenseamentos"), pagina=pagina, tamanho_pagina=tamanho_pagina, numero_bi=numero_bi))
        return PaginaRecenseamentosMilitares([_item(item) for item in resposta.itens], resposta.pagina,
            resposta.tamanho_pagina, resposta.total, resposta.total_paginas, _data_hora(resposta.ultima_actualizacao))

    def actualizar(self, item_id: int, dados: DadosRecenseamentoMilitar) -> RecenseamentoMilitar:
        resposta = self._chamar(self.cliente.ActualizarRecenseamento,
            servico_militar_pb2.PedidoActualizarRecenseamento(contexto=self._contexto("actualizar_recenseamento"), recenseamento_id=item_id, recenseamento=_dados(dados)))
        return _item(resposta)

    def validar_identidade(self, numero_bi: str) -> ValidacaoIdentidade:
        resposta = self._chamar(self.cliente.ValidarIdentidade,
            servico_militar_pb2.PedidoValidarIdentidade(contexto=self._contexto("validar_identidade"), numero_bi=numero_bi))
        return ValidacaoIdentidade(resposta.existe, resposta.numero_bi, resposta.nome_completo or None,
            date.fromisoformat(resposta.data_nascimento) if resposta.data_nascimento else None, resposta.nacionalidade or None)

    def consultar_antecedentes(self, numero_bi: str, pagina: int = 1, tamanho_pagina: int = 10) -> PaginaHistoricoCriminal:
        resposta = self._chamar(self.cliente.ConsultarAntecedentes,
            servico_militar_pb2.PedidoConsultarAntecedentes(contexto=self._contexto("consultar_antecedentes"), numero_bi=numero_bi, pagina=pagina, tamanho_pagina=tamanho_pagina))
        itens = [EntradaHistoricoCriminal(item.id, item.numero_processo, item.tipo_infracao,
            item.descricao, item.tribunal, date.fromisoformat(item.data_sentenca), item.pena, item.estado) for item in resposta.itens]
        return PaginaHistoricoCriminal(resposta.numero_bi, itens, resposta.pagina, resposta.tamanho_pagina, resposta.total, resposta.total_paginas)

    def fechar(self) -> None:
        self.canal.close()


_ligacao = LigacaoServicoMilitar(definicoes.alvo_grpc_servico_militar, definicoes.tempo_limite_grpc_segundos)


def obter_ligacao_servico_militar() -> LigacaoServicoMilitar:
    return _ligacao
