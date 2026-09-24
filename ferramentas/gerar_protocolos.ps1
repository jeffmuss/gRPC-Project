param(
    [string]$ExecutavelPython = "python"
)

$ErrorActionPreference = "Stop"
$RaizProjecto = Split-Path -Parent $PSScriptRoot
$RaizProtocolos = Join-Path $RaizProjecto "contratos\protocolos"
$RaizSaida = Join-Path $RaizProjecto "contratos\gerados\python"

New-Item -ItemType Directory -Force -Path $RaizSaida | Out-Null
$FicheirosProtocolo = Get-ChildItem -Path $RaizProtocolos -Recurse -Filter "*.proto" | Sort-Object FullName

if ($FicheirosProtocolo.Count -eq 0) {
    throw "Nenhum ficheiro .proto foi encontrado em $RaizProtocolos"
}

& $ExecutavelPython -m grpc_tools.protoc `
    "-I$RaizProtocolos" `
    "--python_out=$RaizSaida" `
    "--grpc_python_out=$RaizSaida" `
    @($FicheirosProtocolo.FullName)

if ($LASTEXITCODE -ne 0) {
    throw "A geracao dos contratos terminou com o codigo $LASTEXITCODE"
}

$DirectoriosPacote = @($RaizSaida) + @(Get-ChildItem -Path $RaizSaida -Directory -Recurse | Select-Object -ExpandProperty FullName)
foreach ($Directorio in $DirectoriosPacote) {
    $FicheiroInicializacao = Join-Path $Directorio "__init__.py"
    if (-not (Test-Path $FicheiroInicializacao)) {
        New-Item -ItemType File -Path $FicheiroInicializacao | Out-Null
    }
}

Write-Host "Contratos gerados em $RaizSaida"
