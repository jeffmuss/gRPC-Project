from __future__ import annotations

from datetime import date, datetime
from uuid import uuid4

import grpc

from contratos.execucao import disponibilizar_contratos_gerados
from ...configuracao.definicoes import definicoes
from ...dominio import (
    DadosRegistoCriminal,
    EstadoServico,
    PaginaRegistosCriminais,
    RegistoCriminal,
    ValidacaoIdentidade,
)
from .cliente_identificacao_civil import ErroOperacaoPortal, ServicoIndisponivel

disponibilizar_contratos_gerados()
from comum.v1 import comum_pb2  # noqa: E402
from registo_criminal.v1 import registo_criminal_pb2, registo_criminal_pb2_grpc  # noqa: E402


def _data_hora(valor: str) -> datetime | None:
    return datetime.fromisoformat(valor) if valor else None


def _registo(mensagem) -> RegistoCriminal:
    return RegistoCriminal(
        mensagem.id,
        mensagem.numero_bi,
        mensagem.numero_processo,
        mensagem.tipo_infracao,
        mensagem.descricao,
        mensagem.tribunal,
        date.fromisoformat(mensagem.data_sentenca),
        mensagem.pena,
        mensagem.estado,
        _data_hora(mensagem.data_registo),
        _data_hora(mensagem.data_actualizacao),
    )


def _mensagem_dados(dados: DadosRegistoCriminal):
    return registo_criminal_pb2.DadosRegistoCriminal(
        numero_bi=dados.numero_bi,
        numero_processo=dados.numero_processo,
        tipo_infracao=dados.tipo_infracao,
        descricao=dados.descricao,
        tribunal=dados.tribunal,
        data_sentenca=dados.data_sentenca,
        pena=dados.pena,
        estado=dados.estado,
    )


class LigacaoRegistoCriminal:
    def __init__(self, alvo: str, tempo_limite_segundos: float = 3.0) -> None:
        self.alvo = alvo
        self.tempo_limite_segundos = tempo_limite_segundos
        self._ligar()

    def _ligar(self) -> None:
        self.canal = grpc.insecure_channel(self.alvo)
        self.cliente = registo_criminal_pb2_grpc.ServicoRegistoCriminalStub(self.canal)

    @staticmethod
    def _contexto(finalidade: str):
        return comum_pb2.ContextoPedido(
            id_pedido=str(uuid4()), servico_chamador="portal", finalidade=finalidade
        )

    def _chamar(self, metodo, pedido):
        try:
            return metodo(pedido, timeout=self.tempo_limite_segundos)
        except grpc.RpcError as erro:
            detalhes = erro.details() or "Operacao remota sem resposta."
            if erro.code() in (grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.DEADLINE_EXCEEDED):
                self.canal.close()
                self._ligar()
                raise ServicoIndisponivel(
                    "O servico de Registo Criminal esta temporariamente indisponivel."
                ) from erro
            if erro.code() in (
                grpc.StatusCode.ALREADY_EXISTS,
                grpc.StatusCode.INVALID_ARGUMENT,
                grpc.StatusCode.NOT_FOUND,
                grpc.StatusCode.FAILED_PRECONDITION,
            ):
                raise ErroOperacaoPortal(detalhes) from erro
            raise ErroOperacaoPortal("Nao foi possivel concluir a operacao.") from erro

    def saude(self) -> EstadoServico:
        resposta = self._chamar(
            self.cliente.VerificarSaude,
            registo_criminal_pb2.PedidoSaude(contexto=self._contexto("verificar_saude")),
        )
        return EstadoServico(
            "registo_criminal",
            "Registo Criminal",
            resposta.estado,
            resposta.estado == "operacional",
            "Servico operacional",
        )

    def criar_registo(self, dados: DadosRegistoCriminal) -> RegistoCriminal:
        resposta = self._chamar(
            self.cliente.CriarRegisto,
            registo_criminal_pb2.PedidoCriarRegisto(
                contexto=self._contexto("criar_registo_criminal"),
                registo=_mensagem_dados(dados),
            ),
        )
        return _registo(resposta)

    def obter_registo(self, registo_id: int) -> RegistoCriminal:
        resposta = self._chamar(
            self.cliente.ObterRegisto,
            registo_criminal_pb2.PedidoObterRegisto(
                contexto=self._contexto("obter_registo_criminal"), registo_id=registo_id
            ),
        )
        return _registo(resposta)

    def listar_registos(
        self, pagina: int = 1, tamanho_pagina: int = 10, numero_bi: str = ""
    ) -> PaginaRegistosCriminais:
        resposta = self._chamar(
            self.cliente.ListarRegistos,
            registo_criminal_pb2.PedidoListarRegistos(
                contexto=self._contexto("listar_registos_criminais"),
                pagina=pagina,
                tamanho_pagina=tamanho_pagina,
                numero_bi=numero_bi,
            ),
        )
        return PaginaRegistosCriminais(
            [_registo(item) for item in resposta.itens],
            resposta.pagina,
            resposta.tamanho_pagina,
            resposta.total,
            resposta.total_paginas,
            _data_hora(resposta.ultima_actualizacao),
        )

    def actualizar_registo(
        self, registo_id: int, dados: DadosRegistoCriminal
    ) -> RegistoCriminal:
        resposta = self._chamar(
            self.cliente.ActualizarRegisto,
            registo_criminal_pb2.PedidoActualizarRegisto(
                contexto=self._contexto("actualizar_registo_criminal"),
                registo_id=registo_id,
                registo=_mensagem_dados(dados),
            ),
        )
        return _registo(resposta)

    def validar_identidade(self, numero_bi: str) -> ValidacaoIdentidade:
        resposta = self._chamar(
            self.cliente.ValidarIdentidade,
            registo_criminal_pb2.PedidoValidarIdentidade(
                contexto=self._contexto("validar_identidade"), numero_bi=numero_bi
            ),
        )
        return ValidacaoIdentidade(
            existe=resposta.existe,
            numero_bi=resposta.numero_bi,
            nome_completo=resposta.nome_completo or None,
            data_nascimento=(
                date.fromisoformat(resposta.data_nascimento)
                if resposta.data_nascimento
                else None
            ),
            nacionalidade=resposta.nacionalidade or None,
        )

    def fechar(self) -> None:
        self.canal.close()


_ligacao = LigacaoRegistoCriminal(
    definicoes.alvo_grpc_registo_criminal,
    definicoes.tempo_limite_grpc_segundos,
)


def obter_ligacao_registo_criminal() -> LigacaoRegistoCriminal:
    return _ligacao
