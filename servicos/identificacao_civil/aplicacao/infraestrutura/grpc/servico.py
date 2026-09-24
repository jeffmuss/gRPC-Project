from __future__ import annotations

import logging
from concurrent import futures
from datetime import date

import grpc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from contratos.execucao import disponibilizar_contratos_gerados
from ...casos_uso import DadosCidadao, ServicoCidadaos, ServicoHistoricoCriminal
from ...dominio.entidades import Cidadao
from ...dominio.excepcoes import (
    CidadaoJaExiste, CidadaoNaoEncontrado, HistoricoCriminalIndisponivel,
    ErroDominio, ErroValidacao,
)
from ..base_dados.repositorio import SqlAlchemyRepositorioCidadaos
from ..base_dados.sessao import SessionLocal
from .cliente_registo_criminal import GrpcLigacaoHistoricoCriminal


disponibilizar_contratos_gerados()
from identificacao_civil.v1 import identificacao_civil_pb2, identificacao_civil_pb2_grpc  # noqa: E402


logger = logging.getLogger(__name__)


def _citizen_message(citizen: Cidadao) -> identificacao_civil_pb2.Cidadao:
    return identificacao_civil_pb2.Cidadao(
        id=citizen.id or 0,
        numero_bi=citizen.numero_bi,
        nome_completo=citizen.nome_completo,
        data_nascimento=citizen.data_nascimento.isoformat(),
        sexo=citizen.sexo.value,
        nacionalidade=citizen.nacionalidade,
        nome_pai=citizen.nome_pai or "",
        nome_mae=citizen.nome_mae or "",
        residencia=citizen.residencia or "",
        data_registo=citizen.data_registo.isoformat() if citizen.data_registo else "",
        data_actualizacao=(
            citizen.data_actualizacao.isoformat() if citizen.data_actualizacao else ""
        ),
    )


def _citizen_input(message: identificacao_civil_pb2.DadosCidadao) -> DadosCidadao:
    try:
        birth_date = date.fromisoformat(message.data_nascimento)
    except ValueError as error:
        raise ErroValidacao("Introduza uma data de nascimento valida.") from error
    return DadosCidadao(
        numero_bi=message.numero_bi,
        nome_completo=message.nome_completo,
        data_nascimento=birth_date,
        sexo=message.sexo,
        nacionalidade=message.nacionalidade,
        nome_pai=message.nome_pai or None,
        nome_mae=message.nome_mae or None,
        residencia=message.residencia or None,
    )


class ServicoGrpcIdentificacaoCivil(identificacao_civil_pb2_grpc.ServicoIdentificacaoCivilServicer):
    def __init__(self, session_factory: sessionmaker[Session] = SessionLocal, registo_criminal_gateway=None) -> None:
        self.sessao_factory = session_factory
        self.registo_criminal_gateway = registo_criminal_gateway or GrpcLigacaoHistoricoCriminal()

    def _run(self, operation, context: grpc.ServicerContext):
        try:
            with self.sessao_factory() as session:
                service = ServicoCidadaos(SqlAlchemyRepositorioCidadaos(session))
                return operation(service, session)
        except CidadaoJaExiste as error:
            context.abort(grpc.StatusCode.ALREADY_EXISTS, str(error))
        except CidadaoNaoEncontrado as error:
            context.abort(grpc.StatusCode.NOT_FOUND, str(error))
        except ErroValidacao as error:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(error))
        except HistoricoCriminalIndisponivel as error:
            context.abort(grpc.StatusCode.UNAVAILABLE, str(error))
        except ErroDominio as error:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, str(error))
        except SQLAlchemyError:
            logger.exception("Falha de persistencia no servico de Identificacao Civil")
            context.abort(grpc.StatusCode.INTERNAL, "Falha interna ao aceder aos dados.")

    def VerificarSaude(self, request, context):
        return identificacao_civil_pb2.RespostaSaude(
            servico="identificacao_civil", estado="operacional"
        )

    def RegistarCidadao(self, request, context):
        return self._run(
            lambda service, _: _citizen_message(
                service.registar(_citizen_input(request.cidadao))
            ),
            context,
        )

    def ObterCidadao(self, request, context):
        return self._run(
            lambda service, _: _citizen_message(service.obter(request.cidadao_id)),
            context,
        )

    def ProcurarCidadaoPorBi(self, request, context):
        return self._run(
            lambda service, _: _citizen_message(service.procurar_por_bi(request.numero_bi)),
            context,
        )

    def ListarCidadaos(self, request, context):
        def operation(service: ServicoCidadaos, session: Session):
            result = service.listar(pagina=request.pagina or 1, tamanho_pagina=request.tamanho_pagina or 10)
            repository = SqlAlchemyRepositorioCidadaos(session)
            last_updated = repository.ultima_actualizacao()
            return identificacao_civil_pb2.RespostaListarCidadaos(
                itens=[_citizen_message(item) for item in result.itens],
                pagina=result.pagina,
                tamanho_pagina=result.tamanho_pagina,
                total=result.total,
                total_paginas=result.total_paginas,
                ultima_actualizacao=last_updated.isoformat() if last_updated else "",
            )

        return self._run(operation, context)

    def ActualizarCidadao(self, request, context):
        return self._run(
            lambda service, _: _citizen_message(
                service.actualizar(request.cidadao_id, _citizen_input(request.cidadao))
            ),
            context,
        )

    def ObterHistoricoCriminal(self, request, context):
        def operation(_, session: Session):
            service = ServicoHistoricoCriminal(
                SqlAlchemyRepositorioCidadaos(session), self.registo_criminal_gateway
            )
            result = service.consultar(
                request.numero_bi, request.pagina or 1, request.tamanho_pagina or 10
            )
            return identificacao_civil_pb2.RespostaHistoricoCriminal(
                numero_bi=result.numero_bi,
                itens=[
                    identificacao_civil_pb2.ItemHistoricoCriminal(
                        id=item.id,
                        numero_processo=item.numero_processo,
                        tipo_infracao=item.tipo_infracao,
                        descricao=item.descricao,
                        tribunal=item.tribunal,
                        data_sentenca=item.data_sentenca.isoformat(),
                        pena=item.pena,
                        estado=item.estado,
                    )
                    for item in result.itens
                ],
                pagina=result.pagina,
                tamanho_pagina=result.tamanho_pagina,
                total=result.total,
                total_paginas=result.total_paginas,
            )

        return self._run(operation, context)


def criar_servidor(
    address: str,
    session_factory: sessionmaker[Session] = SessionLocal,
    registo_criminal_gateway=None,
) -> tuple[grpc.Server, int]:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    identificacao_civil_pb2_grpc.add_ServicoIdentificacaoCivilServicer_to_server(
        ServicoGrpcIdentificacaoCivil(session_factory, registo_criminal_gateway), server
    )
    bound_port = server.add_insecure_port(address)
    if bound_port == 0:
        raise RuntimeError(f"Nao foi possivel reservar o endereco gRPC {address}")
    return server, bound_port
