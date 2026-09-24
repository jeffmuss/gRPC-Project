from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from ...configuracao.definicoes import definicoes


def criar_motor_base_dados(url: str):
    if url.startswith("sqlite:///") and ":memory:" not in url:
        Path(url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
    motor = create_engine(
        url,
        connect_args={"check_same_thread": False} if url.startswith("sqlite") else {},
    )
    if url.startswith("sqlite"):
        event.listen(motor, "connect", lambda ligacao, _: ligacao.execute("PRAGMA foreign_keys=ON"))
    return motor


motor = criar_motor_base_dados(definicoes.url_base_dados_resolvida)
SessaoLocal = sessionmaker(bind=motor, autoflush=False, expire_on_commit=False)


def obter_sessao() -> Generator[Session, None, None]:
    with SessaoLocal() as sessao:
        yield sessao
