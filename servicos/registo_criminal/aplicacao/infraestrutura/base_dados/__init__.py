"""Persistencia local do Registo Criminal."""
from .repositorio import SqlAlchemyRepositorioRegistoCriminal
from .sessao import obter_sessao
__all__ = ["SqlAlchemyRepositorioRegistoCriminal", "obter_sessao"]
