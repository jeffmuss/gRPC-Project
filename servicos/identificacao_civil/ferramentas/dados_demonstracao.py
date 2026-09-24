from __future__ import annotations

from datetime import date

from servicos.identificacao_civil.aplicacao.casos_uso import DadosCidadao, ServicoCidadaos
from servicos.identificacao_civil.aplicacao.dominio.excepcoes import CidadaoJaExiste
from servicos.identificacao_civil.aplicacao.infraestrutura.base_dados.repositorio import (
    SqlAlchemyRepositorioCidadaos,
)
from servicos.identificacao_civil.aplicacao.infraestrutura.base_dados.sessao import SessionLocal


CIDADAOS_DEMONSTRACAO = (
    DadosCidadao(
        numero_bi="BI-DEMO-001",
        nome_completo="Ana Exemplo",
        data_nascimento=date(1992, 4, 15),
        sexo="F",
        nacionalidade="Mocambicana (ficticia)",
        nome_mae="Marta Exemplo",
        residencia="Maputo - endereco ficticio",
    ),
    DadosCidadao(
        numero_bi="BI-DEMO-002",
        nome_completo="Carlos Exemplo",
        data_nascimento=date(1987, 9, 3),
        sexo="M",
        nacionalidade="Mocambicana (ficticia)",
        nome_pai="Alberto Exemplo",
        residencia="Matola - endereco ficticio",
    ),
    DadosCidadao(
        numero_bi="BI-DEMO-003",
        nome_completo="Maria Exemplo",
        data_nascimento=date(2000, 1, 21),
        sexo="F",
        nacionalidade="Mocambicana (ficticia)",
        nome_pai="Joao Exemplo",
        nome_mae="Teresa Exemplo",
        residencia="Beira - endereco ficticio",
    ),
)


def principal() -> None:
    inseridos = 0
    with SessionLocal() as session:
        servico = ServicoCidadaos(SqlAlchemyRepositorioCidadaos(session))
        for dados in CIDADAOS_DEMONSTRACAO:
            try:
                servico.registar(dados)
                inseridos += 1
            except CidadaoJaExiste:
                continue
    print(f"Dados ficticios verificados: {inseridos} novo(s), {len(CIDADAOS_DEMONSTRACAO) - inseridos} existente(s).")


if __name__ == "__main__":
    principal()
