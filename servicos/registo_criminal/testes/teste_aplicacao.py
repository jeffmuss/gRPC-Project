from __future__ import annotations

from datetime import date, timedelta

import pytest

from servicos.registo_criminal.aplicacao.casos_uso import ServicoRegistoCriminal, DadosRegisto
from servicos.registo_criminal.aplicacao.dominio import JaExiste, ErroValidacao
from servicos.registo_criminal.aplicacao.infraestrutura.base_dados.repositorio import SqlAlchemyRepositorioRegistoCriminal


def input_record(**changes) -> DadosRegisto:
    values = dict(numero_bi="bi-test-001", numero_processo="proc-001",
                  tipo_infracao="Infraccao ficticia", descricao="Descricao de teste",
                  tribunal="Tribunal de teste", data_sentenca=date(2025, 1, 10),
                  pena="Pena ficticia", estado="ACTIVO")
    values.update(changes)
    return DadosRegisto(**values)


def service_for(session_factory, identity_verifier):
    session = session_factory()
    return ServicoRegistoCriminal(SqlAlchemyRepositorioRegistoCriminal(session), identity_verifier), session


def test_create_search_update_and_no_delete_use_case(session_factory, identity_verifier) -> None:
    service, session = service_for(session_factory, identity_verifier)
    try:
        created = service.criar_registo(input_record())
        assert created.numero_bi == "BI-TEST-001"
        assert service.listar_registos(numero_bi="bi-test-001").total == 1
        updated = service.actualizar_registo(created.id, input_record(estado="CUMPRIDO", pena="Cumprida"))
        assert updated.estado.value == "CUMPRIDO"
        assert not hasattr(service, "delete_record")
    finally:
        session.close()


def test_duplicate_and_future_date_are_rejected_but_registration_is_local(session_factory, identity_verifier) -> None:
    service, session = service_for(session_factory, identity_verifier)
    try:
        service.criar_registo(input_record())
        with pytest.raises(JaExiste):
            service.criar_registo(input_record())
        local = service.criar_registo(input_record(numero_bi="BI-INEXISTENTE", numero_processo="PROC-002"))
        assert local.numero_bi == "BI-INEXISTENTE"
        with pytest.raises(ErroValidacao, match="nao pode ser futura"):
            service.criar_registo(input_record(numero_processo="PROC-003", data_sentenca=date.today() + timedelta(days=1)))
    finally:
        session.close()


def test_identity_validation_is_the_only_interoperable_use_case(session_factory, identity_verifier) -> None:
    service, session = service_for(session_factory, identity_verifier)
    try:
        found = service.validar_identidade("bi-test-001")
        assert found is not None and found.nome_completo == "Cidadao de Teste"
        assert service.validar_identidade("BI-INEXISTENTE") is None
    finally:
        session.close()
