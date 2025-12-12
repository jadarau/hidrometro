from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.infrastructure.db import get_db
from app.models.schemas import TarifaAnoCreate, TarifaAno, TarifaFaixa, TipoImovel, CategoriaLigacao
from app.services.tarifas_service import (
    create_tarifa,
    list_tarifas,
    get_tarifa,
    update_tarifa,
    delete_tarifa,
)
from app.services.faturas_service import carregar_tarifas_xlsx

router = APIRouter(prefix="/tarifas", tags=["tarifas"])

@router.post("/", response_model=TarifaAno)
def criar_tarifa(tarifa: TarifaAnoCreate, db: Session = Depends(get_db)):
    t = create_tarifa(db, tarifa)
    return TarifaAno(id=t.id, ano=t.ano, tipo_imovel=t.tipo, categoria_ligacao=t.categoria_ligacao, faixas=[
        TarifaFaixa(
            faixa=f.faixa,
            consumo_min=f.consumo_min,
            consumo_max=f.consumo_max,
            valor_minimo=(f.valor_minimo / 100.0) if f.valor_minimo is not None else None,
            valor_por_m3=(f.valor_por_m3 / 100.0) if f.valor_por_m3 is not None else None,
        ) for f in t.faixas
    ])

@router.get("/", response_model=List[TarifaAno])
def consultar_tarifas(
    ano: Optional[int] = Query(default=None),
    tipo_imovel: Optional[TipoImovel] = Query(default=None),
    categoria_ligacao: Optional[CategoriaLigacao] = Query(default=None),
    db: Session = Depends(get_db),
):
    rows = list_tarifas(db, ano=ano, tipo_imovel=tipo_imovel, categoria_ligacao=categoria_ligacao)
    result: List[TarifaAno] = []
    for t in rows:
        result.append(TarifaAno(
            id=t.id, ano=t.ano, tipo_imovel=t.tipo, categoria_ligacao=t.categoria_ligacao,
            faixas=[TarifaFaixa(
                faixa=f.faixa,
                consumo_min=f.consumo_min,
                consumo_max=f.consumo_max,
                valor_minimo=(f.valor_minimo / 100.0) if f.valor_minimo is not None else None,
                valor_por_m3=(f.valor_por_m3 / 100.0) if f.valor_por_m3 is not None else None,
            ) for f in t.faixas]
        ))
    return result

@router.get("/{tarifa_id}", response_model=TarifaAno)
def obter_tarifa(tarifa_id: int, db: Session = Depends(get_db)):
    t = get_tarifa(db, tarifa_id)
    if not t:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Tarifa não encontrada")
    return TarifaAno(id=t.id, ano=t.ano, tipo_imovel=t.tipo, categoria_ligacao=t.categoria_ligacao, faixas=[
        TarifaFaixa(
            faixa=f.faixa,
            consumo_min=f.consumo_min,
            consumo_max=f.consumo_max,
            valor_minimo=(f.valor_minimo / 100.0) if f.valor_minimo is not None else None,
            valor_por_m3=(f.valor_por_m3 / 100.0) if f.valor_por_m3 is not None else None,
        ) for f in t.faixas
    ])

@router.put("/{tarifa_id}", response_model=TarifaAno)
def atualizar_tarifa(tarifa_id: int, tarifa: TarifaAnoCreate, db: Session = Depends(get_db)):
    t = update_tarifa(db, tarifa_id, tarifa)
    if not t:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Tarifa não encontrada")
    return TarifaAno(id=t.id, ano=t.ano, tipo_imovel=t.tipo, categoria_ligacao=t.categoria_ligacao, faixas=[
        TarifaFaixa(
            faixa=f.faixa,
            consumo_min=f.consumo_min,
            consumo_max=f.consumo_max,
            valor_minimo=(f.valor_minimo / 100.0) if f.valor_minimo is not None else None,
            valor_por_m3=(f.valor_por_m3 / 100.0) if f.valor_por_m3 is not None else None,
        ) for f in t.faixas
    ])

@router.delete("/{tarifa_id}")
def remover_tarifa(tarifa_id: int, db: Session = Depends(get_db)):
    ok = delete_tarifa(db, tarifa_id)
    if not ok:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Tarifa não encontrada")
    return {"deleted": True}

@router.post("/upload")
def upload_tarifas_xlsx(
    ano: int = Form(...),
    tipo_imovel: TipoImovel = Form(...),
    categoria_ligacao: CategoriaLigacao = Form(...),
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    import tempfile, os
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp.write(arquivo.file.read())
        caminho = tmp.name
    try:
        tid = carregar_tarifas_xlsx(db, caminho, ano, tipo_imovel, categoria_ligacao)
    finally:
        os.remove(caminho)
    return {"tarifa_ano_id": tid, "ano": ano, "tipo_imovel": tipo_imovel, "categoria_ligacao": categoria_ligacao}
