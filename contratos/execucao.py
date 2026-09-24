from __future__ import annotations

import sys
from pathlib import Path


PYTHON_GERADO = Path(__file__).resolve().parent / "gerados" / "python"


def disponibilizar_contratos_gerados() -> None:
    """Disponibiliza os modulos gerados sem depender do directorio de execucao."""
    gerados_path = str(PYTHON_GERADO)
    if gerados_path not in sys.path:
        sys.path.insert(0, gerados_path)
