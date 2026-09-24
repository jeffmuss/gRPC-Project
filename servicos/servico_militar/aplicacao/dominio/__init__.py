"""Dominio do Servico Militar."""
"""Domínio do Serviço Militar."""

from .entidades import (
    AntecedenteCriminal,
    DadosIdentidade,
    PaginaAntecedentes,
    RecenseamentoMilitar,
    SituacaoMilitar,
)
from .excepcoes import (
    ErroValidacao,
    IdentificacaoIndisponivel,
    JaExiste,
    NaoEncontrado,
    RegistoCriminalIndisponivel,
)

__all__ = [
    "AntecedenteCriminal", "DadosIdentidade", "PaginaAntecedentes",
    "RecenseamentoMilitar", "SituacaoMilitar", "ErroValidacao",
    "IdentificacaoIndisponivel", "RegistoCriminalIndisponivel",
    "JaExiste", "NaoEncontrado",
]
