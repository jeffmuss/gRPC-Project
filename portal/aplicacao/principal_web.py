from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .configuracao import definicoes
from .infraestrutura.grpc import (
    obter_ligacao_identificacao_civil,
    obter_ligacao_registo_criminal,
    obter_ligacao_servico_militar,
)
from .web.rotas import roteador
from .web.renderizacao import DIRECTORIO_ESTATICOS


@asynccontextmanager
async def ciclo_vida(_: FastAPI):
    yield
    obter_ligacao_identificacao_civil().fechar()
    obter_ligacao_registo_criminal().fechar()
    obter_ligacao_servico_militar().fechar()


def criar_aplicacao() -> FastAPI:
    aplicacao = FastAPI(
        title="SISP - Portal unico",
        version="0.3.0",
        lifespan=ciclo_vida,
    )
    aplicacao.mount(
        "/estaticos", StaticFiles(directory=DIRECTORIO_ESTATICOS), name="estaticos"
    )
    aplicacao.include_router(roteador)
    return aplicacao


aplicacao = criar_aplicacao()
