from typing import List
from PIL import Image
import base64
import io
from app.tools.ocr_tool import ocr_read_lines, ocr_read_lines_image
from app.services.groq_client import GroqService
from app.services.faturas_service import calcular_fatura
from app.infrastructure.db import SessionLocal

def extract_matricula_from_filename(filename: str) -> int | None:
    try:
        base = filename.split('/')[-1].split('\\')[-1]
        prefix = base.split('_')[0]
        return int(prefix)
    except Exception:
        return None

class HydrometerReadingAgent:
    def __init__(self, lang: str = "pt", detail: bool = False, groq_model: str = "meta-llama/llama-4-maverick-17b-128e-instruct"):
        self.lang = lang
        self.detail = detail
        # Ferramentas disponíveis para o agente (expostas via @tool)
        self.tools = [ocr_read_lines]
        self.groq = GroqService(model=groq_model)

    def read_from_image(self, img: Image.Image) -> str:
        # First try vision model directly on image
        try:
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            image_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            return self.groq.extract_digits_from_image_base64(image_b64)
        except Exception:
            # Fallback para OCR via ferramenta @tool
            try:
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                image_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
                lines: List[str] = self.tools[0].invoke({
                    "image_b64": image_b64,
                    "lang": self.lang,
                    "detail": self.detail,
                })
            except Exception:
                # Fallback direto sem o wrapper de ferramenta
                lines = ocr_read_lines_image(img, lang=self.lang, detail=self.detail)
            ocr_text = "\n".join(lines)
            return self.groq.extract_digits(ocr_text)

    def generate_invoice_from_reading(self, filename: str, leitura_valor: int, ano: int) -> dict:
        matricula = extract_matricula_from_filename(filename)
        if matricula is None:
            raise ValueError("Nome de arquivo inválido. Esperado '<matricula>_resto.ext'.")
        req = {
            "matricula_imovel": matricula,
            "ano": ano,
            "consumo_m3": int(leitura_valor),
        }
        db = SessionLocal()
        try:
            resp = calcular_fatura(db, type("Obj", (), req))
            return {
                "matricula_imovel": resp.matricula_imovel,
                "ano": resp.ano,
                "consumo_m3": resp.consumo_m3,
                "valor_agua": resp.valor_agua,
                "valor_esgoto": resp.valor_esgoto,
                "total": resp.total,
                "detalhamento": resp.detalhamento,
            }
        finally:
            db.close()
