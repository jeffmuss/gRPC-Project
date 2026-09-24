from __future__ import annotations

import logging
from concurrent import futures
from datetime import date

import grpc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from contratos.execucao import disponibilizar_contratos_gerados
from ...casos_uso import DadosRecenseamento, ServicoRecenseamentoMilitar
from ...dominio import (
    ErroValidacao, IdentificacaoIndisponivel, JaExiste, NaoEncontrado,
    RecenseamentoMilitar, RegistoCriminalIndisponivel,
)
from ..base_dados import SessaoLocal, SqlAlchemyRepositorioRecenseamentoMilitar
from .cliente_identificacao_civil import GrpcValidadorIdentidade
from .cliente_registo_criminal import GrpcConsultorAntecedentes

disponibilizar_contratos_gerados()
from servico_militar.v1 import servico_militar_pb2, servico_militar_pb2_grpc  # noqa: E402

logger = logging.getLogger(__name__)


def _mensagem_item(item: RecenseamentoMilitar):
    return servico_militar_pb2.RecenseamentoMilitar(
        id=item.id or 0, numero_bi=item.numero_bi,
        numero_recenseamento=item.numero_recenseamento,
        data_recenseamento=item.data_recenseamento.isoformat(), distrito=item.distrito,
        posto_recenseamento=item.posto_recenseamento, ramo=item.ramo,
        situacao=item.situacao.value, observacoes=item.observacoes or "",
        data_registo=item.data_registo.isoformat() if item.data_registo else "",
        data_actualizacao=item.data_actualizacao.isoformat() if item.data_actualizacao else "",
    )


def _dados(mensagem) -> DadosRecenseamento:
    try:
        data_recenseamento = date.fromisoformat(mensagem.data_recenseamento)
    except ValueError as erro:
        raise ErroValidacao("Introduza uma data de recenseamento válida.") from erro
    return DadosRecenseamento(
        mensagem.numero_bi, mensagem.numero_recenseamento, data_recenseamento,
        mensagem.distrito, mensagem.posto_recenseamento, mensagem.ramo,
        mensagem.situacao, mensagem.observacoes,
    )


class ServicoGrpcMilitar(servico_militar_pb2_grpc.ServicoMilitarServicer):
    def __init__(self, fabrica_sessoes: sessionmaker[Session] = SessaoLocal,
                 validador_identidade=None, consultor_antecedentes=None) -> None:
        self.fabrica_sessoes = fabrica_sessoes
        self.validador_identidade = validador_identidade or GrpcValidadorIdentidade()
        self.consultor_antecedentes = consultor_antecedentes or GrpcConsultorAntecedentes()

    def _executar(self, operacao, contexto):
        try:
            with self.fabrica_sessoes() as sessao:
                servico = ServicoRecenseamentoMilitar(
                    SqlAlchemyRepositorioRecenseamentoMilitar(sessao),
                    self.validador_identidade, self.consultor_antecedentes,
                )
                return operacao(servico, sessao)
        except JaExiste as erro:
            contexto.abort(grpc.StatusCode.ALREADY_EXISTS, str(erro))
        except NaoEncontrado as erro:
            contexto.abort(grpc.StatusCode.NOT_FOUND, str(erro))
        except ErroValidacao as erro:
            contexto.abort(grpc.StatusCode.INVALID_ARGUMENT, str(erro))
        except (IdentificacaoIndisponivel, RegistoCriminalIndisponivel) as erro:
            contexto.abort(grpc.StatusCode.UNAVAILABLE, str(erro))
        except SQLAlchemyError:
            logger.exception("Falha de persistência no Serviço Militar")
            contexto.abort(grpc.StatusCode.INTERNAL, "Falha interna ao aceder aos dados.")

    def VerificarSaude(self, pedido, contexto):
        return servico_militar_pb2.RespostaSaude(servico="servico_militar", estado="operacional")

    def CriarRecenseamento(self, pedido, contexto):
        return self._executar(lambda servico, _: _mensagem_item(servico.criar(_dados(pedido.recenseamento))), contexto)

    def ObterRecenseamento(self, pedido, contexto):
        return self._executar(lambda servico, _: _mensagem_item(servico.obter(pedido.recenseamento_id)), contexto)

    def ConsultarSituacao(self, pedido, contexto):
        return self._executar(lambda servico, _: _mensagem_item(servico.consultar_situacao(pedido.numero_bi)), contexto)

    def ListarRecenseamentos(self, pedido, contexto):
        def operacao(servico, sessao):
            pagina = servico.listar(pedido.pagina or 1, pedido.tamanho_pagina or 10, pedido.numero_bi or None)
            actualizacao = SqlAlchemyRepositorioRecenseamentoMilitar(sessao).ultima_actualizacao()
            return servico_militar_pb2.RespostaListarRecenseamentos(
                itens=[_mensagem_item(item) for item in pagina.itens], pagina=pagina.pagina,
                tamanho_pagina=pagina.tamanho_pagina, total=pagina.total,
                total_paginas=pagina.total_paginas,
                ultima_actualizacao=actualizacao.isoformat() if actualizacao else "",
            )
        return self._executar(operacao, contexto)

    def ActualizarRecenseamento(self, pedido, contexto):
        return self._executar(lambda servico, _: _mensagem_item(servico.actualizar(pedido.recenseamento_id, _dados(pedido.recenseamento))), contexto)

    def ValidarIdentidade(self, pedido, contexto):
        def operacao(servico, _):
            identidade = servico.validar_identidade(pedido.numero_bi)
            if identidade is None:
                return servico_militar_pb2.ValidacaoIdentidade(existe=False, numero_bi=pedido.numero_bi.upper())
            return servico_militar_pb2.ValidacaoIdentidade(
                existe=True, numero_bi=identidade.numero_bi,
                nome_completo=identidade.nome_completo,
                data_nascimento=identidade.data_nascimento.isoformat(),
                nacionalidade=identidade.nacionalidade,
            )
        return self._executar(operacao, contexto)

    def ConsultarAntecedentes(self, pedido, contexto):
        def operacao(servico, _):
            pagina = servico.consultar_antecedentes(pedido.numero_bi, pedido.pagina or 1, pedido.tamanho_pagina or 10)
            return servico_militar_pb2.RespostaAntecedentes(
                numero_bi=pagina.numero_bi,
                itens=[servico_militar_pb2.AntecedenteCriminal(
                    id=item.id, numero_processo=item.numero_processo,
                    tipo_infracao=item.tipo_infracao, descricao=item.descricao,
                    tribunal=item.tribunal, data_sentenca=item.data_sentenca.isoformat(),
                    pena=item.pena, estado=item.estado,
                ) for item in pagina.itens], pagina=pagina.pagina,
                tamanho_pagina=pagina.tamanho_pagina, total=pagina.total,
                total_paginas=pagina.total_paginas,
            )
        return self._executar(operacao, contexto)


def criar_servidor(endereco: str, fabrica_sessoes: sessionmaker[Session] = SessaoLocal,
                   validador_identidade=None, consultor_antecedentes=None):
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servico_militar_pb2_grpc.add_ServicoMilitarServicer_to_server(
        ServicoGrpcMilitar(fabrica_sessoes, validador_identidade, consultor_antecedentes), servidor
    )
    porta = servidor.add_insecure_port(endereco)
    if porta == 0:
        raise RuntimeError(f"Não foi possível reservar o endereço gRPC {endereco}")
    return servidor, porta
