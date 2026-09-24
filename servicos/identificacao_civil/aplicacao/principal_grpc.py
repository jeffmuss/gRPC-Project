from .configuracao.definicoes import definicoes
from .infraestrutura.grpc import criar_servidor


def principal() -> None:
    endereco = f"{definicoes.anfitriao_grpc}:{definicoes.porta_grpc}"
    servidor, _ = criar_servidor(endereco)
    servidor.start()
    print(f"Identificacao Civil gRPC activa em {endereco}")
    try:
        servidor.wait_for_termination()
    except KeyboardInterrupt:
        servidor.stop(grace=5).wait()


if __name__ == "__main__":
    principal()
