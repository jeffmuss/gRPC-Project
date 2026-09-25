# Mapa Rápido dos Pontos Focais do SISP

## Arquitectura

Navegador
   │ HTTP :8000
   ▼
Portal SISP
   ├── gRPC :50051 ── Identificação Civil ── SQLite própria
   ├── gRPC :50052 ── Registo Criminal ───── SQLite própria
   └── gRPC :50053 ── Serviço Militar ────── SQLite própria


O Portal não abre bases SQLite. Comunica com os três serviços exclusivamente através dos clientes gRPC.

## Configurações

Ficheiros preenchidos em cada computador:


portal/.env
servicos/identificacao_civil/.env
servicos/registo_criminal/.env
servicos/servico_militar/.env


Modelos fornecidos pelo projecto:


portal/.env.example
portal/.env.rede.example
servicos/*/.env.example
servicos/*/.env.rede.example


Código que lê as configurações:

portal/aplicacao/configuracao/definicoes.py
servicos/identificacao_civil/aplicacao/configuracao/definicoes.py
servicos/registo_criminal/aplicacao/configuracao/definicoes.py
servicos/servico_militar/aplicacao/configuracao/definicoes.py

Estes ficheiros usam python-dotenv, validam portas e disponibilizam o objecto definicoes.

## Utilização das configurações gRPC

### Portal

portal/aplicacao/infraestrutura/grpc/cliente_identificacao_civil.py
portal/aplicacao/infraestrutura/grpc/cliente_registo_criminal.py
portal/aplicacao/infraestrutura/grpc/cliente_servico_militar.py


Usam os três ALVO_GRPC e TEMPO_LIMITE_GRPC_SEGUNDOS.

### Identificação Civil

servicos/identificacao_civil/aplicacao/principal_grpc.py
servicos/identificacao_civil/aplicacao/infraestrutura/grpc/servico.py
servicos/identificacao_civil/aplicacao/infraestrutura/grpc/cliente_registo_criminal.py


principal_grpc.py usa ANFITRIAO_GRPC e PORTA_GRPC. O cliente usa ALVO_GRPC_REGISTO_CRIMINAL.

### Registo Criminal


servicos/registo_criminal/aplicacao/principal_grpc.py
servicos/registo_criminal/aplicacao/infraestrutura/grpc/servico.py
servicos/registo_criminal/aplicacao/infraestrutura/grpc/cliente_identificacao_civil.py


O cliente usa ALVO_GRPC_IDENTIFICACAO_CIVIL para validar cidadãos.

### Serviço Militar


servicos/servico_militar/aplicacao/principal_grpc.py
servicos/servico_militar/aplicacao/infraestrutura/grpc/servico.py
servicos/servico_militar/aplicacao/infraestrutura/grpc/cliente_identificacao_civil.py
servicos/servico_militar/aplicacao/infraestrutura/grpc/cliente_registo_criminal.py


Usa os alvos da Identificação Civil e do Registo Criminal.

## Contratos gRPC

Fontes editáveis:

contratos/protocolos/comum/v1/comum.proto
contratos/protocolos/identificacao_civil/v1/identificacao_civil.proto
contratos/protocolos/registo_criminal/v1/registo_criminal.proto
contratos/protocolos/servico_militar/v1/servico_militar.proto


Código Python gerado:

contratos/gerados/python/**/**_pb2.py
contratos/gerados/python/**/**_pb2_grpc.py


Scripts de geração:

ferramentas/gerar_protocolos.ps1
ferramentas/gerar_protocolos.sh

contratos/execucao.py adiciona contratos/gerados/python ao caminho de importação.

## Portal

portal/aplicacao/principal_web.py                  Inicialização FastAPI
portal/aplicacao/web/rotas/portal.py               Portal e Identificação Civil
portal/aplicacao/web/rotas/registo_criminal.py     Rotas criminais
portal/aplicacao/web/rotas/servico_militar.py      Rotas militares
portal/aplicacao/web/modelos/                      Páginas Jinja2
portal/aplicacao/web/modelos/base.html             Cabeçalho e rodapé
portal/aplicacao/web/estaticos/estilo.css          Aspecto visual


## Organização interna de cada serviço

aplicacao/dominio/          Entidades, validações, excepções e interfaces
aplicacao/casos_uso/        Regras e operações da aplicação
aplicacao/infraestrutura/   SQLite, SQLAlchemy, clientes e servidores gRPC
aplicacao/configuracao/     Leitura do .env
aplicacao/principal_grpc.py Arranque do servidor gRPC
ferramentas/                Dados fictícios
migracoes/                  Evolução da base com Alembic
testes/                     Testes do serviço


## Bases de dados

servicos/identificacao_civil/dados/identificacao_civil.db
servicos/registo_criminal/dados/registo_criminal.db
servicos/servico_militar/dados/servico_militar.db


Pontos principais:

servicos/*/aplicacao/infraestrutura/base_dados/sessao.py       Ligação e sessões
servicos/*/aplicacao/infraestrutura/base_dados/modelos.py      Modelos SQLAlchemy
servicos/*/aplicacao/infraestrutura/base_dados/repositorio.py  Consultas e gravações

As bases não são partilhadas e não são enviadas ao Git.

## Migrações e dados fictícios

servicos/*/alembic.ini
servicos/*/migracoes/env.py
servicos/*/migracoes/versoes/
servicos/*/ferramentas/dados_demonstracao.py


BI comuns:

BI-DEMO-001
BI-DEMO-002


## Testes

servicos/*/testes/                    Testes de cada serviço
portal/testes/                        Testes da interface e degradação
testes/contratos/                     Geração dos contratos
testes/distribuidos/                  Configuração distribuída
testes/teste_importacao_modulos.py    Importação dos módulos


Executar todos:

..venvScriptspython.exe -m pytest -p no:cacheprovider


## Fluxos de interoperabilidade


Identificação Civil → Registo Criminal
Consultar antecedentes criminais

Registo Criminal → Identificação Civil
Validar identidade do cidadão

Serviço Militar → Identificação Civil
Validar identidade do cidadão

Serviço Militar → Registo Criminal
Consultar antecedentes criminais

As restantes operações são locais ao serviço correspondente.
