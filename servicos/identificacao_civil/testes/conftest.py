from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy.orm import Session, sessionmaker

from servicos.identificacao_civil.aplicacao.infraestrutura.base_dados.base import Base
from servicos.identificacao_civil.aplicacao.infraestrutura.base_dados.sessao import create_base_dados_engine


@pytest.fixture()
def session_factory(tmp_path: Path) -> Generator[sessionmaker[Session], None, None]:
    engine = create_base_dados_engine(f"sqlite:///{(tmp_path / 'identificacao_civil-test.db').as_posix()}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    yield factory
    engine.dispose()
