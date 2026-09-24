from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from ...configuracao.definicoes import definicoes


def create_base_dados_engine(base_dados_url: str) -> Engine:
    if base_dados_url.startswith("sqlite:///") and ":memory:" not in base_dados_url:
        path_text = base_dados_url.removeprefix("sqlite:///")
        Path(path_text).parent.mkdir(parents=True, exist_ok=True)
    connect_args = {"check_same_thread": False} if base_dados_url.startswith("sqlite") else {}
    base_dados_engine = create_engine(base_dados_url, connect_args=connect_args)
    if base_dados_url.startswith("sqlite"):
        event.listen(
            base_dados_engine,
            "connect",
            lambda connection, _: connection.execute("PRAGMA foreign_keys=ON"),
        )
    return base_dados_engine


engine = create_base_dados_engine(definicoes.url_base_dados_resolvida)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def obter_sessao() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
