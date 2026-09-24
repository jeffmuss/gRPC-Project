from __future__ import annotations

from datetime import date, datetime
from uuid import uuid4

import grpc

from contratos.execucao import disponibilizar_contratos_gerados
from ...configuracao.definicoes import definicoes
from ...dominio import (
    Cidadao,
    DadosCidadao,
    EntradaHistoricoCriminal,
    EstadoServico,
    PaginaCidadaos,
    PaginaHistoricoCriminal,
)

disponibilizar_contratos_gerados()
from comum.v1 import comum_pb2  # noqa: E402
from identificacao_civil.v1 import identificacao_civil_pb2, identificacao_civil_pb2_grpc  # noqa: E402


class ErroOperacaoPortal(Exception):
    pass


class ServicoIndisponivel(ErroOperacaoPortal):
    pass


def _data_hora_opcional(valor: str) -> datetime | None:
    return datetime.fromisoformat(valor) if valor else None


def _cidadao(mensagem: identificacao_civil_pb2.Cidadao) -> Cidadao:
    return Cidadao(
        id=mensagem.id,
        numero_bi=mensagem.numero_bi,
        nome_completo=mensagem.nome_completo,
        data_nascimento=date.fromisoformat(mensagem.data_nascimento),
        sexo=mensagem.sexo,
        nacionalidade=mensagem.nacionalidade,
        nome_pai=mensagem.nome_pai or None,
        nome_mae=mensagem.nome_mae or None,
        residencia=mensagem.residencia or None,
        data_registo=_data_hora_opcional(mensagem.data_registo),
        data_actualizacao=_data_hora_opcional(mensagem.data_actualizacao),
    )


def _mensagem_dados(dados: DadosCidadao) -> identificacao_civil_pb2.DadosCidadao:
    return identificacao_civil_pb2.DadosCidadao(
        numero_bi=dados.numero_bi,
        nome_completo=dados.nome_completo,
        data_nascimento=dados.data_nascimento,
        sexo=dados.sexo,
        nacionalidade=dados.nacionalidade,
        nome_pai=dados.nome_pai,
        nome_mae=dados.nome_mae,
        residencia=dados.residencia,
    )


class LigacaoIdentificacaoCivil:
    def __init__(self, alvo: str, tempo_limite_segundos: float = 3.0) -> None:
        self.alvo = alvo
        self.tempo_limite_segundos = tempo_limite_segundos
        self.canal = grpc.insecure_channel(alvo)
        self.cliente = identificacao_civil_pb2_grpc.ServicoIdentificacaoCivilStub(self.canal)

    @staticmethod
    def _contexto(finalidade: str) -> comum_pb2.ContextoPedido:
        return comum_pb2.ContextoPedido(
            id_pedido=str(uuid4()), servico_chamador="portal", finalidade=finalidade
        )

    def _chamar(self, metodo, pedido):
        try:
            return metodo(pedido, timeout=self.tempo_limite_segundos)
        except grpc.RpcError as erro:
            codigo = erro.code()
            detalhes = erro.details() or "Operacao remota sem resposta."
            if codigo in (grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.DEADLINE_EXCEEDED):
                if "Registo Criminal" in detalhes:
                    raise ServicoIndisponivel(detalhes) from erro
                raise ServicoIndisponivel(
                    "O servico de Identificacao Civil esta temporariamente indisponivel."
                ) from erro
            if codigo in (
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
            identificacao_civil_pb2.PedidoSaude(contexto=self._contexto("verificar_saude")),
        )
        return EstadoServico(
            chave="identificacao_civil",
            nome="Identificacao Civil",
            estado=resposta.estado,
            disponivel=resposta.estado == "operacional",
            mensagem="Servico operacional" if resposta.estado == "operacional" else resposta.estado,
        )

    def registar(self, dados: DadosCidadao) -> Cidadao:
        resposta = self._chamar(
            self.cliente.RegistarCidadao,
            identificacao_civil_pb2.PedidoRegistarCidadao(
                contexto=self._contexto("registar_cidadao"), cidadao=_mensagem_dados(dados)
            ),
        )
        return _cidadao(resposta)

    def obter(self, cidadao_id: int) -> Cidadao:
        resposta = self._chamar(
            self.cliente.ObterCidadao,
            identificacao_civil_pb2.PedidoObterCidadao(
                contexto=self._contexto("obter_cidadao"), cidadao_id=cidadao_id
            ),
        )
        return _cidadao(resposta)

    def procurar_por_bi(self, numero_bi: str) -> Cidadao:
        resposta = self._chamar(
            self.cliente.ProcurarCidadaoPorBi,
            identificacao_civil_pb2.PedidoProcurarCidadaoPorBi(
                contexto=self._contexto("procurar_cidadao_por_bi"), numero_bi=numero_bi
            ),
        )
        return _cidadao(resposta)

    def listar(self, pagina: int = 1, tamanho_pagina: int = 10) -> PaginaCidadaos:
        resposta = self._chamar(
            self.cliente.ListarCidadaos,
            identificacao_civil_pb2.PedidoListarCidadaos(
                contexto=self._contexto("listar_cidadaos"),
                pagina=pagina,
                tamanho_pagina=tamanho_pagina,
            ),
        )
        return PaginaCidadaos(
            itens=[_cidadao(item) for item in resposta.itens],
            pagina=resposta.pagina,
            tamanho_pagina=resposta.tamanho_pagina,
            total=resposta.total,
            total_paginas=resposta.total_paginas,
            ultima_actualizacao=_data_hora_opcional(resposta.ultima_actualizacao),
        )

    def actualizar(self, cidadao_id: int, dados: DadosCidadao) -> Cidadao:
        resposta = self._chamar(
            self.cliente.ActualizarCidadao,
            identificacao_civil_pb2.PedidoActualizarCidadao(
                contexto=self._contexto("actualizar_cidadao"),
                cidadao_id=cidadao_id,
                cidadao=_mensagem_dados(dados),
            ),
        )
        return _cidadao(resposta)

    def historico_criminal(
        self, numero_bi: str, pagina: int = 1, tamanho_pagina: int = 10
    ) -> PaginaHistoricoCriminal:
        resposta = self._chamar(
            self.cliente.ObterHistoricoCriminal,
            identificacao_civil_pb2.PedidoHistoricoCriminal(
                contexto=self._contexto("consultar_historico_criminal"),
                numero_bi=numero_bi,
                pagina=pagina,
                tamanho_pagina=tamanho_pagina,
            ),
        )
        return PaginaHistoricoCriminal(
            numero_bi=resposta.numero_bi,
            itens=[
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
            ],
            pagina=resposta.pagina,
            tamanho_pagina=resposta.tamanho_pagina,
            total=resposta.total,
            total_paginas=resposta.total_paginas,
        )

    def fechar(self) -> None:
        self.canal.close()


_ligacao = LigacaoIdentificacaoCivil(
    definicoes.alvo_grpc_identificacao_civil,
    definicoes.tempo_limite_grpc_segundos,
)


def obter_ligacao_identificacao_civil() -> LigacaoIdentificacaoCivil:
    return _ligacao
