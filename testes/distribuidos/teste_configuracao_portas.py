from servicos.registo_criminal.aplicacao.configuracao.definicoes import definicoes as registo_criminal_definicoes
from servicos.identificacao_civil.aplicacao.configuracao.definicoes import definicoes as identificacao_civil_definicoes
from servicos.servico_militar.aplicacao.configuracao.definicoes import definicoes as servico_militar_definicoes
from portal.aplicacao.configuracao.definicoes import definicoes as portal_definicoes


def test_local_ports_are_unique() -> None:
    portas_web = {
        identificacao_civil_definicoes.porta_web,
        registo_criminal_definicoes.porta_web,
        servico_militar_definicoes.porta_web,
    }
    portas_grpc = {
        identificacao_civil_definicoes.porta_grpc,
        registo_criminal_definicoes.porta_grpc,
        servico_militar_definicoes.porta_grpc,
    }

    assert portas_web == {8001, 8002, 8003}
    assert portal_definicoes.porta_web == 8000
    assert portal_definicoes.porta_web not in portas_web
    assert portas_grpc == {50051, 50052, 50053}
    assert portas_web.isdisjoint(portas_grpc)
