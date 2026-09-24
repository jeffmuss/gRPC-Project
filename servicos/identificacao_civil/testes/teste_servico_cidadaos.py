from __future__ import annotations

from datetime import date, timedelta

import pytest
from sqlalchemy.orm import Session, sessionmaker

from servicos.identificacao_civil.aplicacao.casos_uso import DadosCidadao, ServicoCidadaos
from servicos.identificacao_civil.aplicacao.dominio.excepcoes import CidadaoJaExiste, CidadaoNaoEncontrado, ErroValidacao
from servicos.identificacao_civil.aplicacao.infraestrutura.base_dados.repositorio import SqlAlchemyRepositorioCidadaos


def service_for(factory: sessionmaker[Session]) -> tuple[ServicoCidadaos, Session]:
    session = factory()
    return ServicoCidadaos(SqlAlchemyRepositorioCidadaos(session)), session


def valid_input(numero_bi: str = "BI-TEST-001") -> DadosCidadao:
    return DadosCidadao(
        numero_bi=numero_bi,
        nome_completo="Cidadao Teste",
        data_nascimento=date(1990, 6, 12),
        sexo="M",
        nacionalidade="Ficticia",
        residencia="Endereco ficticio",
    )


def test_register_and_persist_between_sessions(session_factory: sessionmaker[Session]) -> None:
    service, first_session = service_for(session_factory)
    created = service.registar(valid_input())
    first_session.close()
    second_service, second_session = service_for(session_factory)
    try:
        found = second_service.procurar_por_bi("bi-test-001")
        assert found.id == created.id
        assert found.nome_completo == "Cidadao Teste"
    finally:
        second_session.close()


def test_reject_duplicate_bi(session_factory: sessionmaker[Session]) -> None:
    service, session = service_for(session_factory)
    try:
        service.registar(valid_input())
        with pytest.raises(CidadaoJaExiste):
            service.registar(valid_input())
    finally:
        session.close()


def test_reject_blank_required_field(session_factory: sessionmaker[Session]) -> None:
    service, session = service_for(session_factory)
    try:
        data = valid_input()
        with pytest.raises(ErroValidacao, match="Nome completo e obrigatorio"):
            service.registar(
                DadosCidadao(
                    numero_bi=data.numero_bi,
                    nome_completo="   ",
                    data_nascimento=data.data_nascimento,
                    sexo=data.sexo,
                    nacionalidade=data.nacionalidade,
                )
            )
    finally:
        session.close()


def test_reject_future_birth_date(session_factory: sessionmaker[Session]) -> None:
    service, session = service_for(session_factory)
    try:
        with pytest.raises(ErroValidacao, match="nao pode ser futura"):
            service.registar(
                DadosCidadao(
                    numero_bi="BI-FUTURE",
                    nome_completo="Pessoa Futura",
                    data_nascimento=date.today() + timedelta(days=1),
                    sexo="F",
                    nacionalidade="Ficticia",
                )
            )
    finally:
        session.close()


def test_update_and_paginate(session_factory: sessionmaker[Session]) -> None:
    service, session = service_for(session_factory)
    try:
        for index in range(12):
            service.registar(valid_input(f"BI-PAGE-{index:03d}"))
        second_page = service.listar(pagina=2, tamanho_pagina=10)
        assert second_page.total == 12
        assert len(second_page.itens) == 2
        citizen = service.procurar_por_bi("BI-PAGE-000")
        updated = service.actualizar(
            citizen.id,
            DadosCidadao(
                numero_bi=citizen.numero_bi,
                nome_completo=citizen.nome_completo,
                data_nascimento=citizen.data_nascimento,
                sexo=citizen.sexo,
                nacionalidade=citizen.nacionalidade,
                residencia="Nova residencia ficticia",
            ),
        )
        assert updated.residencia == "Nova residencia ficticia"
    finally:
        session.close()


def test_missing_citizen(session_factory: sessionmaker[Session]) -> None:
    service, session = service_for(session_factory)
    try:
        with pytest.raises(CidadaoNaoEncontrado):
            service.obter(9999)
    finally:
        session.close()
