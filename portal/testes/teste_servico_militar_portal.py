from fastapi.testclient import TestClient


FORMULARIO = {
    "numero_bi": "BI-TEST-001", "numero_recenseamento": "RM-TEST-001",
    "data_recenseamento": "2026-03-10", "distrito": "KaMpfumo",
    "posto_recenseamento": "Posto de Teste", "ramo": "Exército",
    "situacao": "RECENSEADO", "observacoes": "Dados fictícios",
}


def test_recenseamento_crud_pesquisa_e_sem_eliminacao(portal_client: TestClient) -> None:
    criado = portal_client.post("/servico_militar/recenseamentos", data=FORMULARIO, follow_redirects=False)
    assert criado.status_code == 303
    assert "RM-TEST-001" in portal_client.get(criado.headers["location"]).text
    pesquisa = portal_client.get("/servico_militar/consultar-situacao", params={"numero_bi": "bi-test-001"})
    assert pesquisa.status_code == 200
    assert "RECENSEADO" in pesquisa.text
    actualizado = portal_client.post("/servico_militar/recenseamentos/1",
        data={**FORMULARIO, "situacao": "APTO"}, follow_redirects=False)
    assert actualizado.status_code == 303
    assert "APTO" in portal_client.get("/servico_militar/recenseamentos/1").text
    assert "elimin" not in portal_client.get("/servico_militar/recenseamentos").text.lower()


def test_servico_militar_valida_identidade_e_consulta_antecedentes(portal_client: TestClient) -> None:
    identidade = portal_client.get("/servico_militar/validar-identidade", params={"numero_bi": "BI-TEST-001"})
    assert identidade.status_code == 200
    assert "Cidadao de Teste" in identidade.text
    assert "Identidade confirmada" in identidade.text
    antecedentes = portal_client.get("/servico_militar/consultar-antecedentes", params={"numero_bi": "BI-TEST-001"})
    assert antecedentes.status_code == 200
    assert "PROC-MILITAR-001" in antecedentes.text
