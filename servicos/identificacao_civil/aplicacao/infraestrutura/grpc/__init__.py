"""Adaptadores gRPC da Identificacao Civil."""
from .servico import ServicoGrpcIdentificacaoCivil, criar_servidor
from .cliente_registo_criminal import GrpcLigacaoHistoricoCriminal

__all__ = ["GrpcLigacaoHistoricoCriminal", "ServicoGrpcIdentificacaoCivil", "criar_servidor"]
