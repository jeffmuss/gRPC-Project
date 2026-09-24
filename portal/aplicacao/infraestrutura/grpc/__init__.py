from .cliente_identificacao_civil import (
    LigacaoIdentificacaoCivil,
    ErroOperacaoPortal,
    ServicoIndisponivel,
    obter_ligacao_identificacao_civil,
)
from .cliente_registo_criminal import LigacaoRegistoCriminal, obter_ligacao_registo_criminal
from .cliente_servico_militar import LigacaoServicoMilitar, obter_ligacao_servico_militar

__all__ = [
    "LigacaoIdentificacaoCivil",
    "LigacaoRegistoCriminal",
    "LigacaoServicoMilitar",
    "ErroOperacaoPortal",
    "ServicoIndisponivel",
    "obter_ligacao_identificacao_civil",
    "obter_ligacao_registo_criminal",
    "obter_ligacao_servico_militar",
]
