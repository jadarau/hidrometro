from typing import List
from PIL import Image
from app.tools.ocr import run_ocr_image

class OCRTool:
    def __init__(self, lang: str = "pt", detail: bool = False):
        self.lang = lang
        self.detail = detail

    def extract_lines_from_image(self, img: Image.Image) -> List[str]:
        return run_ocr_image(img, lang=self.lang, detail=self.detail)
