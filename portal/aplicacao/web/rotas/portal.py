from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ...dominio import DadosCidadao, EstadoServico
from ...infraestrutura.grpc import (
    LigacaoRegistoCriminal,
    LigacaoIdentificacaoCivil,
    ErroOperacaoPortal,
    ServicoIndisponivel,
    obter_ligacao_identificacao_civil,
    obter_ligacao_registo_criminal,
    LigacaoServicoMilitar,
    obter_ligacao_servico_militar,
)
from ..renderizacao import modelos


roteador = APIRouter()
TAMANHO_PAGINA = 10
VALORES_SEXO = (("F", "Feminino"), ("M", "Masculino"), ("OUTRO", "Outro"))


def _identificacao_civil_indisponivel(mensagem: str) -> EstadoServico:
    return EstadoServico(
        chave="identificacao_civil",
        nome="Identificacao Civil",
        estado="indisponivel",
        disponivel=False,
        mensagem=mensagem,
    )


def _form_values(**values: str) -> dict[str, str]:
    return {name: value or "" for name, value in values.items()}


def _input(values: dict[str, str]) -> DadosCidadao:
    return DadosCidadao(
        numero_bi=values["numero_bi"],
        nome_completo=values["nome_completo"],
        data_nascimento=values["data_nascimento"],
        sexo=values["sexo"],
        nacionalidade=values["nacionalidade"],
        nome_pai=values["nome_pai"],
        nome_mae=values["nome_mae"],
        residencia=values["residencia"],
    )


def _render_form(
    request: Request,
    *,
    values: dict[str, str],
    title: str,
    action: str,
    submit_label: str,
    error: str | None = None,
    status_code: int = 200,
) -> HTMLResponse:
    return modelos.TemplateResponse(
        request=request,
        name="identificacao_civil/formulario.html",
        context={
            "values": values,
            "title": title,
            "action": action,
            "submit_label": submit_label,
            "error": error,
            "sex_values": VALORES_SEXO,
        },
        status_code=status_code,
    )


@roteador.get("/saude", name="saude_portal")
def saude_portal() -> dict[str, str]:
    return {"servico": "portal", "estado": "operacional"}


@roteador.get("/", response_class=HTMLResponse, name="painel_portal")
def painel_portal(
    request: Request,
    gateway: LigacaoIdentificacaoCivil = Depends(obter_ligacao_identificacao_civil),
    registo_criminal_gateway: LigacaoRegistoCriminal = Depends(obter_ligacao_registo_criminal),
    servico_militar_gateway: LigacaoServicoMilitar = Depends(obter_ligacao_servico_militar),
) -> HTMLResponse:
    try:
        identificacao_civil = gateway.saude()
    except ErroOperacaoPortal as error:
        identificacao_civil = _identificacao_civil_indisponivel(str(error))
    try:
        registo_criminal = registo_criminal_gateway.saude()
    except ErroOperacaoPortal as error:
        registo_criminal = EstadoServico("registo_criminal", "Registo Criminal", "indisponivel", False, str(error))
    try:
        servico_militar = servico_militar_gateway.saude()
    except ErroOperacaoPortal as error:
        servico_militar = EstadoServico("servico_militar", "Serviço Militar", "indisponivel", False, str(error))
    servicos = [identificacao_civil, registo_criminal, servico_militar]
    return modelos.TemplateResponse(
        request=request, name="portal/painel.html", context={"servicos": servicos}
    )


@roteador.get("/identificacao", response_class=HTMLResponse, name="painel_identificacao_civil")
def painel_identificacao_civil(
    request: Request,
    gateway: LigacaoIdentificacaoCivil = Depends(obter_ligacao_identificacao_civil),
) -> HTMLResponse:
    try:
        resultado = gateway.listar(pagina=1, tamanho_pagina=5)
    except ServicoIndisponivel as error:
        return modelos.TemplateResponse(
            request=request,
            name="partilhado/erro.html",
            context={"title": "Identificacao Civil indisponivel", "message": str(error)},
            status_code=503,
        )
    return modelos.TemplateResponse(
        request=request,
        name="identificacao_civil/painel.html",
        context={"resultado": resultado},
    )


@roteador.get(
    "/identificacao/cidadaos",
    response_class=HTMLResponse,
    name="lista_cidadaos",
)
def lista_cidadaos(
    request: Request,
    pagina: int = Query(1, ge=1),
    gateway: LigacaoIdentificacaoCivil = Depends(obter_ligacao_identificacao_civil),
) -> HTMLResponse:
    try:
        resultado = gateway.listar(pagina=pagina, tamanho_pagina=TAMANHO_PAGINA)
    except ErroOperacaoPortal as error:
        return modelos.TemplateResponse(
            request=request,
            name="partilhado/erro.html",
            context={"title": "Nao foi possivel listar cidadaos", "message": str(error)},
            status_code=503,
        )
    return modelos.TemplateResponse(
        request=request, name="identificacao_civil/lista.html", context={"resultado": resultado}
    )


@roteador.get(
    "/identificacao/cidadaos/pesquisar",
    response_class=HTMLResponse,
    name="pesquisa_cidadaos",
)
def pesquisa_cidadaos(
    request: Request,
    numero_bi: str = Query(""),
    gateway: LigacaoIdentificacaoCivil = Depends(obter_ligacao_identificacao_civil),
) -> HTMLResponse:
    cidadao = None
    error = None
    if numero_bi.strip():
        try:
            cidadao = gateway.procurar_por_bi(numero_bi)
        except ErroOperacaoPortal as expected:
            error = str(expected)
    return modelos.TemplateResponse(
        request=request,
        name="identificacao_civil/pesquisa.html",
        context={"cidadao": cidadao, "error": error, "numero_bi": numero_bi},
    )


@roteador.get(
    "/identificacao/cidadaos/novo",
    response_class=HTMLResponse,
    name="novo_cidadao",
)
def novo_cidadao(request: Request) -> HTMLResponse:
    return _render_form(
        request,
        values={},
        title="Registar cidadao",
        action=str(request.url_for("registar_cidadao")),
        submit_label="Registar cidadao",
    )


@roteador.post(
    "/identificacao/cidadaos",
    response_class=HTMLResponse,
    name="registar_cidadao",
)
def registar_cidadao(
    request: Request,
    numero_bi: str = Form(""),
    nome_completo: str = Form(""),
    data_nascimento: str = Form(""),
    sexo: str = Form(""),
    nacionalidade: str = Form(""),
    nome_pai: str = Form(""),
    nome_mae: str = Form(""),
    residencia: str = Form(""),
    gateway: LigacaoIdentificacaoCivil = Depends(obter_ligacao_identificacao_civil),
) -> HTMLResponse:
    values = _form_values(
        numero_bi=numero_bi,
        nome_completo=nome_completo,
        data_nascimento=data_nascimento,
        sexo=sexo,
        nacionalidade=nacionalidade,
        nome_pai=nome_pai,
        nome_mae=nome_mae,
        residencia=residencia,
    )
    try:
        cidadao = gateway.registar(_input(values))
    except ErroOperacaoPortal as expected:
        status_code = 503 if isinstance(expected, ServicoIndisponivel) else 400
        return _render_form(
            request,
            values=values,
            title="Registar cidadao",
            action=str(request.url_for("registar_cidadao")),
            submit_label="Registar cidadao",
            error=str(expected),
            status_code=status_code,
        )
    return RedirectResponse(
        request.url_for("detalhe_cidadao", cidadao_id=cidadao.id).include_query_params(saved="1"),
        status_code=303,
    )


@roteador.get(
    "/identificacao/cidadaos/{cidadao_id}",
    response_class=HTMLResponse,
    name="detalhe_cidadao",
)
def detalhe_cidadao(
    request: Request,
    cidadao_id: int,
    saved: bool = False,
    updated: bool = False,
    gateway: LigacaoIdentificacaoCivil = Depends(obter_ligacao_identificacao_civil),
) -> HTMLResponse:
    try:
        cidadao = gateway.obter(cidadao_id)
    except ErroOperacaoPortal as error:
        return modelos.TemplateResponse(
            request=request,
            name="partilhado/erro.html",
            context={"title": "Cidadao nao encontrado", "message": str(error)},
            status_code=503 if isinstance(error, ServicoIndisponivel) else 404,
        )
    return modelos.TemplateResponse(
        request=request,
        name="identificacao_civil/detalhe.html",
        context={"cidadao": cidadao, "saved": saved, "updated": updated},
    )


@roteador.get(
    "/identificacao/cidadaos/{cidadao_id}/antecedentes",
    response_class=HTMLResponse,
    name="historico_criminal_cidadao",
)
def historico_criminal_cidadao(
    request: Request,
    cidadao_id: int,
    pagina: int = Query(1, ge=1),
    gateway: LigacaoIdentificacaoCivil = Depends(obter_ligacao_identificacao_civil),
) -> HTMLResponse:
    try:
        cidadao = gateway.obter(cidadao_id)
        resultado = gateway.historico_criminal(cidadao.numero_bi, pagina=pagina, tamanho_pagina=TAMANHO_PAGINA)
    except ErroOperacaoPortal as error:
        return modelos.TemplateResponse(
            request=request,
            name="partilhado/erro.html",
            context={"title": "Nao foi possivel consultar os antecedentes", "message": str(error)},
            status_code=503 if isinstance(error, ServicoIndisponivel) else 404,
        )
    return modelos.TemplateResponse(
        request=request,
        name="identificacao_civil/historico_criminal.html",
        context={"cidadao": cidadao, "resultado": resultado},
    )


@roteador.get(
    "/identificacao/cidadaos/{cidadao_id}/editar",
    response_class=HTMLResponse,
    name="editar_cidadao",
)
def editar_cidadao(
    request: Request,
    cidadao_id: int,
    gateway: LigacaoIdentificacaoCivil = Depends(obter_ligacao_identificacao_civil),
) -> HTMLResponse:
    try:
        cidadao = gateway.obter(cidadao_id)
    except ErroOperacaoPortal as error:
        return modelos.TemplateResponse(
            request=request,
            name="partilhado/erro.html",
            context={"title": "Nao foi possivel abrir o registo", "message": str(error)},
            status_code=503 if isinstance(error, ServicoIndisponivel) else 404,
        )
    values = {
        "numero_bi": cidadao.numero_bi,
        "nome_completo": cidadao.nome_completo,
        "data_nascimento": cidadao.data_nascimento.isoformat(),
        "sexo": cidadao.sexo,
        "nacionalidade": cidadao.nacionalidade,
        "nome_pai": cidadao.nome_pai or "",
        "nome_mae": cidadao.nome_mae or "",
        "residencia": cidadao.residencia or "",
    }
    return _render_form(
        request,
        values=values,
        title="Actualizar cidadao",
        action=str(request.url_for("actualizar_cidadao", cidadao_id=cidadao_id)),
        submit_label="Guardar alteracoes",
    )


@roteador.post(
    "/identificacao/cidadaos/{cidadao_id}",
    response_class=HTMLResponse,
    name="actualizar_cidadao",
)
def actualizar_cidadao(
    request: Request,
    cidadao_id: int,
    numero_bi: str = Form(""),
    nome_completo: str = Form(""),
    data_nascimento: str = Form(""),
    sexo: str = Form(""),
    nacionalidade: str = Form(""),
    nome_pai: str = Form(""),
    nome_mae: str = Form(""),
    residencia: str = Form(""),
    gateway: LigacaoIdentificacaoCivil = Depends(obter_ligacao_identificacao_civil),
) -> HTMLResponse:
    values = _form_values(
        numero_bi=numero_bi,
        nome_completo=nome_completo,
        data_nascimento=data_nascimento,
        sexo=sexo,
        nacionalidade=nacionalidade,
        nome_pai=nome_pai,
        nome_mae=nome_mae,
        residencia=residencia,
    )
    try:
        gateway.actualizar(cidadao_id, _input(values))
    except ErroOperacaoPortal as expected:
        return _render_form(
            request,
            values=values,
            title="Actualizar cidadao",
            action=str(request.url_for("actualizar_cidadao", cidadao_id=cidadao_id)),
            submit_label="Guardar alteracoes",
            error=str(expected),
            status_code=503 if isinstance(expected, ServicoIndisponivel) else 400,
        )
    return RedirectResponse(
        request.url_for("detalhe_cidadao", cidadao_id=cidadao_id).include_query_params(updated="1"),
        status_code=303,
    )
