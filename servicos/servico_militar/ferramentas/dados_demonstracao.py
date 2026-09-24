from datetime import date

from servicos.servico_militar.aplicacao.casos_uso import DadosRecenseamento, ServicoRecenseamentoMilitar
from servicos.servico_militar.aplicacao.infraestrutura.base_dados import SessaoLocal, SqlAlchemyRepositorioRecenseamentoMilitar


class LigacaoNula:
    def procurar(self, numero_bi):
        return None

    def consultar(self, numero_bi, pagina, tamanho_pagina):
        raise RuntimeError("Não utilizada na criação dos dados de demonstração.")


DADOS = (
    DadosRecenseamento("BI-DEMO-001", "RM-2026-0001", date(2026, 1, 15), "KaMpfumo", "Posto Central", "Exército", "APTO", "Dado exclusivamente fictício."),
    DadosRecenseamento("BI-DEMO-002", "RM-2026-0002", date(2026, 2, 10), "Matola", "Posto da Matola", "Força Aérea", "RECENSEADO", "Dado exclusivamente fictício."),
)


def principal() -> None:
    with SessaoLocal() as sessao:
        repositorio = SqlAlchemyRepositorioRecenseamentoMilitar(sessao)
        servico = ServicoRecenseamentoMilitar(repositorio, LigacaoNula(), LigacaoNula())
        criados = 0
        for dados in DADOS:
            if repositorio.obter_por_numero(dados.numero_recenseamento):
                continue
            servico.criar(dados)
            criados += 1
    print(f"Dados fictícios do Serviço Militar: {criados} criado(s), restantes preservados.")


if __name__ == "__main__":
    principal()
