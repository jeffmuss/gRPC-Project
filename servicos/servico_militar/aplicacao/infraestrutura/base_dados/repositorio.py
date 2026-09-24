from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...dominio.entidades import RecenseamentoMilitar, SituacaoMilitar
from ...dominio.excepcoes import JaExiste, NaoEncontrado
from .modelos import ModeloRecenseamentoMilitar


class SqlAlchemyRepositorioRecenseamentoMilitar:
    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao

    @staticmethod
    def _entidade(modelo: ModeloRecenseamentoMilitar) -> RecenseamentoMilitar:
        return RecenseamentoMilitar(
            numero_bi=modelo.numero_bi,
            numero_recenseamento=modelo.numero_recenseamento,
            data_recenseamento=modelo.data_recenseamento,
            distrito=modelo.distrito,
            posto_recenseamento=modelo.posto_recenseamento,
            ramo=modelo.ramo,
            situacao=SituacaoMilitar(modelo.situacao),
            observacoes=modelo.observacoes,
            id=modelo.id,
            data_registo=modelo.data_registo,
            data_actualizacao=modelo.data_actualizacao,
        )

    def adicionar(self, item: RecenseamentoMilitar) -> RecenseamentoMilitar:
        modelo = ModeloRecenseamentoMilitar(
            numero_bi=item.numero_bi,
            numero_recenseamento=item.numero_recenseamento,
            data_recenseamento=item.data_recenseamento,
            distrito=item.distrito,
            posto_recenseamento=item.posto_recenseamento,
            ramo=item.ramo,
            situacao=item.situacao.value,
            observacoes=item.observacoes,
        )
        self.sessao.add(modelo)
        try:
            self.sessao.commit()
        except IntegrityError as erro:
            self.sessao.rollback()
            raise JaExiste("O BI ou número de recenseamento já está registado.") from erro
        self.sessao.refresh(modelo)
        return self._entidade(modelo)

    def obter(self, item_id: int) -> RecenseamentoMilitar | None:
        modelo = self.sessao.get(ModeloRecenseamentoMilitar, item_id)
        return self._entidade(modelo) if modelo else None

    def obter_por_bi(self, numero_bi: str) -> RecenseamentoMilitar | None:
        modelo = self.sessao.scalar(select(ModeloRecenseamentoMilitar).where(ModeloRecenseamentoMilitar.numero_bi == numero_bi))
        return self._entidade(modelo) if modelo else None

    def obter_por_numero(self, numero_recenseamento: str) -> RecenseamentoMilitar | None:
        modelo = self.sessao.scalar(select(ModeloRecenseamentoMilitar).where(ModeloRecenseamentoMilitar.numero_recenseamento == numero_recenseamento))
        return self._entidade(modelo) if modelo else None

    def listar(self, pagina: int, tamanho_pagina: int, numero_bi: str | None = None):
        contagem = select(func.count()).select_from(ModeloRecenseamentoMilitar)
        consulta = select(ModeloRecenseamentoMilitar)
        if numero_bi:
            condicao = ModeloRecenseamentoMilitar.numero_bi == numero_bi
            contagem = contagem.where(condicao)
            consulta = consulta.where(condicao)
        total = self.sessao.scalar(contagem) or 0
        modelos = self.sessao.scalars(
            consulta.order_by(ModeloRecenseamentoMilitar.data_recenseamento.desc(), ModeloRecenseamentoMilitar.id.desc())
            .offset((pagina - 1) * tamanho_pagina).limit(tamanho_pagina)
        ).all()
        return [self._entidade(modelo) for modelo in modelos], total

    def actualizar(self, item: RecenseamentoMilitar) -> RecenseamentoMilitar:
        modelo = self.sessao.get(ModeloRecenseamentoMilitar, item.id)
        if not modelo:
            raise NaoEncontrado("Recenseamento militar não encontrado.")
        for campo in ("numero_bi", "numero_recenseamento", "data_recenseamento", "distrito", "posto_recenseamento", "ramo", "observacoes"):
            setattr(modelo, campo, getattr(item, campo))
        modelo.situacao = item.situacao.value
        try:
            self.sessao.commit()
        except IntegrityError as erro:
            self.sessao.rollback()
            raise JaExiste("O BI ou número de recenseamento já está registado.") from erro
        self.sessao.refresh(modelo)
        return self._entidade(modelo)

    def ultima_actualizacao(self):
        return self.sessao.scalar(select(func.max(ModeloRecenseamentoMilitar.data_actualizacao)))
