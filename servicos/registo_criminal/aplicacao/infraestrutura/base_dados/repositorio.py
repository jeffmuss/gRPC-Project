from dataclasses import replace
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ...dominio.entidades import RegistoCriminal, EstadoRegisto
from ...dominio.excepcoes import JaExiste, NaoEncontrado
from .modelos import ModeloRegistoCriminal

class SqlAlchemyRepositorioRegistoCriminal:
    def __init__(self, session: Session): self.sessao = session
    @staticmethod
    def _record(m): return RegistoCriminal(m.numero_bi,m.numero_processo,m.tipo_infracao,m.descricao,m.tribunal,m.data_sentenca,m.pena,EstadoRegisto(m.estado),m.id,m.data_registo,m.data_actualizacao)
    def adicionar_registo(self, r):
        m=ModeloRegistoCriminal(numero_bi=r.numero_bi,numero_processo=r.numero_processo,tipo_infracao=r.tipo_infracao,descricao=r.descricao,tribunal=r.tribunal,data_sentenca=r.data_sentenca,pena=r.pena,estado=r.estado.value); self.sessao.add(m)
        try: self.sessao.commit()
        except IntegrityError as e: self.sessao.rollback(); raise JaExiste("Ja existe um registo com este numero de processo.") from e
        self.sessao.refresh(m); return self._record(m)
    def obter_registo(self, record_id):
        m=self.sessao.get(ModeloRegistoCriminal,record_id); return self._record(m) if m else None
    def obter_registo_por_processo(self, number):
        m=self.sessao.scalar(select(ModeloRegistoCriminal).where(ModeloRegistoCriminal.numero_processo==number)); return self._record(m) if m else None
    def listar_registos(self,page,page_size,numero_bi=None):
        condition=ModeloRegistoCriminal.numero_bi==numero_bi if numero_bi else None
        count=select(func.count()).select_from(ModeloRegistoCriminal); query=select(ModeloRegistoCriminal)
        if condition is not None: count=count.where(condition); query=query.where(condition)
        total=self.sessao.scalar(count) or 0; models=self.sessao.scalars(query.order_by(ModeloRegistoCriminal.data_sentenca.desc(),ModeloRegistoCriminal.id.desc()).offset((page-1)*page_size).limit(page_size)).all(); return [self._record(m) for m in models],total
    def actualizar_registo(self,r):
        m=self.sessao.get(ModeloRegistoCriminal,r.id)
        if not m: raise NaoEncontrado("Registo registo_criminal nao encontrado.")
        for f in ("numero_bi","numero_processo","tipo_infracao","descricao","tribunal","data_sentenca","pena"): setattr(m,f,getattr(r,f))
        m.estado=r.estado.value
        try: self.sessao.commit()
        except IntegrityError as e: self.sessao.rollback(); raise JaExiste("Ja existe um registo com este numero de processo.") from e
        self.sessao.refresh(m); return self._record(m)
    def ultima_actualizacao_registo(self): return self.sessao.scalar(select(func.max(ModeloRegistoCriminal.data_actualizacao)))
