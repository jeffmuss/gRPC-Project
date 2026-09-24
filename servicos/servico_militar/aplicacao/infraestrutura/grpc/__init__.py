"""Adaptadores gRPC do Servico Militar."""
from .servico import ServicoGrpcMilitar, criar_servidor

__all__ = ["ServicoGrpcMilitar", "criar_servidor"]
