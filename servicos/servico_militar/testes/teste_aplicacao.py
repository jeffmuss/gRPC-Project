from datetime import date

import pytest

from servicos.servico_militar.aplicacao.casos_uso import DadosRecenseamento, ServicoRecenseamentoMilitar
from servicos.servico_militar.aplicacao.dominio import JaExiste, NaoEncontrado
from servicos.servico_militar.aplicacao.infraestrutura.base_dados import SqlAlchemyRepositorioRecenseamentoMilitar


def _dados(**alteracoes):
    valores = dict(numero_bi="BI-TEST-001", numero_recenseamento="RM-TEST-001",
        data_recenseamento=date(2026, 3, 10), distrito="KaMpfumo",
        posto_recenseamento="Posto de Teste", ramo="Exército",
        situacao="RECENSEADO", observacoes="Fictício")
    valores.update(alteracoes)
    return DadosRecenseamento(**valores)


def test_criar_consultar_actualizar_e_listar(fabrica_sessoes, identidade_falsa, antecedentes_falsos) -> None:
    with fabrica_sessoes() as sessao:
        servico = ServicoRecenseamentoMilitar(SqlAlchemyRepositorioRecenseamentoMilitar(sessao), identidade_falsa, antecedentes_falsos)
        criado = servico.criar(_dados())
        assert criado.id == 1
        assert servico.consultar_situacao("bi-test-001").numero_recenseamento == "RM-TEST-001"
        actualizado = servico.actualizar(criado.id, _dados(situacao="APTO"))
        assert actualizado.situacao.value == "APTO"
        assert servico.listar(numero_bi="BI-TEST-001").total == 1
        assert servico.validar_identidade("BI-TEST-001").nome_completo == "Cidadão de Teste"
        assert servico.consultar_antecedentes("BI-TEST-001").itens[0].numero_processo == "PROC-TEST-001"


def test_impede_duplicados_e_reporta_bi_inexistente(fabrica_sessoes, identidade_falsa, antecedentes_falsos) -> None:
    with fabrica_sessoes() as sessao:
        servico = ServicoRecenseamentoMilitar(SqlAlchemyRepositorioRecenseamentoMilitar(sessao), identidade_falsa, antecedentes_falsos)
        servico.criar(_dados())
        with pytest.raises(JaExiste):
            servico.criar(_dados(numero_recenseamento="RM-OUTRO"))
        with pytest.raises(NaoEncontrado):
            servico.consultar_situacao("BI-INEXISTENTE")
