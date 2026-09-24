from __future__ import annotations

import logging
from concurrent import futures
from datetime import date

import grpc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from contratos.execucao import disponibilizar_contratos_gerados
from ...casos_uso import ServicoRegistoCriminal, DadosRegisto
from ...dominio import JaExiste, RegistoCriminal, DadosIdentidade, IdentificacaoIndisponivel, NaoEncontrado, ErroValidacao
from ..base_dados.repositorio import SqlAlchemyRepositorioRegistoCriminal
from ..base_dados.sessao import SessionLocal
from .cliente_identificacao_civil import GrpcValidadorIdentidade

disponibilizar_contratos_gerados()
from registo_criminal.v1 import registo_criminal_pb2, registo_criminal_pb2_grpc  # noqa: E402

logger = logging.getLogger(__name__)


def _record_message(item: RegistoCriminal) -> registo_criminal_pb2.RegistoCriminal:
    return registo_criminal_pb2.RegistoCriminal(
        id=item.id or 0, numero_bi=item.numero_bi, numero_processo=item.numero_processo,
        tipo_infracao=item.tipo_infracao, descricao=item.descricao, tribunal=item.tribunal,
        data_sentenca=item.data_sentenca.isoformat(), pena=item.pena, estado=item.estado.value,
        data_registo=item.data_registo.isoformat() if item.data_registo else "",
        data_actualizacao=item.data_actualizacao.isoformat() if item.data_actualizacao else "",
    )


def _identity_message(item: DadosIdentidade | None, requested_bi: str) -> registo_criminal_pb2.ValidacaoIdentidade:
    if item is None:
        return registo_criminal_pb2.ValidacaoIdentidade(existe=False, numero_bi=requested_bi.upper())
    return registo_criminal_pb2.ValidacaoIdentidade(
        existe=True,
        numero_bi=item.numero_bi,
        nome_completo=item.nome_completo,
        data_nascimento=item.data_nascimento.isoformat(),
        nacionalidade=item.nacionalidade,
    )


def _record_input(message) -> DadosRegisto:
    try:
        sentenca = date.fromisoformat(message.data_sentenca)
    except ValueError as error:
        raise ErroValidacao("Introduza uma data de sentenca valida.") from error
    return DadosRegisto(message.numero_bi, message.numero_processo, message.tipo_infracao,
                       message.descricao, message.tribunal, sentenca, message.pena, message.estado)


class ServicoGrpcRegistoCriminal(registo_criminal_pb2_grpc.ServicoRegistoCriminalServicer):
    def __init__(self, session_factory: sessionmaker[Session] = SessionLocal, identity_verifier=None) -> None:
        self.sessao_factory = session_factory
        self.identity_verifier = identity_verifier or GrpcValidadorIdentidade()

    def _run(self, operation, context):
        try:
            with self.sessao_factory() as session:
                service = ServicoRegistoCriminal(SqlAlchemyRepositorioRegistoCriminal(session), self.identity_verifier)
                return operation(service, session)
        except JaExiste as error:
            context.abort(grpc.StatusCode.ALREADY_EXISTS, str(error))
        except NaoEncontrado as error:
            context.abort(grpc.StatusCode.NOT_FOUND, str(error))
        except ErroValidacao as error:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(error))
        except IdentificacaoIndisponivel as error:
            context.abort(grpc.StatusCode.UNAVAILABLE, str(error))
        except SQLAlchemyError:
            logger.exception("Falha de persistencia no servico de Registo Criminal")
            context.abort(grpc.StatusCode.INTERNAL, "Falha interna ao aceder aos dados.")

    def VerificarSaude(self, request, context):
        return registo_criminal_pb2.RespostaSaude(servico="registo_criminal", estado="operacional")

    def CriarRegisto(self, request, context):
        return self._run(lambda service, _: _record_message(service.criar_registo(_record_input(request.registo))), context)

    def ObterRegisto(self, request, context):
        return self._run(lambda service, _: _record_message(service.obter_registo(request.registo_id)), context)

    def ListarRegistos(self, request, context):
        def operation(service, session):
            result = service.listar_registos(request.pagina or 1, request.tamanho_pagina or 10, request.numero_bi or None)
            updated = SqlAlchemyRepositorioRegistoCriminal(session).ultima_actualizacao_registo()
            return registo_criminal_pb2.RespostaListarRegistos(
                itens=[_record_message(item) for item in result.itens], pagina=result.pagina,
                tamanho_pagina=result.tamanho_pagina, total=result.total, total_paginas=result.total_paginas,
                ultima_actualizacao=updated.isoformat() if updated else "",
            )
        return self._run(operation, context)

    def ActualizarRegisto(self, request, context):
        return self._run(lambda service, _: _record_message(service.actualizar_registo(request.registo_id, _record_input(request.registo))), context)

    def ValidarIdentidade(self, request, context):
        return self._run(
            lambda service, _: _identity_message(
                service.validar_identidade(request.numero_bi), request.numero_bi
            ),
            context,
        )


def criar_servidor(address: str, session_factory: sessionmaker[Session] = SessionLocal, identity_verifier=None) -> tuple[grpc.Server, int]:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    registo_criminal_pb2_grpc.add_ServicoRegistoCriminalServicer_to_server(
        ServicoGrpcRegistoCriminal(session_factory, identity_verifier), server
    )
    bound_port = server.add_insecure_port(address)
    if bound_port == 0:
        raise RuntimeError(f"Nao foi possivel reservar o endereco gRPC {address}")
    return server, bound_port
