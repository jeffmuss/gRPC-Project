from __future__ import annotations

import logging

from .configuracao.definicoes import definicoes
from .infraestrutura.grpc import criar_servidor


def principal() -> None:
    endereco = f"{definicoes.anfitriao_grpc}:{definicoes.porta_grpc}"
    servidor, _ = criar_servidor(endereco)
    servidor.start()
    logging.getLogger(__name__).info("Registo Criminal gRPC activo em %s", endereco)
    try:
        servidor.wait_for_termination()
    except KeyboardInterrupt:
        servidor.stop(grace=3)


if __name__ == "__main__":
    principal()
