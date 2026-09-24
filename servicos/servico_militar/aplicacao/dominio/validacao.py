from __future__ import annotations

from datetime import date

from .entidades import SituacaoMilitar
from .excepcoes import ErroValidacao


def obrigatorio(valor: str, rotulo: str, maximo: int = 200) -> str:
    normalizado = " ".join(valor.split())
    if not normalizado:
        raise ErroValidacao(f"{rotulo} é obrigatório.")
    if len(normalizado) > maximo:
        raise ErroValidacao(f"{rotulo} não pode exceder {maximo} caracteres.")
    return normalizado


def normalizar_bi(valor: str) -> str:
    return obrigatorio(valor, "Número de BI", 50).upper()


def normalizar_numero(valor: str) -> str:
    return obrigatorio(valor, "Número de recenseamento", 80).upper()


def validar_data(valor: date) -> date:
    if valor > date.today():
        raise ErroValidacao("A data de recenseamento não pode ser futura.")
    return valor


def validar_situacao(valor: str | SituacaoMilitar) -> SituacaoMilitar:
    try:
        return valor if isinstance(valor, SituacaoMilitar) else SituacaoMilitar(valor.strip().upper())
    except ValueError as erro:
        raise ErroValidacao("Seleccione uma situação militar válida.") from erro
