from typing import Optional, List
from fastapi import HTTPException

from app.infrastructure.db import SessionLocal
from app.infrastructure.orm_models import PessoaDB
from app.models.schemas import PessoaCreate, Pessoa
from app.services.pagination import resolve_page, resolve_order


def criar_pessoa(payload: PessoaCreate) -> Pessoa:
    with SessionLocal() as db:
        existing = db.query(PessoaDB).filter(PessoaDB.documento == payload.documento).first()
        if existing:
            raise HTTPException(status_code=400, detail="Documento já cadastrado para outra pessoa")
        obj = PessoaDB(**payload.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return Pessoa(
            matricula=obj.matricula,
            tipo_doc=obj.tipo_doc,
            documento=obj.documento,
            nome=obj.nome,
            sobre_nome=obj.sobre_nome,
            nascimento=obj.nascimento,
            sexo=obj.sexo,
            ativo=obj.ativo,
            id_endereco_fatura=obj.id_endereco_fatura,
        )


def listar_pessoas(
    tipo_doc: Optional[str],
    documento: Optional[str],
    nome: Optional[str],
    sobre_nome: Optional[str],
    sexo: Optional[str],
    ativo: Optional[bool],
    nascimento: Optional[str],
    page: str,
    page_size: int,
    sort_by: str,
    order: str,
):
    with SessionLocal() as db:
        q = db.query(PessoaDB)
        if tipo_doc:
            q = q.filter(PessoaDB.tipo_doc == tipo_doc)
        if documento:
            q = q.filter(PessoaDB.documento.contains(documento))
        if nome:
            q = q.filter(PessoaDB.nome.ilike(f"%{nome}%"))
        if sobre_nome:
            q = q.filter(PessoaDB.sobre_nome.ilike(f"%{sobre_nome}%"))
        if sexo:
            q = q.filter(PessoaDB.sexo == sexo)
        if ativo is not None:
            q = q.filter(PessoaDB.ativo == ativo)
        if nascimento:
            q = q.filter(PessoaDB.nascimento == nascimento)
        sort_map = {
            "nome": PessoaDB.nome,
            "sobre_nome": PessoaDB.sobre_nome,
            "documento": PessoaDB.documento,
            "sexo": PessoaDB.sexo,
            "ativo": PessoaDB.ativo,
            "nascimento": PessoaDB.nascimento,
        }
        sort_col = sort_map.get(sort_by, PessoaDB.nome)
        order_norm = resolve_order(order)
        q = q.order_by(sort_col.desc() if order_norm == "desc" else sort_col.asc())

        total = q.count()
        page_number = resolve_page(page, total, page_size)
        rows = q.offset((page_number - 1) * page_size).limit(page_size).all()
        items = [
            Pessoa(
                matricula=r.matricula,
                tipo_doc=r.tipo_doc,
                documento=r.documento,
                nome=r.nome,
                sobre_nome=r.sobre_nome,
                nascimento=r.nascimento,
                sexo=r.sexo,
                ativo=r.ativo,
                id_endereco_fatura=r.id_endereco_fatura,
            ) for r in rows
        ]
        return total, page_number, items


def obter_pessoa(matricula: int) -> Pessoa:
    with SessionLocal() as db:
        r = db.get(PessoaDB, matricula)
        if not r:
            raise HTTPException(status_code=404, detail="Pessoa não encontrada")
        return Pessoa(
            matricula=r.matricula,
            tipo_doc=r.tipo_doc,
            documento=r.documento,
            nome=r.nome,
            sobre_nome=r.sobre_nome,
            nascimento=r.nascimento,
            sexo=r.sexo,
            ativo=r.ativo,
            id_endereco_fatura=r.id_endereco_fatura,
        )


def atualizar_pessoa(matricula: int, payload: PessoaCreate) -> Pessoa:
    with SessionLocal() as db:
        r = db.get(PessoaDB, matricula)
        if not r:
            raise HTTPException(status_code=404, detail="Pessoa não encontrada")
        # garantimos unicidade do documento ao atualizar
        existing = db.query(PessoaDB).filter(PessoaDB.documento == payload.documento, PessoaDB.matricula != matricula).first()
        if existing:
            raise HTTPException(status_code=400, detail="Documento já cadastrado para outra pessoa")
        for k, v in payload.model_dump().items():
            setattr(r, k, v)
        db.commit()
        db.refresh(r)
        return Pessoa(
            matricula=r.matricula,
            tipo_doc=r.tipo_doc,
            documento=r.documento,
            nome=r.nome,
            sobre_nome=r.sobre_nome,
            nascimento=r.nascimento,
            sexo=r.sexo,
            ativo=r.ativo,
            id_endereco_fatura=r.id_endereco_fatura,
        )


def remover_pessoa(matricula: int) -> None:
    with SessionLocal() as db:
        r = db.get(PessoaDB, matricula)
        if not r:
            raise HTTPException(status_code=404, detail="Pessoa não encontrada")
        db.delete(r)
        db.commit()