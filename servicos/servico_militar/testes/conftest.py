from __future__ import annotations

from collections.abc import Generator
from datetime import date
from pathlib import Path

import pytest
from sqlalchemy.orm import Session, sessionmaker

from servicos.servico_militar.aplicacao.dominio import AntecedenteCriminal, DadosIdentidade, PaginaAntecedentes
from servicos.servico_militar.aplicacao.infraestrutura.base_dados.base import Base
from servicos.servico_militar.aplicacao.infraestrutura.base_dados.sessao import criar_motor_base_dados


class IdentidadeFalsa:
    def procurar(self, numero_bi: str):
        if numero_bi != "BI-TEST-001":
            return None
        return DadosIdentidade(numero_bi, "Cidadão de Teste", date(1990, 1, 1), "Fictícia")


class AntecedentesFalsos:
    def consultar(self, numero_bi: str, pagina: int, tamanho_pagina: int):
        item = AntecedenteCriminal(1, "PROC-TEST-001", "Infracção fictícia", "Descrição",
                                   "Tribunal fictício", date(2025, 1, 1), "Pena fictícia", "ACTIVO")
        return PaginaAntecedentes(numero_bi, [item], pagina, tamanho_pagina, 1, 1)


@pytest.fixture()
def fabrica_sessoes(tmp_path: Path) -> Generator[sessionmaker[Session], None, None]:
    motor = criar_motor_base_dados(f"sqlite:///{(tmp_path / 'servico-militar.db').as_posix()}")
    Base.metadata.create_all(motor)
    fabrica = sessionmaker(bind=motor, autoflush=False, expire_on_commit=False)
    yield fabrica
    motor.dispose()


@pytest.fixture()
def identidade_falsa():
    return IdentidadeFalsa()


@pytest.fixture()
def antecedentes_falsos():
    return AntecedentesFalsos()
