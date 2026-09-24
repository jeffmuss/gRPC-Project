from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ...dominio import DadosRegistoCriminal
from ...infraestrutura.grpc import LigacaoRegistoCriminal, ErroOperacaoPortal, ServicoIndisponivel, obter_ligacao_registo_criminal
from ..renderizacao import modelos

roteador = APIRouter(prefix="/registo_criminal")
TAMANHO_PAGINA = 10
ESTADOS = (("ACTIVO", "Activo"), ("CUMPRIDO", "Cumprido"), ("ARQUIVADO", "Arquivado"))


def _error(request: Request, title: str, error: Exception, code: int | None = None):
    return modelos.TemplateResponse(
        request=request, name="partilhado/erro.html",
        context={"title": title, "message": str(error)},
        status_code=code or (503 if isinstance(error, ServicoIndisponivel) else 400),
    )


def _record_values(**values: str) -> dict[str, str]:
    return {key: value or "" for key, value in values.items()}


def _record_input(values: dict[str, str]) -> DadosRegistoCriminal:
    return DadosRegistoCriminal(**values)


def _record_form(request: Request, *, values: dict[str, str], title: str, action: str,
                 submit_label: str, error: str | None = None, status_code: int = 200):
    return modelos.TemplateResponse(
        request=request, name="registo_criminal/formulario_registo.html",
        context={"values": values, "title": title, "action": action,
                 "submit_label": submit_label, "error": error, "estados": ESTADOS},
        status_code=status_code,
    )


@roteador.get("", response_class=HTMLResponse, name="painel_registo_criminal")
def painel_registo_criminal(request: Request, gateway: LigacaoRegistoCriminal = Depends(obter_ligacao_registo_criminal)):
    try:
        registos = gateway.listar_registos(pagina=1, tamanho_pagina=5)
    except ErroOperacaoPortal as error:
        return _error(request, "Registo Criminal indisponivel", error, 503)
    return modelos.TemplateResponse(request=request, name="registo_criminal/painel.html",
                                      context={"registos": registos})


@roteador.get("/validar-identidade", response_class=HTMLResponse, name="validacao_identidade_registo_criminal")
def validar_identidade(
    request: Request,
    numero_bi: str = Query(""),
    gateway: LigacaoRegistoCriminal = Depends(obter_ligacao_registo_criminal),
):
    resultado = None
    error: ErroOperacaoPortal | None = None
    if numero_bi.strip():
        try:
            resultado = gateway.validar_identidade(numero_bi)
        except ErroOperacaoPortal as expected:
            error = expected
    return modelos.TemplateResponse(
        request=request,
        name="registo_criminal/validacao_identidade.html",
        context={"numero_bi": numero_bi, "resultado": resultado, "error": error},
        status_code=503 if isinstance(error, ServicoIndisponivel) else 200,
    )


@roteador.get("/registos", response_class=HTMLResponse, name="lista_registos_criminais")
def listar_registos(request: Request, pagina: int = Query(1, ge=1), numero_bi: str = Query(""),
                gateway: LigacaoRegistoCriminal = Depends(obter_ligacao_registo_criminal)):
    try:
        resultado = gateway.listar_registos(pagina, TAMANHO_PAGINA, numero_bi)
    except ErroOperacaoPortal as error:
        return _error(request, "Nao foi possivel listar os registos", error, 503)
    return modelos.TemplateResponse(request=request, name="registo_criminal/lista_registos.html",
                                      context={"resultado": resultado, "numero_bi": numero_bi})


@roteador.get("/registos/novo", response_class=HTMLResponse, name="novo_registo_criminal")
def novo_registo(request: Request):
    return _record_form(request, values={"estado": "ACTIVO"}, title="Criar registo criminal",
                        action=str(request.url_for("criar_registo_criminal")), submit_label="Guardar registo")


@roteador.post("/registos", response_class=HTMLResponse, name="criar_registo_criminal")
def criar_registo(request: Request, numero_bi: str = Form(""), numero_processo: str = Form(""),
                  tipo_infracao: str = Form(""), descricao: str = Form(""), tribunal: str = Form(""),
                  data_sentenca: str = Form(""), pena: str = Form(""), estado: str = Form(""),
                  gateway: LigacaoRegistoCriminal = Depends(obter_ligacao_registo_criminal)):
    values = _record_values(numero_bi=numero_bi, numero_processo=numero_processo,
                            tipo_infracao=tipo_infracao, descricao=descricao, tribunal=tribunal,
                            data_sentenca=data_sentenca, pena=pena, estado=estado)
    try:
        item = gateway.criar_registo(_record_input(values))
    except ErroOperacaoPortal as error:
        return _record_form(request, values=values, title="Criar registo criminal",
                            action=str(request.url_for("criar_registo_criminal")), submit_label="Guardar registo",
                            error=str(error), status_code=503 if isinstance(error, ServicoIndisponivel) else 400)
    return RedirectResponse(request.url_for("detalhe_registo_criminal", registo_id=item.id).include_query_params(saved="1"), 303)


@roteador.get("/registos/{registo_id}", response_class=HTMLResponse, name="detalhe_registo_criminal")
def detalhe_registo(request: Request, registo_id: int, saved: bool = False, updated: bool = False,
                  gateway: LigacaoRegistoCriminal = Depends(obter_ligacao_registo_criminal)):
    try:
        item = gateway.obter_registo(registo_id)
    except ErroOperacaoPortal as error:
        return _error(request, "Registo criminal nao encontrado", error, 404)
    return modelos.TemplateResponse(request=request, name="registo_criminal/detalhe_registo.html",
                                      context={"item": item, "saved": saved, "updated": updated})


@roteador.get("/registos/{registo_id}/editar", response_class=HTMLResponse, name="editar_registo_criminal")
def editar_registo(request: Request, registo_id: int, gateway: LigacaoRegistoCriminal = Depends(obter_ligacao_registo_criminal)):
    try:
        item = gateway.obter_registo(registo_id)
    except ErroOperacaoPortal as error:
        return _error(request, "Registo criminal nao encontrado", error, 404)
    values = _record_values(numero_bi=item.numero_bi, numero_processo=item.numero_processo,
                            tipo_infracao=item.tipo_infracao, descricao=item.descricao, tribunal=item.tribunal,
                            data_sentenca=item.data_sentenca.isoformat(), pena=item.pena, estado=item.estado)
    return _record_form(request, values=values, title="Actualizar registo criminal",
                        action=str(request.url_for("actualizar_registo_criminal", registo_id=registo_id)),
                        submit_label="Guardar alteracoes")


@roteador.post("/registos/{registo_id}", response_class=HTMLResponse, name="actualizar_registo_criminal")
def actualizar_registo(request: Request, registo_id: int, numero_bi: str = Form(""), numero_processo: str = Form(""),
                  tipo_infracao: str = Form(""), descricao: str = Form(""), tribunal: str = Form(""),
                  data_sentenca: str = Form(""), pena: str = Form(""), estado: str = Form(""),
                  gateway: LigacaoRegistoCriminal = Depends(obter_ligacao_registo_criminal)):
    values = _record_values(numero_bi=numero_bi, numero_processo=numero_processo,
                            tipo_infracao=tipo_infracao, descricao=descricao, tribunal=tribunal,
                            data_sentenca=data_sentenca, pena=pena, estado=estado)
    try:
        gateway.actualizar_registo(registo_id, _record_input(values))
    except ErroOperacaoPortal as error:
        return _record_form(request, values=values, title="Actualizar registo criminal",
                            action=str(request.url_for("actualizar_registo_criminal", registo_id=registo_id)),
                            submit_label="Guardar alteracoes", error=str(error),
                            status_code=503 if isinstance(error, ServicoIndisponivel) else 400)
    return RedirectResponse(request.url_for("detalhe_registo_criminal", registo_id=registo_id).include_query_params(updated="1"), 303)
