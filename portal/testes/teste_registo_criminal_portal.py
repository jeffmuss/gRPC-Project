from fastapi.testclient import TestClient


FORMULARIO_REGISTO = {
    "numero_bi": "BI-TEST-001", "numero_processo": "PROC-PORTAL-001",
    "tipo_infracao": "Infraccao ficticia", "descricao": "Descricao de demonstracao",
    "tribunal": "Tribunal ficticio", "data_sentenca": "2025-03-10",
    "pena": "Pena ficticia", "estado": "ACTIVO",
}


def test_registo_criminal_crud_search_and_no_delete_ui(portal_client: TestClient) -> None:
    created = portal_client.post("/registo_criminal/registos", data=FORMULARIO_REGISTO, follow_redirects=False)
    assert created.status_code == 303
    detail = portal_client.get(created.headers["location"])
    assert "PROC-PORTAL-001" in detail.text
    searched = portal_client.get("/registo_criminal/registos", params={"numero_bi": "bi-test-001"})
    assert "Infraccao ficticia" in searched.text
    updated = portal_client.post("/registo_criminal/registos/1", data={**FORMULARIO_REGISTO, "estado": "CUMPRIDO"}, follow_redirects=False)
    assert updated.status_code == 303
    assert "CUMPRIDO" in portal_client.get("/registo_criminal/registos/1").text
    assert "elimin" not in portal_client.get("/registo_criminal/registos").text.lower()


def test_registo_criminal_validates_identity_through_identificacao_civil(portal_client: TestClient) -> None:
    found = portal_client.get("/registo_criminal/validar-identidade", params={"numero_bi": "BI-TEST-001"})
    assert found.status_code == 200
    assert "Cidadao de Teste" in found.text
    assert "Identidade confirmada" in found.text
    missing = portal_client.get("/registo_criminal/validar-identidade", params={"numero_bi": "BI-INEXISTENTE"})
    assert "Nao existe cidadao" in missing.text


def test_identificacao_civil_consults_registo_historico_criminal(portal_client: TestClient) -> None:
    portal_client.post("/identificacao/cidadaos", data={
        "numero_bi": "BI-TEST-001", "nome_completo": "Cidadao de Teste",
        "data_nascimento": "1990-01-01", "sexo": "M", "nacionalidade": "Ficticia",
        "nome_pai": "", "nome_mae": "", "residencia": "",
    })
    response = portal_client.get("/identificacao/cidadaos/1/antecedentes")
    assert response.status_code == 200
    assert "Identificacao Civil" in response.text
    assert "PROC-INTEROP-001" in response.text
