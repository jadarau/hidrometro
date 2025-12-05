from typing import List

from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi import status
from PIL import Image
import io

from app.agents.reading_agent import HydrometerReadingAgent
from app.models.schemas import HydrometerResponse, HydrometerResult
from app.config.settings import settings
from app.tools.ocr import _ensure_reader

router = APIRouter()

@router.post("/extract")
async def extract_ocr(
    files: List[UploadFile] = File(..., description="Imagens ou PDFs"),
    lang: str = Form("pt"),
    detail: bool = Form(False),
):
    try:
        _ensure_reader(lang)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    results = []
    for f in files:
        filename = f.filename or "file"
        content = await f.read()
        suffix = (filename.split(".")[-1] or "").lower()
        try:
            if suffix == "pdf":
                try:
                    from pdf2image import convert_from_bytes
                except Exception:
                    raise HTTPException(status_code=500, detail="pdf2image/poppler not available to convert PDFs.")
                pages = convert_from_bytes(content, dpi=300)
                page_values = []
                agent = HydrometerReadingAgent(lang=lang, detail=detail)
                for p in pages:
                    value = agent.read_from_image(p.convert("RGB"))
                    page_values.append(value)
                results.append({"filename": filename, "pages": page_values})
            else:
                img = Image.open(io.BytesIO(content)).convert("RGB")
                agent = HydrometerReadingAgent(lang=lang, detail=detail)
                value = agent.read_from_image(img)
                results.append({"filename": filename, "pages": [value]})
        finally:
            await f.close()

    return JSONResponse(results)

@router.post("/hydrometer/read", response_model=HydrometerResponse)
async def read_hydrometer(
    files: List[UploadFile] = File(..., description="Imagens ou PDFs de hidrômetros"),
    lang: str = Form("pt"),
    detail: bool = Form(False),
):
    try:
        _ensure_reader(lang)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    agent = HydrometerReadingAgent(lang=lang, detail=detail)
    results = []
    for f in files:
        filename = f.filename or "file"
        content = await f.read()
        suffix = (filename.split(".")[-1] or "").lower()
        if suffix not in settings.allowed_extensions:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Tipo de arquivo não permitido: {suffix}")
        size_mb = max(len(content), 1) / (1024 * 1024)
        if size_mb > settings.max_file_size_mb:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f"Arquivo excede {settings.max_file_size_mb} MB: {filename}")
        try:
            if suffix == "pdf":
                try:
                    from pdf2image import convert_from_bytes
                except Exception:
                    raise HTTPException(status_code=500, detail="pdf2image/poppler não disponível para PDFs.")
                pages = convert_from_bytes(content, dpi=300)
                if len(pages) == 0:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PDF sem páginas.")
                if len(pages) > settings.max_pdf_pages:
                    pages = pages[:settings.max_pdf_pages]
                # Choose the best page by IA consensus (first page for now)
                # Could later run best-of over multiple pages.
                value = agent.read_from_image(pages[0].convert("RGB"))
            else:
                img = Image.open(io.BytesIO(content)).convert("RGB")
                value = agent.read_from_image(img)
            results.append(HydrometerResult(filename=filename, valor_da_leitura=value))
        finally:
            await f.close()

    return HydrometerResponse(results=results)
