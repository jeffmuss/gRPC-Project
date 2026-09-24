"""Persistencia local do Servico Militar."""
from .repositorio import SqlAlchemyRepositorioRecenseamentoMilitar
from .sessao import SessaoLocal, criar_motor_base_dados

__all__ = ["SqlAlchemyRepositorioRecenseamentoMilitar", "SessaoLocal", "criar_motor_base_dados"]
