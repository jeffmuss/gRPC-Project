from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values


RAIZ_SERVICO = Path(__file__).resolve().parents[2]
_ambiente = {**dotenv_values(RAIZ_SERVICO / ".env"), **os.environ}


def _inteiro(nome: str, predefinido: int) -> int:
    valor = int(_ambiente.get(nome, str(predefinido)))
    if not 1 <= valor <= 65535:
        raise ValueError(f"{nome} deve estar entre 1 e 65535")
    return valor


def _decimal_positivo(nome: str, predefinido: float) -> float:
    valor = float(_ambiente.get(nome, str(predefinido)))
    if valor <= 0:
        raise ValueError(f"{nome} deve ser superior a zero")
    return valor


@dataclass(frozen=True)
class Definicoes:
    nome_servico: str = "identificacao_civil"
    nome_apresentacao_servico: str = "Identificacao Civil"
    ip_servico: str = _ambiente.get("IP_SERVICO", "127.0.0.1")
    anfitriao_web: str = _ambiente.get("ANFITRIAO_WEB", "127.0.0.1")
    porta_web: int = _inteiro("PORTA_WEB", 8001)
    anfitriao_grpc: str = _ambiente.get("ANFITRIAO_GRPC", "127.0.0.1")
    porta_grpc: int = _inteiro("PORTA_GRPC", 50051)
    url_base_dados: str = _ambiente.get(
        "URL_BASE_DADOS", "sqlite:///./dados/identificacao_civil.db"
    )
    alvo_grpc_registo_criminal: str = _ambiente.get(
        "ALVO_GRPC_REGISTO_CRIMINAL", "127.0.0.1:50052"
    )
    tempo_limite_grpc_segundos: float = _decimal_positivo(
        "TEMPO_LIMITE_GRPC_SEGUNDOS", 3.0
    )

    @property
    def url_base_dados_resolvida(self) -> str:
        prefixo = "sqlite:///./"
        if not self.url_base_dados.startswith(prefixo):
            return self.url_base_dados
        caminho = (RAIZ_SERVICO / self.url_base_dados.removeprefix(prefixo)).resolve()
        return f"sqlite:///{caminho.as_posix()}"


definicoes = Definicoes()
