from fastapi.testclient import TestClient

from servicos.registo_criminal.aplicacao.principal_web import aplicacao


def test_health() -> None:
    response = TestClient(aplicacao).get("/saude")

    assert response.status_code == 200
    assert response.json() == {"servico": "registo_criminal", "estado": "operacional"}
