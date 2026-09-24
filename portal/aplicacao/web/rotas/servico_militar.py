from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ...dominio import DadosRecenseamentoMilitar
from ...infraestrutura.grpc import (
    ErroOperacaoPortal, LigacaoServicoMilitar, ServicoIndisponivel,
    obter_ligacao_servico_militar,
)
from ..renderizacao import modelos


roteador = APIRouter(prefix="/servico_militar")
TAMANHO_PAGINA = 10
SITUACOES = (
    ("RECENSEADO", "Recenseado"), ("APTO", "Apto"),
    ("INCORPORADO", "Incorporado"), ("RESERVA", "Reserva"), ("ISENTO", "Isento"),
)


def _erro(request: Request, titulo: str, erro: Exception, codigo: int | None = None):
    return modelos.TemplateResponse(request=request, name="partilhado/erro.html",
        context={"title": titulo, "message": str(erro)},
        status_code=codigo or (503 if isinstance(erro, ServicoIndisponivel) else 400))


def _valores(**valores: str) -> dict[str, str]:
    return {chave: valor or "" for chave, valor in valores.items()}


def _dados(valores: dict[str, str]) -> DadosRecenseamentoMilitar:
    return DadosRecenseamentoMilitar(**valores)


def _formulario(request: Request, *, valores: dict[str, str], titulo: str,
                accao: str, rotulo: str, erro: str | None = None, codigo: int = 200):
    return modelos.TemplateResponse(request=request, name="servico_militar/formulario.html",
        context={"values": valores, "title": titulo, "action": accao,
                 "submit_label": rotulo, "error": erro, "situacoes": SITUACOES}, status_code=codigo)


@roteador.get("", response_class=HTMLResponse, name="painel_servico_militar")
def painel(request: Request, gateway: LigacaoServicoMilitar = Depends(obter_ligacao_servico_militar)):
    try:
        resultado = gateway.listar(1, 5)
    except ErroOperacaoPortal as erro:
        return _erro(request, "Serviço Militar indisponível", erro, 503)
    return modelos.TemplateResponse(request=request, name="servico_militar/painel.html", context={"resultado": resultado})


@roteador.get("/recenseamentos", response_class=HTMLResponse, name="lista_recenseamentos_militares")
def listar(request: Request, pagina: int = Query(1, ge=1), numero_bi: str = Query(""),
           gateway: LigacaoServicoMilitar = Depends(obter_ligacao_servico_militar)):
    try:
        resultado = gateway.listar(pagina, TAMANHO_PAGINA, numero_bi)
    except ErroOperacaoPortal as erro:
        return _erro(request, "Não foi possível listar os recenseamentos", erro, 503)
    return modelos.TemplateResponse(request=request, name="servico_militar/lista.html",
        context={"resultado": resultado, "numero_bi": numero_bi})


@roteador.get("/recenseamentos/novo", response_class=HTMLResponse, name="novo_recenseamento_militar")
def novo(request: Request):
    return _formulario(request, valores={"situacao": "RECENSEADO"}, titulo="Novo recenseamento militar",
        accao=str(request.url_for("criar_recenseamento_militar")), rotulo="Guardar recenseamento")


@roteador.post("/recenseamentos", response_class=HTMLResponse, name="criar_recenseamento_militar")
def criar(request: Request, numero_bi: str = Form(""), numero_recenseamento: str = Form(""),
          data_recenseamento: str = Form(""), distrito: str = Form(""),
          posto_recenseamento: str = Form(""), ramo: str = Form(""),
          situacao: str = Form(""), observacoes: str = Form(""),
          gateway: LigacaoServicoMilitar = Depends(obter_ligacao_servico_militar)):
    valores = _valores(numero_bi=numero_bi, numero_recenseamento=numero_recenseamento,
        data_recenseamento=data_recenseamento, distrito=distrito,
        posto_recenseamento=posto_recenseamento, ramo=ramo,
        situacao=situacao, observacoes=observacoes)
    try:
        item = gateway.criar(_dados(valores))
    except ErroOperacaoPortal as erro:
        return _formulario(request, valores=valores, titulo="Novo recenseamento militar",
            accao=str(request.url_for("criar_recenseamento_militar")), rotulo="Guardar recenseamento",
            erro=str(erro), codigo=503 if isinstance(erro, ServicoIndisponivel) else 400)
    return RedirectResponse(request.url_for("detalhe_recenseamento_militar", item_id=item.id).include_query_params(saved="1"), 303)


@roteador.get("/recenseamentos/{item_id}", response_class=HTMLResponse, name="detalhe_recenseamento_militar")
def detalhe(request: Request, item_id: int, saved: bool = False, updated: bool = False,
            gateway: LigacaoServicoMilitar = Depends(obter_ligacao_servico_militar)):
    try:
        item = gateway.obter(item_id)
    except ErroOperacaoPortal as erro:
        return _erro(request, "Recenseamento militar não encontrado", erro, 404)
    return modelos.TemplateResponse(request=request, name="servico_militar/detalhe.html",
        context={"item": item, "saved": saved, "updated": updated})


@roteador.get("/recenseamentos/{item_id}/editar", response_class=HTMLResponse, name="editar_recenseamento_militar")
def editar(request: Request, item_id: int,
           gateway: LigacaoServicoMilitar = Depends(obter_ligacao_servico_militar)):
    try:
        item = gateway.obter(item_id)
    except ErroOperacaoPortal as erro:
        return _erro(request, "Recenseamento militar não encontrado", erro, 404)
    valores = _valores(numero_bi=item.numero_bi, numero_recenseamento=item.numero_recenseamento,
        data_recenseamento=item.data_recenseamento.isoformat(), distrito=item.distrito,
        posto_recenseamento=item.posto_recenseamento, ramo=item.ramo,
        situacao=item.situacao, observacoes=item.observacoes or "")
    return _formulario(request, valores=valores, titulo="Actualizar recenseamento militar",
        accao=str(request.url_for("actualizar_recenseamento_militar", item_id=item_id)), rotulo="Guardar alterações")


@roteador.post("/recenseamentos/{item_id}", response_class=HTMLResponse, name="actualizar_recenseamento_militar")
def actualizar(request: Request, item_id: int, numero_bi: str = Form(""),
               numero_recenseamento: str = Form(""), data_recenseamento: str = Form(""),
               distrito: str = Form(""), posto_recenseamento: str = Form(""),
               ramo: str = Form(""), situacao: str = Form(""), observacoes: str = Form(""),
               gateway: LigacaoServicoMilitar = Depends(obter_ligacao_servico_militar)):
    valores = _valores(numero_bi=numero_bi, numero_recenseamento=numero_recenseamento,
        data_recenseamento=data_recenseamento, distrito=distrito,
        posto_recenseamento=posto_recenseamento, ramo=ramo, situacao=situacao, observacoes=observacoes)
    try:
        gateway.actualizar(item_id, _dados(valores))
    except ErroOperacaoPortal as erro:
        return _formulario(request, valores=valores, titulo="Actualizar recenseamento militar",
            accao=str(request.url_for("actualizar_recenseamento_militar", item_id=item_id)), rotulo="Guardar alterações",
            erro=str(erro), codigo=503 if isinstance(erro, ServicoIndisponivel) else 400)
    return RedirectResponse(request.url_for("detalhe_recenseamento_militar", item_id=item_id).include_query_params(updated="1"), 303)


@roteador.get("/consultar-situacao", response_class=HTMLResponse, name="consultar_situacao_militar")
def consultar_situacao(request: Request, numero_bi: str = Query(""),
                       gateway: LigacaoServicoMilitar = Depends(obter_ligacao_servico_militar)):
    resultado = None
    erro = None
    if numero_bi.strip():
        try:
            resultado = gateway.consultar_situacao(numero_bi)
        except ErroOperacaoPortal as esperado:
            erro = esperado
    return modelos.TemplateResponse(request=request, name="servico_militar/situacao.html",
        context={"numero_bi": numero_bi, "resultado": resultado, "error": erro},
        status_code=503 if isinstance(erro, ServicoIndisponivel) else 200)


@roteador.get("/validar-identidade", response_class=HTMLResponse, name="validar_identidade_servico_militar")
def validar_identidade(request: Request, numero_bi: str = Query(""),
                       gateway: LigacaoServicoMilitar = Depends(obter_ligacao_servico_militar)):
    resultado = None
    erro = None
    if numero_bi.strip():
        try:
            resultado = gateway.validar_identidade(numero_bi)
        except ErroOperacaoPortal as esperado:
            erro = esperado
    return modelos.TemplateResponse(request=request, name="servico_militar/validacao_identidade.html",
        context={"numero_bi": numero_bi, "resultado": resultado, "error": erro},
        status_code=503 if isinstance(erro, ServicoIndisponivel) else 200)


@roteador.get("/consultar-antecedentes", response_class=HTMLResponse, name="consultar_antecedentes_servico_militar")
def consultar_antecedentes(request: Request, numero_bi: str = Query(""), pagina: int = Query(1, ge=1),
                           gateway: LigacaoServicoMilitar = Depends(obter_ligacao_servico_militar)):
    resultado = None
    erro = None
    if numero_bi.strip():
        try:
            resultado = gateway.consultar_antecedentes(numero_bi, pagina, TAMANHO_PAGINA)
        except ErroOperacaoPortal as esperado:
            erro = esperado
    return modelos.TemplateResponse(request=request, name="servico_militar/antecedentes.html",
        context={"numero_bi": numero_bi, "resultado": resultado, "error": erro},
        status_code=503 if isinstance(erro, ServicoIndisponivel) else 200)
