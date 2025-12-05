import os
from pydantic import BaseModel


class AppSettings(BaseModel):
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    max_pdf_pages: int = int(os.getenv("MAX_PDF_PAGES", "5"))
    allowed_extensions: tuple[str, ...] = ("png", "jpg", "jpeg", "pdf")
    # WARNING: use apenas variáveis de ambiente; nunca hardcode segredos.
    groq_api_key: str | None = os.getenv("GROQ_API_KEY", "SEU_API_KEY_AQUI")
    groq_model: str = os.getenv("GROQ_MODEL", "meta-llama/llama-4-maverick-17b-128e-instruct")
    # Database (psycopg v3)
    db_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg://ocruser:ocrpass@localhost:5432/hidrometro")


settings = AppSettings()