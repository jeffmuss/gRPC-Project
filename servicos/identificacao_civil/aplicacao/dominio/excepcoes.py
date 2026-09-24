class ErroDominio(Exception):
    """Erro esperado e seguro para apresentacao ao utilizador."""


class ErroValidacao(ErroDominio):
    pass


class CidadaoJaExiste(ErroDominio):
    pass


class CidadaoNaoEncontrado(ErroDominio):
    pass


class HistoricoCriminalIndisponivel(ErroDominio):
    pass
