# Guia Prático de Execução — Apresentação do SISP

Este guia pressupõe que Python 3.12, o ambiente virtual e as dependências já foram instalados nos três computadores.

## 1. Identificar os computadores

| Computador | Executa | Portas |
|---|---|---|
| Computador 1 | Portal e Identificação Civil | 8000 e 50051 |
| Computador 2 | Registo Criminal | 50052 |
| Computador 3 | Serviço Militar | 50053 |

Em cada computador, abrir o PowerShell:

~~~powershell
ipconfig
~~~

Anotar o Endereço IPv4:

~~~text
IP_PC1 = ____________________
IP_PC2 = ____________________
IP_PC3 = ____________________
~~~

Confirmar que os três computadores estão na mesma rede privada, sem VPN e sem usar uma rede Wi-Fi de convidados.

## 2. Confirmar as configurações

### Computador 1

~~~powershell
cd D:/Documents/Projectos/sisp
if (-not (Test-Path portal/.env)) { Copy-Item portal/.env.rede.example portal/.env }
if (-not (Test-Path servicos/identificacao_civil/.env)) { Copy-Item servicos/identificacao_civil/.env.rede.example servicos/identificacao_civil/.env }
notepad portal/.env
notepad servicos/identificacao_civil/.env
~~~

No ficheiro portal/.env, confirmar:

~~~env
ANFITRIAO_WEB=0.0.0.0
PORTA_WEB=8000
ALVO_GRPC_IDENTIFICACAO_CIVIL=IP_PC1:50051
ALVO_GRPC_REGISTO_CRIMINAL=IP_PC2:50052
ALVO_GRPC_SERVICO_MILITAR=IP_PC3:50053
TEMPO_LIMITE_GRPC_SEGUNDOS=3
~~~

No ficheiro servicos/identificacao_civil/.env, confirmar:

~~~env
IP_SERVICO=IP_PC1
ANFITRIAO_GRPC=0.0.0.0
PORTA_GRPC=50051
URL_BASE_DADOS=sqlite:///./dados/identificacao_civil.db
ALVO_GRPC_REGISTO_CRIMINAL=IP_PC2:50052
TEMPO_LIMITE_GRPC_SEGUNDOS=3
~~~

### Computador 2

~~~powershell
cd C:/SISP
if (-not (Test-Path servicos/registo_criminal/.env)) { Copy-Item servicos/registo_criminal/.env.rede.example servicos/registo_criminal/.env }
notepad servicos/registo_criminal/.env
~~~

Confirmar:

~~~env
IP_SERVICO=IP_PC2
ANFITRIAO_GRPC=0.0.0.0
PORTA_GRPC=50052
URL_BASE_DADOS=sqlite:///./dados/registo_criminal.db
ALVO_GRPC_IDENTIFICACAO_CIVIL=IP_PC1:50051
TEMPO_LIMITE_GRPC_SEGUNDOS=3
~~~

### Computador 3

~~~powershell
cd C:/SISP
if (-not (Test-Path servicos/servico_militar/.env)) { Copy-Item servicos/servico_militar/.env.rede.example servicos/servico_militar/.env }
notepad servicos/servico_militar/.env
~~~

Confirmar:

~~~env
IP_SERVICO=IP_PC3
ANFITRIAO_GRPC=0.0.0.0
PORTA_GRPC=50053
URL_BASE_DADOS=sqlite:///./dados/servico_militar.db
ALVO_GRPC_IDENTIFICACAO_CIVIL=IP_PC1:50051
ALVO_GRPC_REGISTO_CRIMINAL=IP_PC2:50052
TEMPO_LIMITE_GRPC_SEGUNDOS=3
~~~

Substituir IP_PC1, IP_PC2 e IP_PC3 pelos endereços reais e guardar os ficheiros.

## 3. Confirmar as bases

### Computador 1

~~~powershell
Test-Path D:/Documents/Projectos/sisp/servicos/identificacao_civil/dados/identificacao_civil.db
~~~

### Computador 2

~~~powershell
Test-Path C:/SISP/servicos/registo_criminal/dados/registo_criminal.db
~~~

### Computador 3

~~~powershell
Test-Path C:/SISP/servicos/servico_militar/dados/servico_militar.db
~~~

O resultado deve ser True. Se for False, executar no computador correspondente.

### Criar a base da Identificação Civil

~~~powershell
cd D:/Documents/Projectos/sisp
New-Item -ItemType Directory -Force servicos/identificacao_civil/dados
./.venv/Scripts/python.exe -m alembic -c servicos/identificacao_civil/alembic.ini upgrade head
./.venv/Scripts/python.exe -m servicos.identificacao_civil.ferramentas.dados_demonstracao
~~~

### Criar a base do Registo Criminal

~~~powershell
cd C:/SISP
New-Item -ItemType Directory -Force servicos/registo_criminal/dados
./.venv/Scripts/python.exe -m alembic -c servicos/registo_criminal/alembic.ini upgrade head
./.venv/Scripts/python.exe -m servicos.registo_criminal.ferramentas.dados_demonstracao
~~~

### Criar a base do Serviço Militar

~~~powershell
cd C:/SISP
New-Item -ItemType Directory -Force servicos/servico_militar/dados
./.venv/Scripts/python.exe -m alembic -c servicos/servico_militar/alembic.ini upgrade head
./.venv/Scripts/python.exe -m servicos.servico_militar.ferramentas.dados_demonstracao
~~~

## 4. Iniciar os serviços gRPC

Manter os terminais abertos durante toda a apresentação.

### Computador 1 — Identificação Civil

~~~powershell
cd D:/Documents/Projectos/sisp
./.venv/Scripts/python.exe -m servicos.identificacao_civil.aplicacao.principal_grpc
~~~

Confirmar a porta 50051.

### Computador 2 — Registo Criminal

~~~powershell
cd C:/SISP
./.venv/Scripts/python.exe -m servicos.registo_criminal.aplicacao.principal_grpc
~~~

Confirmar a porta 50052.

### Computador 3 — Serviço Militar

~~~powershell
cd C:/SISP
./.venv/Scripts/python.exe -m servicos.servico_militar.aplicacao.principal_grpc
~~~

Confirmar a porta 50053.

## 5. Testar a comunicação

### Computador 1

~~~powershell
Test-NetConnection IP_PC2 -Port 50052
Test-NetConnection IP_PC3 -Port 50053
~~~

### Computador 2

~~~powershell
Test-NetConnection IP_PC1 -Port 50051
~~~

### Computador 3

~~~powershell
Test-NetConnection IP_PC1 -Port 50051
Test-NetConnection IP_PC2 -Port 50052
~~~

Substituir os IP e confirmar:

~~~text
TcpTestSucceeded : True
~~~

Não avançar enquanto algum resultado for False.

## 6. Iniciar o Portal no Computador 1

Abrir um segundo PowerShell:

~~~powershell
cd D:/Documents/Projectos/sisp
./.venv/Scripts/python.exe -m uvicorn portal.aplicacao.principal_web:aplicacao --host 0.0.0.0 --port 8000
~~~

Confirmar que o Uvicorn está activo na porta 8000.

## 7. Abrir o Portal

No navegador de qualquer computador:

~~~text
http://IP_PC1:8000
~~~

No Computador 1 também pode ser usado:

~~~text
http://127.0.0.1:8000
~~~

Confirmar que os três serviços aparecem activos.

## 8. Testar Identificação Civil

1. Aceder à Identificação Civil.
2. Pesquisar BI-DEMO-001.
3. Confirmar que aparece Ana Exemplo.
4. Abrir os detalhes.
5. Consultar os antecedentes.
6. Confirmar que aparece o processo devolvido pelo Registo Criminal.

## 9. Testar Registo Criminal

1. Voltar ao Portal.
2. Aceder ao Registo Criminal.
3. Pesquisar o histórico de BI-DEMO-001.
4. Confirmar PROC-DEMO-2025-001.
5. Abrir Validar identidade.
6. Pesquisar BI-DEMO-002.
7. Confirmar os dados devolvidos pela Identificação Civil.

## 10. Testar Serviço Militar

1. Voltar ao Portal.
2. Aceder ao Serviço Militar.
3. Confirmar que o histórico aparece imediatamente.
4. Consultar a situação de BI-DEMO-001.
5. Confirmar RM-2026-0001.
6. Validar a identidade de BI-DEMO-001.
7. Consultar os antecedentes de BI-DEMO-001.

## 11. Demonstrar indisponibilidade

No terminal do Registo Criminal, no Computador 2, premir Ctrl + C.

1. Actualizar o Portal.
2. Confirmar que o Registo Criminal aparece indisponível.
3. Confirmar que as funcionalidades continuam descritas no cartão.
4. Aceder ao Serviço Militar.
5. Confirmar que o painel e o histórico continuam disponíveis.
6. Confirmar que a consulta da situação militar funciona.
7. Confirmar que a validação de identidade funciona.
8. Consultar antecedentes e confirmar a indisponibilidade.

Restaurar o Registo Criminal:

~~~powershell
cd C:/SISP
./.venv/Scripts/python.exe -m servicos.registo_criminal.aplicacao.principal_grpc
~~~

Actualizar o Portal e confirmar o estado activo.

## 12. Encerrar

Premir Ctrl + C em cada terminal, nesta ordem:

1. Portal no Computador 1.
2. Serviço Militar no Computador 3.
3. Registo Criminal no Computador 2.
4. Identificação Civil no Computador 1.

## 13. Se algo falhar

1. Confirmar o IP com ipconfig.
2. Confirmar os IP nos ficheiros .env.
3. Confirmar que o terminal do serviço está aberto.
4. Confirmar a porta com Test-NetConnection.
5. Confirmar que a rede do Windows está como Privada.
6. Confirmar as regras da firewall.
7. Confirmar a base com Test-Path.
8. Reiniciar somente o componente que falhou.
