from fastapi import FastAPI

from .configuracao.definicoes import definicoes
from .web.rotas.saude import roteador as roteador_saude


def criar_aplicacao() -> FastAPI:
    aplicacao = FastAPI(
        title=f"SISP - {definicoes.nome_apresentacao_servico}",
        version="0.1.0",
    )
    aplicacao.include_router(roteador_saude)
    return aplicacao


aplicacao = criar_aplicacao()
