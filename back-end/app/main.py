from fastapi import FastAPI

from app.routers import ocr
from app.routers import pessoas
from app.routers import imoveis
from app.infrastructure.db import init_db

app = FastAPI(title="OCR API", version="1.0.0")

init_db()

app.include_router(ocr.router, prefix="/api", tags=["ocr"])
app.include_router(pessoas.router, prefix="/api")
app.include_router(imoveis.router, prefix="/api")

@app.get("/")
async def root():
    return {"status": "ok", "service": "ocr"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
