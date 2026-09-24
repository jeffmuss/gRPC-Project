from fastapi.testclient import TestClient

from servicos.servico_militar.aplicacao.principal_web import aplicacao


def test_saude() -> None:
    response = TestClient(aplicacao).get("/saude")

    assert response.status_code == 200
    assert response.json() == {"servico": "servico_militar", "estado": "operacional"}
