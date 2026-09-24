from __future__ import annotations

import importlib
import sys
from pathlib import Path

from grpc_tools import protoc


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROTO_ROOT = PROJECT_ROOT / "contratos" / "protocolos"


def test_contratos_generate_and_import(tmp_path: Path) -> None:
    proto_files = sorted(PROTO_ROOT.glob("**/*.proto"))
    assert len(proto_files) == 4

    arguments = [
        "grpc_tools.protoc",
        f"-I{PROTO_ROOT}",
        f"--python_out={tmp_path}",
        f"--grpc_python_out={tmp_path}",
        *(str(path) for path in proto_files),
    ]
    assert protoc.main(arguments) == 0

    sys.path.insert(0, str(tmp_path))
    try:
        for module_name in (
            "comum.v1.comum_pb2",
            "comum.v1.comum_pb2_grpc",
            "identificacao_civil.v1.identificacao_civil_pb2",
            "identificacao_civil.v1.identificacao_civil_pb2_grpc",
            "registo_criminal.v1.registo_criminal_pb2",
            "registo_criminal.v1.registo_criminal_pb2_grpc",
            "servico_militar.v1.servico_militar_pb2",
            "servico_militar.v1.servico_militar_pb2_grpc",
        ):
            importlib.import_module(module_name)
    finally:
        sys.path.remove(str(tmp_path))

