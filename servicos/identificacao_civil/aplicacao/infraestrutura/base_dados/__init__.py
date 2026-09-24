"""Persistencia local da Identificacao Civil."""
from .repositorio import SqlAlchemyRepositorioCidadaos
from .sessao import obter_sessao

__all__ = ["SqlAlchemyRepositorioCidadaos", "obter_sessao"]
