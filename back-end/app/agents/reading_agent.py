from typing import List
from PIL import Image
import base64
import io
from app.tools.ocr_tool import OCRTool
from app.services.groq_client import GroqService

class HydrometerReadingAgent:
    def __init__(self, lang: str = "pt", detail: bool = False, groq_model: str = "meta-llama/llama-4-maverick-17b-128e-instruct"):
        self.ocr = OCRTool(lang=lang, detail=detail)
        self.groq = GroqService(model=groq_model)

    def read_from_image(self, img: Image.Image) -> str:
        # First try vision model directly on image
        try:
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            image_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            return self.groq.extract_digits_from_image_base64(image_b64)
        except Exception:
            # Fallback to OCR + text LLM parsing
            lines: List[str] = self.ocr.extract_lines_from_image(img)
            ocr_text = "\n".join(lines)
            return self.groq.extract_digits(ocr_text)
