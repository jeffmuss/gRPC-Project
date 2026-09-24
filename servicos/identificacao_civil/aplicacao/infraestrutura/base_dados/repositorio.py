from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...casos_uso.servico_cidadaos import DUPLICATE_BI_MESSAGE
from ...dominio.entidades import Cidadao, Sexo
from ...dominio.excepcoes import CidadaoJaExiste, CidadaoNaoEncontrado
from .modelos import ModeloCidadao


class SqlAlchemyRepositorioCidadaos:
    def __init__(self, session: Session) -> None:
        self.sessao = session

    def adicionar(self, cidadao: Cidadao) -> Cidadao:
        model = self._para_modelo(cidadao)
        self.sessao.add(model)
        try:
            self.sessao.commit()
        except IntegrityError as error:
            self.sessao.rollback()
            raise CidadaoJaExiste(DUPLICATE_BI_MESSAGE) from error
        self.sessao.refresh(model)
        return self._para_entidade(model)

    def obter_por_id(self, cidadao_id: int) -> Cidadao | None:
        model = self.sessao.get(ModeloCidadao, cidadao_id)
        return self._para_entidade(model) if model else None

    def obter_por_bi(self, numero_bi: str) -> Cidadao | None:
        model = self.sessao.scalar(
            select(ModeloCidadao).where(ModeloCidadao.numero_bi == numero_bi)
        )
        return self._para_entidade(model) if model else None

    def listar(self, *, pagina: int, tamanho_pagina: int) -> tuple[list[Cidadao], int]:
        total = self.sessao.scalar(select(func.count()).select_from(ModeloCidadao)) or 0
        modelos = self.sessao.scalars(
            select(ModeloCidadao)
            .order_by(ModeloCidadao.nome_completo, ModeloCidadao.id)
            .offset((pagina - 1) * tamanho_pagina)
            .limit(tamanho_pagina)
        ).all()
        return [self._para_entidade(modelo) for modelo in modelos], total

    def actualizar(self, cidadao: Cidadao) -> Cidadao:
        model = self.sessao.get(ModeloCidadao, cidadao.id)
        if model is None:
            raise CidadaoNaoEncontrado("Cidadao nao encontrado.")
        for field in (
            "numero_bi",
            "nome_completo",
            "data_nascimento",
            "nacionalidade",
            "nome_pai",
            "nome_mae",
            "residencia",
        ):
            setattr(model, field, getattr(cidadao, field))
        model.sexo = cidadao.sexo.value
        try:
            self.sessao.commit()
        except IntegrityError as error:
            self.sessao.rollback()
            raise CidadaoJaExiste(DUPLICATE_BI_MESSAGE) from error
        self.sessao.refresh(model)
        return self._para_entidade(model)

    def ultima_actualizacao(self) -> datetime | None:
        return self.sessao.scalar(select(func.max(ModeloCidadao.data_actualizacao)))

    @staticmethod
    def _para_modelo(cidadao: Cidadao) -> ModeloCidadao:
        return ModeloCidadao(
            numero_bi=cidadao.numero_bi,
            nome_completo=cidadao.nome_completo,
            data_nascimento=cidadao.data_nascimento,
            sexo=cidadao.sexo.value,
            nacionalidade=cidadao.nacionalidade,
            nome_pai=cidadao.nome_pai,
            nome_mae=cidadao.nome_mae,
            residencia=cidadao.residencia,
        )

    @staticmethod
    def _para_entidade(model: ModeloCidadao) -> Cidadao:
        return Cidadao(
            id=model.id,
            numero_bi=model.numero_bi,
            nome_completo=model.nome_completo,
            data_nascimento=model.data_nascimento,
            sexo=Sexo(model.sexo),
            nacionalidade=model.nacionalidade,
            nome_pai=model.nome_pai,
            nome_mae=model.nome_mae,
            residencia=model.residencia,
            data_registo=model.data_registo,
            data_actualizacao=model.data_actualizacao,
        )
