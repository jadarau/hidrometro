from sqlalchemy.orm import Session
from typing import Optional, List
from app.infrastructure.orm_models import TarifaAnoDB, TarifaFaixaDB
from app.models.schemas import TarifaAnoCreate, TarifaFaixa, TipoImovel, CategoriaLigacao


def create_tarifa(db: Session, payload: TarifaAnoCreate) -> TarifaAnoDB:
    tarifa = TarifaAnoDB(ano=payload.ano, tipo=payload.tipo_imovel, categoria_ligacao=payload.categoria_ligacao)
    db.add(tarifa)
    db.flush()
    for f in payload.faixas:
        db.add(
            TarifaFaixaDB(
                tarifa_ano_id=tarifa.id,
                faixa=f.faixa,
                consumo_min=f.consumo_min,
                consumo_max=f.consumo_max,
                valor_minimo=int(round((f.valor_minimo or 0) * 100)) if f.valor_minimo is not None else None,
                valor_por_m3=int(round((f.valor_por_m3 or 0) * 100)) if f.valor_por_m3 is not None else None,
            )
        )
    db.commit()
    db.refresh(tarifa)
    return tarifa


def list_tarifas(
    db: Session,
    ano: Optional[int] = None,
    tipo_imovel: Optional[TipoImovel] = None,
    categoria_ligacao: Optional[CategoriaLigacao] = None,
) -> List[TarifaAnoDB]:
    q = db.query(TarifaAnoDB)
    if ano is not None:
        q = q.filter(TarifaAnoDB.ano == ano)
    if tipo_imovel is not None:
        q = q.filter(TarifaAnoDB.tipo == tipo_imovel)
    if categoria_ligacao is not None:
        q = q.filter(TarifaAnoDB.categoria_ligacao == categoria_ligacao)
    return q.order_by(TarifaAnoDB.ano.desc(), TarifaAnoDB.tipo.asc(), TarifaAnoDB.categoria_ligacao.asc()).all()


def get_tarifa(db: Session, tarifa_id: int) -> Optional[TarifaAnoDB]:
    return db.query(TarifaAnoDB).filter(TarifaAnoDB.id == tarifa_id).first()


def update_tarifa(db: Session, tarifa_id: int, payload: TarifaAnoCreate) -> Optional[TarifaAnoDB]:
    tarifa = get_tarifa(db, tarifa_id)
    if not tarifa:
        return None
    tarifa.ano = payload.ano
    tarifa.tipo = payload.tipo_imovel
    tarifa.categoria_ligacao = payload.categoria_ligacao
    # replace faixas
    db.query(TarifaFaixaDB).filter(TarifaFaixaDB.tarifa_ano_id == tarifa.id).delete()
    for f in payload.faixas:
        db.add(
            TarifaFaixaDB(
                tarifa_ano_id=tarifa.id,
                faixa=f.faixa,
                consumo_min=f.consumo_min,
                consumo_max=f.consumo_max,
                valor_minimo=int(round((f.valor_minimo or 0) * 100)),
                valor_por_m3=int(round((f.valor_por_m3 or 0) * 100)),
            )
        )
    db.commit()
    db.refresh(tarifa)
    return tarifa


def delete_tarifa(db: Session, tarifa_id: int) -> bool:
    tarifa = get_tarifa(db, tarifa_id)
    if not tarifa:
        return False
    db.delete(tarifa)
    db.commit()
    return True

def create_tarifas_bulk(db: Session, tarifas: List[TarifaAnoCreate]) -> List[TarifaAnoDB]:
    created: List[TarifaAnoDB] = []
    for t in tarifas:
        # upsert by unique (ano, tipo, categoria_ligacao)
        existing = (
            db.query(TarifaAnoDB)
            .filter(
                TarifaAnoDB.ano == t.ano,
                TarifaAnoDB.tipo == t.tipo_imovel,
                TarifaAnoDB.categoria_ligacao == t.categoria_ligacao,
            )
            .first()
        )
        if existing:
            # replace faixas
            db.query(TarifaFaixaDB).filter(TarifaFaixaDB.tarifa_ano_id == existing.id).delete()
            for f in t.faixas:
                db.add(
                    TarifaFaixaDB(
                        tarifa_ano_id=existing.id,
                        faixa=f.faixa,
                        consumo_min=f.consumo_min,
                        consumo_max=f.consumo_max,
                        valor_minimo=int(round((f.valor_minimo or 0) * 100)) if f.valor_minimo is not None else None,
                        valor_por_m3=int(round((f.valor_por_m3 or 0) * 100)) if f.valor_por_m3 is not None else None,
                    )
                )
            created.append(existing)
        else:
            novo = TarifaAnoDB(ano=t.ano, tipo=t.tipo_imovel, categoria_ligacao=t.categoria_ligacao)
            db.add(novo)
            db.flush()
            for f in t.faixas:
                db.add(
                    TarifaFaixaDB(
                        tarifa_ano_id=novo.id,
                        faixa=f.faixa,
                        consumo_min=f.consumo_min,
                        consumo_max=f.consumo_max,
                        valor_minimo=int(round((f.valor_minimo or 0) * 100)) if f.valor_minimo is not None else None,
                        valor_por_m3=int(round((f.valor_por_m3 or 0) * 100)) if f.valor_por_m3 is not None else None,
                    )
                )
            created.append(novo)
    db.commit()
    for item in created:
        db.refresh(item)
    return created
