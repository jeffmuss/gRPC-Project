from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from servicos.servico_militar.aplicacao.configuracao.definicoes import definicoes
from servicos.servico_militar.aplicacao.infraestrutura.base_dados.base import Base
from servicos.servico_militar.aplicacao.infraestrutura.base_dados import modelos  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
config.set_main_option("sqlalchemy.url", definicoes.url_base_dados_resolvida)
target_metadata = Base.metadata


def executar_offline() -> None:
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata,
                      literal_binds=True, dialect_opts={"paramstyle": "named"}, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()


def executar_online() -> None:
    ligacao = engine_from_config(config.get_section(config.config_ini_section, {}),
                                 prefix="sqlalchemy.", poolclass=pool.NullPool)
    with ligacao.connect() as conexao:
        context.configure(connection=conexao, target_metadata=target_metadata, render_as_batch=True)
        with context.begin_transaction():
            context.run_migrations()


executar_offline() if context.is_offline_mode() else executar_online()
