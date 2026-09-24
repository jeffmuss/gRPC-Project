from __future__ import annotations

from datetime import date

from servicos.registo_criminal.aplicacao.casos_uso import ServicoRegistoCriminal, DadosRegisto
from servicos.registo_criminal.aplicacao.infraestrutura.base_dados.repositorio import SqlAlchemyRepositorioRegistoCriminal
from servicos.registo_criminal.aplicacao.dominio import DadosIdentidade
from servicos.registo_criminal.aplicacao.infraestrutura.base_dados.sessao import SessionLocal


class ValidadorIdentidadeDemonstracao:
    """Verificador limitado aos BI ficticios criados pelo seed da Identificacao Civil."""

    def procurar(self, numero_bi: str) -> DadosIdentidade | None:
        if numero_bi not in {"BI-DEMO-001", "BI-DEMO-002", "BI-DEMO-003"}:
            return None
        return DadosIdentidade(numero_bi, "Cidadao Ficticio", date(1990, 1, 1), "Ficticia")


REGISTOS_DEMONSTRACAO = (
    DadosRegisto("BI-DEMO-001", "PROC-DEMO-2025-001", "Infraccao ficticia",
                "Registo criado exclusivamente para demonstracao academica.",
                "Tribunal Ficticio de Maputo", date(2025, 3, 14),
                "Pena simulada integralmente cumprida", "CUMPRIDO"),
    DadosRegisto("BI-DEMO-002", "PROC-DEMO-2026-002", "Contravencao ficticia",
                "Caso sem correspondencia com pessoas ou processos reais.",
                "Tribunal Ficticio da Matola", date(2026, 2, 5),
                "Medida simulada de trabalho comunitario", "ACTIVO"),
)


def principal() -> None:
    with SessionLocal() as session:
        repositorio = SqlAlchemyRepositorioRegistoCriminal(session)
        servico = ServicoRegistoCriminal(repositorio, ValidadorIdentidadeDemonstracao())
        criados = 0
        for dados in REGISTOS_DEMONSTRACAO:
            if repositorio.obter_registo_por_processo(dados.numero_processo):
                continue
            servico.criar_registo(dados)
            criados += 1
    print(f"Dados ficticios do Registo Criminal: {criados} criado(s), restantes preservados.")


if __name__ == "__main__":
    principal()
