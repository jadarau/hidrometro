from typing import Optional
from fastapi import HTTPException

from app.infrastructure.db import SessionLocal
from app.infrastructure.orm_models import ImovelDB, PessoaDB
from app.models.schemas import ImovelCreate, Imovel
from app.services.pagination import resolve_page, resolve_order


def criar_imovel(payload: ImovelCreate) -> Imovel:
    with SessionLocal() as db:
        pessoa = db.get(PessoaDB, payload.id_pessoa)
        if not pessoa:
            raise HTTPException(status_code=400, detail="Pessoa associada inexistente")
        obj = ImovelDB(**payload.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return Imovel(
            matricula=obj.matricula,
            id_pessoa=obj.id_pessoa,
            categoria=obj.categoria,
            tipo=obj.tipo,
            endereco=obj.endereco,
            numero=obj.numero,
            bairro=obj.bairro,
            cidade=obj.cidade,
            uf=obj.uf,
            cep=obj.cep,
            esgoto=obj.esgoto,
            consumo_misto=obj.consumo_misto,
        )


def listar_imoveis(
    cidade: Optional[str],
    categoria: Optional[str],
    ativo: Optional[bool],
    cep: Optional[str],
    page: str,
    page_size: int,
    sort_by: str,
    order: str,
):
    with SessionLocal() as db:
        q = db.query(ImovelDB)
        if cidade:
            q = q.filter(ImovelDB.cidade.ilike(f"%{cidade}%"))
        if categoria:
            q = q.filter(ImovelDB.categoria == categoria)
        if cep:
            q = q.filter(ImovelDB.cep == cep)
        if ativo is not None:
            q = q.join(PessoaDB).filter(PessoaDB.ativo == ativo)

        sort_map = {
            "cidade": ImovelDB.cidade,
            "categoria": ImovelDB.categoria,
            "cep": ImovelDB.cep,
            "bairro": ImovelDB.bairro,
            "uf": ImovelDB.uf,
        }
        sort_col = sort_map.get(sort_by, ImovelDB.cidade)
        order_norm = resolve_order(order)
        q = q.order_by(sort_col.desc() if order_norm == "desc" else sort_col.asc())

        total = q.count()
        page_number = resolve_page(page, total, page_size)
        rows = q.offset((page_number - 1) * page_size).limit(page_size).all()
        items = [
            Imovel(
                matricula=r.matricula,
                id_pessoa=r.id_pessoa,
                categoria=r.categoria,
                tipo=r.tipo,
                endereco=r.endereco,
                numero=r.numero,
                bairro=r.bairro,
                cidade=r.cidade,
                uf=r.uf,
                cep=r.cep,
                esgoto=r.esgoto,
                consumo_misto=r.consumo_misto,
            ) for r in rows
        ]
        return total, page_number, items


def obter_imovel(matricula: int) -> Imovel:
    with SessionLocal() as db:
        r = db.get(ImovelDB, matricula)
        if not r:
            raise HTTPException(status_code=404, detail="Imóvel não encontrado")
        return Imovel(
            matricula=r.matricula,
            id_pessoa=r.id_pessoa,
            categoria=r.categoria,
            tipo=r.tipo,
            endereco=r.endereco,
            numero=r.numero,
            bairro=r.bairro,
            cidade=r.cidade,
            uf=r.uf,
            cep=r.cep,
            esgoto=r.esgoto,
            consumo_misto=r.consumo_misto,
        )


def atualizar_imovel(matricula: int, payload: ImovelCreate) -> Imovel:
    with SessionLocal() as db:
        r = db.get(ImovelDB, matricula)
        if not r:
            raise HTTPException(status_code=404, detail="Imóvel não encontrado")
        pessoa = db.get(PessoaDB, payload.id_pessoa)
        if not pessoa:
            raise HTTPException(status_code=400, detail="Pessoa associada inexistente")
        for k, v in payload.model_dump().items():
            setattr(r, k, v)
        db.commit()
        db.refresh(r)
        return Imovel(
            matricula=r.matricula,
            id_pessoa=r.id_pessoa,
            categoria=r.categoria,
            tipo=r.tipo,
            endereco=r.endereco,
            numero=r.numero,
            bairro=r.bairro,
            cidade=r.cidade,
            uf=r.uf,
            cep=r.cep,
            esgoto=r.esgoto,
            consumo_misto=r.consumo_misto,
        )


def remover_imovel(matricula: int) -> None:
    with SessionLocal() as db:
        r = db.get(ImovelDB, matricula)
        if not r:
            raise HTTPException(status_code=404, detail="Imóvel não encontrado")
        db.delete(r)
        db.commit()