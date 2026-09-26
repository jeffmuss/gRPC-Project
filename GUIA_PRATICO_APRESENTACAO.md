# Guia Prático de Execução — Apresentação do SISP

## 0. Topologia

Cada computador executa **um microserviço** e **uma cópia do Portal**:

| Computador | Microserviço | Portal | Portas |
|---|---|---|---|
| Computador 1 | Identificação Civil | Sim | 50051 e 8000 |
| Computador 2 | Registo Criminal | Sim | 50052 e 8000 |
| Computador 3 | Serviço Militar | Sim | 50053 e 8000 |

~~~text
   Computador 1                 Computador 2                 Computador 3
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│ Portal :8000     │         │ Portal :8000     │         │ Portal :8000     │
│ Identificação    │◄──gRPC─►│ Registo Criminal │◄──gRPC─►│ Serviço Militar  │
│ Civil :50051     │         │ :50052           │         │ :50053           │
│ SQLite própria   │         │ SQLite própria   │         │ SQLite própria   │
└──────────────────┘         └──────────────────┘         └──────────────────┘
        ▲                                                          │
        └──────────────────────────gRPC────────────────────────────┘
~~~

Os três Portais não guardam dados: cada um consulta os três microserviços por gRPC. Por isso:

- o que for registado num computador aparece imediatamente nos outros;
- se um computador cair, os Portais dos outros continuam acessíveis.

## 1. Instalação (fazer antes do dia, nos 3 computadores)

A instalação é **igual nos três computadores**. Assim qualquer computador pode substituir outro.

### 1.1 Instalar o Python 3.12 (64 bits)

Descarregar de https://www.python.org/downloads/release/python-31210/ (Windows installer 64-bit).

Durante a instalação, marcar **Add python.exe to PATH** e **py launcher**.

Não usar Python 3.14: a versão do grpcio usada pelo projecto não o suporta.

Confirmar:

~~~powershell
py -3.12 --version
~~~

Atenção: se o computador tiver o MySQL Shell, o comando `python` pode abrir o Python do MySQL, que não funciona. Usar sempre `py -3.12` ou `./.venv/Scripts/python.exe`.

### 1.2 Copiar o projecto

Colocar a pasta completa do projecto em **C:/SISP** nos três computadores, por git clone ou por pen USB. As pastas `contratos`, `portal` e `servicos` são todas necessárias em cada computador.

### 1.3 Criar o ambiente virtual e instalar as dependências

~~~powershell
cd C:/SISP
py -3.12 -m venv .venv
./.venv/Scripts/python.exe -m pip install -r servicos/identificacao_civil/requirements.txt -r servicos/registo_criminal/requirements.txt -r servicos/servico_militar/requirements.txt -r portal/requirements.txt
~~~

### 1.4 Confirmar que está tudo bem

~~~powershell
cd C:/SISP
./.venv/Scripts/python.exe -m pytest -q
~~~

O resultado deve terminar com `35 passed`.

### Não é necessário instalar

- Servidor de base de dados: o SQLite já vem com o Python.
- Compilador protoc: os contratos gRPC já estão gerados em `contratos/gerados/python`.
- Docker, Node.js ou servidor web: o Portal usa o Uvicorn, instalado pelo pip.

### Se na faculdade não houver Internet

Num computador com Internet e com Python 3.12, descarregar os pacotes para uma pasta:

~~~powershell
cd C:/SISP
py -3.12 -m pip download -d pacotes -r servicos/identificacao_civil/requirements.txt -r servicos/registo_criminal/requirements.txt -r servicos/servico_militar/requirements.txt -r portal/requirements.txt
~~~

Copiar o instalador do Python e a pasta `C:/SISP` (já com a pasta `pacotes`) para a pen. Em cada computador, instalar sem Internet:

~~~powershell
cd C:/SISP
py -3.12 -m venv .venv
./.venv/Scripts/python.exe -m pip install --no-index --find-links pacotes -r servicos/identificacao_civil/requirements.txt -r servicos/registo_criminal/requirements.txt -r servicos/servico_militar/requirements.txt -r portal/requirements.txt
~~~

## 2. Preparar a rede (no dia)

### 2.1 Mesma rede

Ligar os três computadores à mesma rede. As redes Wi-Fi das faculdades (eduroam, convidados) costumam **bloquear a comunicação entre computadores**. Levar alternativa:

- hotspot de um telemóvel, ou
- um router ou switch com cabos de rede.

Sem VPN activa.

### 2.2 Anotar os IP

Em cada computador:

~~~powershell
ipconfig
~~~

Anotar o Endereço IPv4 do adaptador ligado à rede:

~~~text
IP_PC1 = ____________________
IP_PC2 = ____________________
IP_PC3 = ____________________
~~~

### 2.3 Rede privada e firewall (PowerShell como Administrador, nos 3 computadores)

~~~powershell
Get-NetConnectionProfile
Set-NetConnectionProfile -InterfaceAlias "Wi-Fi" -NetworkCategory Private
New-NetFirewallRule -DisplayName "SISP" -Direction Inbound -Protocol TCP -LocalPort 8000,50051,50052,50053 -Action Allow -Profile Private
~~~

Substituir "Wi-Fi" pelo nome mostrado em `Get-NetConnectionProfile` (por exemplo "Ethernet").

Na primeira execução do Python, se o Windows perguntar, permitir o acesso em **Redes privadas**.

## 3. Configurar os ficheiros .env

### Nos três computadores — Portal

~~~powershell
cd C:/SISP
Copy-Item portal/.env.rede.example portal/.env
notepad portal/.env
~~~

O ficheiro portal/.env é **igual nos três computadores**:

~~~env
AMBIENTE_APLICACAO=rede
ANFITRIAO_WEB=0.0.0.0
PORTA_WEB=8000
ALVO_GRPC_IDENTIFICACAO_CIVIL=IP_PC1:50051
ALVO_GRPC_REGISTO_CRIMINAL=IP_PC2:50052
ALVO_GRPC_SERVICO_MILITAR=IP_PC3:50053
TEMPO_LIMITE_GRPC_SEGUNDOS=3
~~~

### Computador 1 — Identificação Civil

~~~powershell
cd C:/SISP
Copy-Item servicos/identificacao_civil/.env.rede.example servicos/identificacao_civil/.env
notepad servicos/identificacao_civil/.env
~~~

~~~env
IP_SERVICO=IP_PC1
ANFITRIAO_GRPC=0.0.0.0
PORTA_GRPC=50051
URL_BASE_DADOS=sqlite:///./dados/identificacao_civil.db
ALVO_GRPC_REGISTO_CRIMINAL=IP_PC2:50052
TEMPO_LIMITE_GRPC_SEGUNDOS=3
~~~

### Computador 2 — Registo Criminal

~~~powershell
cd C:/SISP
Copy-Item servicos/registo_criminal/.env.rede.example servicos/registo_criminal/.env
notepad servicos/registo_criminal/.env
~~~

~~~env
IP_SERVICO=IP_PC2
ANFITRIAO_GRPC=0.0.0.0
PORTA_GRPC=50052
URL_BASE_DADOS=sqlite:///./dados/registo_criminal.db
ALVO_GRPC_IDENTIFICACAO_CIVIL=IP_PC1:50051
TEMPO_LIMITE_GRPC_SEGUNDOS=3
~~~

### Computador 3 — Serviço Militar

~~~powershell
cd C:/SISP
Copy-Item servicos/servico_militar/.env.rede.example servicos/servico_militar/.env
notepad servicos/servico_militar/.env
~~~

~~~env
IP_SERVICO=IP_PC3
ANFITRIAO_GRPC=0.0.0.0
PORTA_GRPC=50053
URL_BASE_DADOS=sqlite:///./dados/servico_militar.db
ALVO_GRPC_IDENTIFICACAO_CIVIL=IP_PC1:50051
ALVO_GRPC_REGISTO_CRIMINAL=IP_PC2:50052
TEMPO_LIMITE_GRPC_SEGUNDOS=3
~~~

Substituir IP_PC1, IP_PC2 e IP_PC3 pelos endereços reais e guardar.

## 4. Criar as bases

Cada base só existe no computador do seu microserviço.

### Computador 1

~~~powershell
cd C:/SISP
./.venv/Scripts/python.exe -m alembic -c servicos/identificacao_civil/alembic.ini upgrade head
./.venv/Scripts/python.exe -m servicos.identificacao_civil.ferramentas.dados_demonstracao
~~~

### Computador 2

~~~powershell
cd C:/SISP
./.venv/Scripts/python.exe -m alembic -c servicos/registo_criminal/alembic.ini upgrade head
./.venv/Scripts/python.exe -m servicos.registo_criminal.ferramentas.dados_demonstracao
~~~

### Computador 3

~~~powershell
cd C:/SISP
./.venv/Scripts/python.exe -m alembic -c servicos/servico_militar/alembic.ini upgrade head
./.venv/Scripts/python.exe -m servicos.servico_militar.ferramentas.dados_demonstracao
~~~

## 5. Iniciar os microserviços gRPC

Manter os terminais abertos durante toda a apresentação.

| Computador | Comando | Mensagem esperada |
|---|---|---|
| 1 | `./.venv/Scripts/python.exe -m servicos.identificacao_civil.aplicacao.principal_grpc` | Identificacao Civil gRPC activa em 0.0.0.0:50051 |
| 2 | `./.venv/Scripts/python.exe -m servicos.registo_criminal.aplicacao.principal_grpc` | Registo Criminal gRPC activo em 0.0.0.0:50052 |
| 3 | `./.venv/Scripts/python.exe -m servicos.servico_militar.aplicacao.principal_grpc` | Serviço Militar gRPC activo em 0.0.0.0:50053 |

Executar sempre a partir de `C:/SISP`.

## 6. Testar a comunicação

### Computador 1

~~~powershell
Test-NetConnection IP_PC2 -Port 50052
Test-NetConnection IP_PC3 -Port 50053
~~~

### Computador 2

~~~powershell
Test-NetConnection IP_PC1 -Port 50051
Test-NetConnection IP_PC3 -Port 50053
~~~

### Computador 3

~~~powershell
Test-NetConnection IP_PC1 -Port 50051
Test-NetConnection IP_PC2 -Port 50052
~~~

Todos devem mostrar `TcpTestSucceeded : True`. Não avançar enquanto algum for False.

## 7. Iniciar o Portal nos três computadores

Em cada computador, abrir um segundo PowerShell:

~~~powershell
cd C:/SISP
./.venv/Scripts/python.exe -m uvicorn portal.aplicacao.principal_web:aplicacao --host 0.0.0.0 --port 8000
~~~

Em cada computador, abrir no navegador:

~~~text
http://127.0.0.1:8000
~~~

Os três painéis devem mostrar os três serviços **operacionais**.

## 8. Demonstração: o que acontece num computador reflecte-se nos outros

Colocar os três ecrãs lado a lado.

| Passo | Onde | Acção | Confirmar noutro computador |
|---|---|---|---|
| 1 | Computador 2 | Identificação Civil → Registar cidadão: BI **BI-APRES-001**, Maria Apresentação, 2000-05-10, F, Moçambicana | No Computador 3, Identificação Civil → Pesquisar BI-APRES-001: aparece Maria Apresentação |
| 2 | Computador 3 | Registo Criminal → Novo registo: BI-APRES-001, processo **PROC-APRES-2026-001**, estado ACTIVO | No Computador 1, abrir Maria Apresentação → Antecedentes: aparece PROC-APRES-2026-001 |
| 3 | Computador 1 | Serviço Militar → Novo recenseamento: BI-APRES-001, número **RM-2026-0100**, situação RECENSEADO | No Computador 2, Serviço Militar → lista: aparece RM-2026-0100 |
| 4 | Computador 2 | Serviço Militar → Validar identidade BI-APRES-001 | Dados vindos da Identificação Civil (Computador 1) |
| 5 | Computador 2 | Serviço Militar → Consultar antecedentes BI-APRES-001 | Dados vindos do Registo Criminal (Computador 2) através do Serviço Militar (Computador 3) |

Explicação para o júri: o cidadão foi registado a partir do Computador 2, mas foi gravado na base do Computador 1, através de gRPC. Os outros Portais apenas o consultam.

Dados fictícios já existentes: BI-DEMO-001 (Ana Exemplo, PROC-DEMO-2025-001, RM-2026-0001) e BI-DEMO-002.

## 9. Demonstração de tolerância a falhas

### 9.1 Queda do Registo Criminal

No Computador 2, no terminal do Registo Criminal, premir Ctrl + C.

1. Em qualquer computador, actualizar o Portal: o Registo Criminal aparece **indisponível** e os outros dois continuam operacionais.
2. Serviço Militar → Consultar situação de BI-DEMO-001: funciona.
3. Serviço Militar → Validar identidade de BI-DEMO-001: funciona.
4. Serviço Militar → Consultar antecedentes: mostra indisponibilidade, sem bloquear o sistema.

Restaurar no Computador 2:

~~~powershell
./.venv/Scripts/python.exe -m servicos.registo_criminal.aplicacao.principal_grpc
~~~

Actualizar o Portal: volta a operacional sem reiniciar mais nada.

### 9.2 Queda completa de um computador

Desligar o cabo, ou o Wi-Fi, do Computador 1. Assim caem a Identificação Civil e o Portal desse computador.

1. Nos Computadores 2 e 3, os Portais continuam acessíveis.
2. A Identificação Civil aparece indisponível.
3. Registo Criminal e Serviço Militar continuam a listar, criar e consultar os seus dados.
4. Apenas a validação de identidade fica indisponível.

Voltar a ligar a rede do Computador 1 e actualizar os Portais.

## 10. Encerrar

Premir Ctrl + C em cada terminal, nesta ordem:

1. Portais nos três computadores.
2. Serviço Militar no Computador 3.
3. Registo Criminal no Computador 2.
4. Identificação Civil no Computador 1.

## 11. Se algo falhar

| Sintoma | Verificar |
|---|---|
| `'.' is not recognized` ou `The system cannot find the path specified` | Está no CMD, não no PowerShell. Escrever `powershell` e repetir, ou usar `.venv\Scripts\python.exe` com barras invertidas |
| `python` dá erro de `encodings` | Está a usar o Python do MySQL Shell. Usar `./.venv/Scripts/python.exe` |
| Serviço aparece indisponível | O terminal do serviço está aberto? O IP no `portal/.env` está correcto? |
| `TcpTestSucceeded : False` | Rede Privada, regra de firewall, mesma rede, rede da faculdade a isolar computadores (usar hotspot) |
| IP mudou | Correr `ipconfig`, corrigir os `.env` e reiniciar só o Portal ou o serviço afectado |
| Porta ocupada | `Get-NetTCPConnection -State Listen -LocalPort 8000,50051,50052,50053` |
| Base em falta | Repetir a secção 4 no computador correspondente |
| "Já existe" ao registar BI-APRES-001 | Já foi registado num ensaio. Usar BI-APRES-002 |
