from fastapi import APIRouter

from ...configuracao.definicoes import definicoes


roteador = APIRouter()


@roteador.get("/saude", tags=["saude"])
def saude() -> dict[str, str]:
    return {"servico": definicoes.nome_servico, "estado": "operacional"}
