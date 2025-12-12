from typing import List
from PIL import Image
import base64
import io

# Usamos o decorador @tool da LangChain Core para expor a função como ferramenta
try:
    from langchain_core.tools import tool
except Exception:  # fallback quando lib não estiver disponível
    def tool(fn):
        return fn

from app.tools.ocr import run_ocr_image


def _ocr_read_lines_image(img: Image.Image, lang: str = "pt", detail: bool = False) -> List[str]:
    """Função base: executa OCR em uma imagem PIL e retorna linhas de texto."""
    return run_ocr_image(img, lang=lang, detail=detail)


@tool("ocr_read_lines")
def ocr_read_lines(image_b64: str, lang: str = "pt", detail: bool = False) -> List[str]:
    """
    Lê linhas de texto de uma imagem de hidrômetro usando OCR.
    Parâmetros:
      - image_b64: imagem em base64 (PNG/JPEG)
      - lang: idioma (default: pt)
      - detail: se deve retornar com mais detalhes
    Retorna:
      - Lista de linhas de texto extraídas
    """
    try:
        data = base64.b64decode(image_b64)
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as e:
        raise ValueError(f"Imagem inválida em base64: {e}")
    return _ocr_read_lines_image(img, lang=lang, detail=detail)


# Também exportamos a função de conveniência para chamada direta com PIL.Image
def ocr_read_lines_image(img: Image.Image, lang: str = "pt", detail: bool = False) -> List[str]:
    return _ocr_read_lines_image(img, lang=lang, detail=detail)
from typing import List
from PIL import Image
from app.tools.ocr import run_ocr_image

class OCRTool:
    def __init__(self, lang: str = "pt", detail: bool = False):
        self.lang = lang
        self.detail = detail

    def extract_lines_from_image(self, img: Image.Image) -> List[str]:
        return run_ocr_image(img, lang=self.lang, detail=self.detail)
