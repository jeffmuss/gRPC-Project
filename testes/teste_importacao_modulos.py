import importlib


def test_service_entry_points_import() -> None:
    for module_name in (
        "portal.aplicacao.principal_web",
        "servicos.identificacao_civil.aplicacao.principal_web",
        "servicos.identificacao_civil.aplicacao.principal_grpc",
        "servicos.registo_criminal.aplicacao.principal_web",
        "servicos.registo_criminal.aplicacao.principal_grpc",
        "servicos.servico_militar.aplicacao.principal_web",
        "servicos.servico_militar.aplicacao.principal_grpc",
    ):
        assert importlib.import_module(module_name) is not None
