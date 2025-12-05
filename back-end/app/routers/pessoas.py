from fastapi import APIRouter, HTTPException, Query, Response
from typing import List, Optional

from app.models.schemas import PessoaCreate, Pessoa, PessoasPage, PageMeta
from app.services import pessoas_service


router = APIRouter(prefix="/cadastro/pessoas", tags=["pessoas"])


@router.post("", response_model=Pessoa)
def criar_pessoa(payload: PessoaCreate):
    return pessoas_service.criar_pessoa(payload)


@router.get("", response_model=PessoasPage)
def listar_pessoas(
    tipo_doc: Optional[str] = Query(None),
    documento: Optional[str] = Query(None),
    nome: Optional[str] = Query(None),
    sobre_nome: Optional[str] = Query(None),
    sexo: Optional[str] = Query(None),
    ativo: Optional[bool] = Query(None),
    nascimento: Optional[str] = Query(None),
    page: str = Query("1"),
    page_size: int = Query(20, ge=1, le=200),
    sort_by: str = Query("nome"),
    order: str = Query("asc"),
    response: Response = None,
):
    total, page_number, items = pessoas_service.listar_pessoas(
        tipo_doc, documento, nome, sobre_nome, sexo, ativo, nascimento, page, page_size, sort_by, order
    )
    from fastapi import Response as _Response
    if isinstance(response, _Response):
        response.headers["X-Total-Count"] = str(total)
        response.headers["X-Page"] = str(page_number)
        response.headers["X-Page-Size"] = str(page_size)
    return PessoasPage(items=items, meta=PageMeta(total=total, page=page_number, page_size=page_size))


@router.get("/{matricula}", response_model=Pessoa)
def obter_pessoa(matricula: int):
    return pessoas_service.obter_pessoa(matricula)


@router.put("/{matricula}", response_model=Pessoa)
def atualizar_pessoa(matricula: int, payload: PessoaCreate):
    return pessoas_service.atualizar_pessoa(matricula, payload)


@router.delete("/{matricula}")
def remover_pessoa(matricula: int):
    pessoas_service.remover_pessoa(matricula)
    return {"ok": True}
