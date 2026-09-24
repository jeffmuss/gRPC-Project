from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from datetime import date

import pytest
from sqlalchemy.orm import Session, sessionmaker

from servicos.registo_criminal.aplicacao.infraestrutura.base_dados.base import Base
from servicos.registo_criminal.aplicacao.infraestrutura.base_dados.sessao import create_base_dados_engine
from servicos.registo_criminal.aplicacao.dominio import DadosIdentidade


class FakeValidadorIdentidade:
    def __init__(self, valid_bis: set[str] | None = None) -> None:
        self.valid_bis = valid_bis or {"BI-TEST-001", "BI-TEST-002"}

    def procurar(self, numero_bi: str) -> DadosIdentidade | None:
        if numero_bi not in self.valid_bis:
            return None
        return DadosIdentidade(numero_bi, "Cidadao de Teste", date(1990, 1, 1), "Ficticia")


@pytest.fixture()
def identity_verifier() -> FakeValidadorIdentidade:
    return FakeValidadorIdentidade()


@pytest.fixture()
def session_factory(tmp_path: Path) -> Generator[sessionmaker[Session], None, None]:
    engine = create_base_dados_engine(f"sqlite:///{(tmp_path / 'registo_criminal-test.db').as_posix()}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    yield factory
    engine.dispose()
