from __future__ import annotations
from datetime import date
from .entidades import EstadoRegisto
from .excepcoes import ErroValidacao


def required(value: str, label: str, maximum: int = 300) -> str:
    normalized = " ".join(value.split())
    if not normalized: raise ErroValidacao(f"{label} e obrigatorio.")
    if len(normalized) > maximum: raise ErroValidacao(f"{label} nao pode exceder {maximum} caracteres.")
    return normalized


def normalize_bi(value: str) -> str: return required(value, "Numero de BI", 50).upper()
def normalize_process(value: str) -> str: return required(value, "Numero do processo", 80).upper()


def sentence_date(value: date) -> date:
    if value > date.today(): raise ErroValidacao("A data da sentenca nao pode ser futura.")
    return value


def record_status(value: str | EstadoRegisto) -> EstadoRegisto:
    try: return value if isinstance(value, EstadoRegisto) else EstadoRegisto(value.strip().upper())
    except ValueError as error: raise ErroValidacao("Seleccione um estado valido.") from error
