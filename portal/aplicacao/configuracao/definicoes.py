from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values


RAIZ_PORTAL = Path(__file__).resolve().parents[2]
_ambiente = {**dotenv_values(RAIZ_PORTAL / ".env"), **os.environ}


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
    nome_servico: str = "portal"
    nome_apresentacao_servico: str = "Portal SISP"
    anfitriao_web: str = _ambiente.get("ANFITRIAO_WEB", "127.0.0.1")
    porta_web: int = _inteiro("PORTA_WEB", 8000)
    alvo_grpc_identificacao_civil: str = _ambiente.get(
        "ALVO_GRPC_IDENTIFICACAO_CIVIL", "127.0.0.1:50051"
    )
    alvo_grpc_registo_criminal: str = _ambiente.get(
        "ALVO_GRPC_REGISTO_CRIMINAL", "127.0.0.1:50052"
    )
    alvo_grpc_servico_militar: str = _ambiente.get(
        "ALVO_GRPC_SERVICO_MILITAR", "127.0.0.1:50053"
    )
    tempo_limite_grpc_segundos: float = _decimal_positivo(
        "TEMPO_LIMITE_GRPC_SEGUNDOS", 3.0
    )


definicoes = Definicoes()
