from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.infrastructure.db import get_db
from app.models.schemas import FaturaCalculoRequest, FaturaCalculoResponse
from app.services.faturas_service import calcular_fatura

router = APIRouter(prefix="/faturas", tags=["faturas"])

@router.post("/calcular", response_model=FaturaCalculoResponse)
def calcular(req: FaturaCalculoRequest, db: Session = Depends(get_db)):
    return calcular_fatura(db, req)