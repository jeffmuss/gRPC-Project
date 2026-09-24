from fastapi import APIRouter

from .registo_criminal import roteador as roteador_registo_criminal
from .portal import roteador as roteador_portal
from .servico_militar import roteador as roteador_servico_militar

roteador = APIRouter()
roteador.include_router(roteador_portal)
roteador.include_router(roteador_registo_criminal)
roteador.include_router(roteador_servico_militar)

__all__ = ["roteador"]
