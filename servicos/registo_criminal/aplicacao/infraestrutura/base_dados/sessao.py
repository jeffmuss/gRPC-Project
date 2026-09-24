from collections.abc import Generator
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from ...configuracao.definicoes import definicoes

def create_base_dados_engine(url: str):
    if url.startswith("sqlite:///") and ":memory:" not in url: Path(url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(url, connect_args={"check_same_thread": False} if url.startswith("sqlite") else {})
    if url.startswith("sqlite"): event.listen(engine, "connect", lambda connection, _: connection.execute("PRAGMA foreign_keys=ON"))
    return engine

engine = create_base_dados_engine(definicoes.url_base_dados_resolvida)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
def obter_sessao() -> Generator[Session, None, None]:
    with SessionLocal() as session: yield session
