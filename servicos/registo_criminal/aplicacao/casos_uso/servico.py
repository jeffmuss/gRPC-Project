from __future__ import annotations
from dataclasses import replace
from .dados_transferencia import Pagina, DadosRegisto
from ..dominio.entidades import RegistoCriminal, DadosIdentidade
from ..dominio.excepcoes import JaExiste, NaoEncontrado, ErroValidacao
from ..dominio.repositorios import RepositorioRegistoCriminal, ValidadorIdentidade
from ..dominio.validacao import normalize_bi, normalize_process, record_status, required, sentence_date


class ServicoRegistoCriminal:
    def __init__(self, repositorio: RepositorioRegistoCriminal, identidade: ValidadorIdentidade) -> None:
        self.repositorio, self.identidade = repositorio, identidade

    def _validated_record(self, data: DadosRegisto) -> RegistoCriminal:
        bi = normalize_bi(data.numero_bi)
        return RegistoCriminal(bi, normalize_process(data.numero_processo), required(data.tipo_infracao, "Tipo de infracao", 150), required(data.descricao, "Descricao", 500), required(data.tribunal, "Tribunal", 200), sentence_date(data.data_sentenca), required(data.pena, "Pena", 300), record_status(data.estado))

    def criar_registo(self, data: DadosRegisto) -> RegistoCriminal:
        record = self._validated_record(data)
        if self.repositorio.obter_registo_por_processo(record.numero_processo): raise JaExiste("Ja existe um registo com este numero de processo.")
        return self.repositorio.adicionar_registo(record)

    def obter_registo(self, record_id: int) -> RegistoCriminal:
        record = self.repositorio.obter_registo(record_id)
        if not record: raise NaoEncontrado("Registo registo_criminal nao encontrado.")
        return record

    def listar_registos(self, pagina: int = 1, tamanho_pagina: int = 10, numero_bi: str | None = None) -> Pagina[RegistoCriminal]:
        if pagina < 1 or not 1 <= tamanho_pagina <= 100: raise ErroValidacao("Paginacao invalida.")
        bi = normalize_bi(numero_bi) if numero_bi else None
        itens, total = self.repositorio.listar_registos(pagina, tamanho_pagina, bi)
        return Pagina(itens, pagina, tamanho_pagina, total)

    def actualizar_registo(self, record_id: int, data: DadosRegisto) -> RegistoCriminal:
        current, validated = self.obter_registo(record_id), self._validated_record(data)
        duplicate = self.repositorio.obter_registo_por_processo(validated.numero_processo)
        if duplicate and duplicate.id != record_id: raise JaExiste("Ja existe um registo com este numero de processo.")
        return self.repositorio.actualizar_registo(replace(validated, id=current.id, data_registo=current.data_registo, data_actualizacao=current.data_actualizacao))

    def validar_identidade(self, numero_bi: str) -> DadosIdentidade | None:
        return self.identidade.procurar(normalize_bi(numero_bi))
