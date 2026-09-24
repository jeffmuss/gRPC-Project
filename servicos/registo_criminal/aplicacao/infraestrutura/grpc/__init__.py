"""Adaptadores gRPC do Registo Criminal."""

from .cliente_identificacao_civil import GrpcValidadorIdentidade
from .servico import ServicoGrpcRegistoCriminal, criar_servidor

__all__ = ["ServicoGrpcRegistoCriminal", "GrpcValidadorIdentidade", "criar_servidor"]
