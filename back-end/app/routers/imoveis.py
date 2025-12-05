from fastapi import APIRouter, HTTPException, Query, Response
from typing import List, Optional

from app.models.schemas import (
    ImovelCreate,
    Imovel,
    ImoveisPage,
    PageMeta,
)
from app.services import imoveis_service

router = APIRouter(prefix="/cadastro/imoveis", tags=["imoveis"])


@router.post("", response_model=Imovel)
def criar_imovel(payload: ImovelCreate):
    return imoveis_service.criar_imovel(payload)


@router.get("", response_model=ImoveisPage)
def listar_imoveis(
    cidade: Optional[str] = Query(None),
    categoria: Optional[str] = Query(None),
    ativo: Optional[bool] = Query(None),
    cep: Optional[str] = Query(None),
    page: str = Query("1"),
    page_size: int = Query(20, ge=1, le=200),
    sort_by: str = Query("cidade"),
    order: str = Query("asc"),
    response: Response = None,
):
    total, page_number, items = imoveis_service.listar_imoveis(
        cidade, categoria, ativo, cep, page, page_size, sort_by, order
    )
    from fastapi import Response as _Response
    if isinstance(response, _Response):
        response.headers["X-Total-Count"] = str(total)
        response.headers["X-Page"] = str(page_number)
        response.headers["X-Page-Size"] = str(page_size)
    return ImoveisPage(items=items, meta=PageMeta(total=total, page=page_number, page_size=page_size))


@router.get("/{matricula}", response_model=Imovel)
def obter_imovel(matricula: int):
    return imoveis_service.obter_imovel(matricula)


@router.put("/{matricula}", response_model=Imovel)
def atualizar_imovel(matricula: int, payload: ImovelCreate):
    return imoveis_service.atualizar_imovel(matricula, payload)


@router.delete("/{matricula}")
def remover_imovel(matricula: int):
    imoveis_service.remover_imovel(matricula)
    return {"ok": True}
