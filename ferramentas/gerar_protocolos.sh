#!/usr/bin/env bash
set -euo pipefail

DIRECTORIO_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ_PROJECTO="$(cd "$DIRECTORIO_SCRIPT/.." && pwd)"
RAIZ_PROTOCOLOS="$RAIZ_PROJECTO/contratos/protocolos"
RAIZ_SAIDA="$RAIZ_PROJECTO/contratos/gerados/python"
EXECUTAVEL_PYTHON="${PYTHON:-python3}"

mkdir -p "$RAIZ_SAIDA"
mapfile -d '' FICHEIROS_PROTOCOLO < <(find "$RAIZ_PROTOCOLOS" -type f -name '*.proto' -print0 | sort -z)

if [[ ${#FICHEIROS_PROTOCOLO[@]} -eq 0 ]]; then
    echo "Nenhum ficheiro .proto foi encontrado em $RAIZ_PROTOCOLOS" >&2
    exit 1
fi

"$EXECUTAVEL_PYTHON" -m grpc_tools.protoc \
    -I"$RAIZ_PROTOCOLOS" \
    --python_out="$RAIZ_SAIDA" \
    --grpc_python_out="$RAIZ_SAIDA" \
    "${FICHEIROS_PROTOCOLO[@]}"

while IFS= read -r -d '' directory; do
    touch "$directory/__init__.py"
done < <(find "$RAIZ_SAIDA" -type d -print0)

echo "Contratos gerados em $RAIZ_SAIDA"
