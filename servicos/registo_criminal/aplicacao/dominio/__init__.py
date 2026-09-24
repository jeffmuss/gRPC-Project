"""Dominio do Registo Criminal."""
from .entidades import RegistoCriminal, DadosIdentidade, EstadoRegisto
from .excepcoes import JaExiste, IdentificacaoIndisponivel, NaoEncontrado, ErroValidacao

__all__ = ["JaExiste", "RegistoCriminal", "DadosIdentidade", "IdentificacaoIndisponivel", "NaoEncontrado", "EstadoRegisto", "ErroValidacao"]
