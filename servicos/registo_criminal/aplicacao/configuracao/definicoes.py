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


@dataclass(frozen=True)
class Definicoes:
    nome_servico: str = "registo_criminal"
    nome_apresentacao_servico: str = "Registo Criminal"
    ip_servico: str = _ambiente.get("IP_SERVICO", "127.0.0.1")
    anfitriao_web: str = _ambiente.get("ANFITRIAO_WEB", "127.0.0.1")
    porta_web: int = _inteiro("PORTA_WEB", 8002)
    anfitriao_grpc: str = _ambiente.get("ANFITRIAO_GRPC", "127.0.0.1")
    porta_grpc: int = _inteiro("PORTA_GRPC", 50052)
    url_base_dados: str = _ambiente.get(
        "URL_BASE_DADOS", "sqlite:///./dados/registo_criminal.db"
    )
    alvo_grpc_identificacao_civil: str = _ambiente.get(
        "ALVO_GRPC_IDENTIFICACAO_CIVIL", "127.0.0.1:50051"
    )
    tempo_limite_grpc_segundos: float = float(
        _ambiente.get("TEMPO_LIMITE_GRPC_SEGUNDOS", "3")
    )

    @property
    def url_base_dados_resolvida(self) -> str:
        prefixo = "sqlite:///./"
        if not self.url_base_dados.startswith(prefixo):
            return self.url_base_dados
        caminho = (RAIZ_SERVICO / self.url_base_dados.removeprefix(prefixo)).resolve()
        return f"sqlite:///{caminho.as_posix()}"


definicoes = Definicoes()
