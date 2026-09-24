from __future__ import annotations

from datetime import date

from .entidades import Sexo
from .excepcoes import ErroValidacao


MAX_BI_LENGTH = 50
MAX_NAME_LENGTH = 200
MAX_SHORT_TEXT_LENGTH = 100
MAX_ADDRESS_LENGTH = 300


def required_text(value: str, label: str, max_length: int) -> str:
    normalized = " ".join(value.split())
    if not normalized:
        raise ErroValidacao(f"{label} e obrigatorio.")
    if len(normalized) > max_length:
        raise ErroValidacao(f"{label} nao pode exceder {max_length} caracteres.")
    return normalized


def optional_text(value: str | None, label: str, max_length: int) -> str | None:
    if value is None or not value.strip():
        return None
    return required_text(value, label, max_length)


def normalize_bi(value: str) -> str:
    return required_text(value, "Numero de BI", MAX_BI_LENGTH).upper()


def validate_birth_date(value: date) -> date:
    if value > date.today():
        raise ErroValidacao("A data de nascimento nao pode ser futura.")
    return value


def parse_sex(value: str | Sexo) -> Sexo:
    try:
        return value if isinstance(value, Sexo) else Sexo(value.strip().upper())
    except ValueError as error:
        raise ErroValidacao("Seleccione um valor de sexo valido.") from error
