import argparse
import os
from typing import List, Optional

import numpy as np
from PIL import Image

try:
    import cv2  # type: ignore
except Exception:
    cv2 = None

try:
    from pdf2image import convert_from_path, convert_from_bytes  # type: ignore
except Exception:
    convert_from_path = None
    convert_from_bytes = None

try:
    import easyocr  # type: ignore
except Exception:
    easyocr = None


def _ensure_reader(lang: str = "pt"):
    if easyocr is None:
        raise RuntimeError("EasyOCR is not installed. Install dependencies first.")
    return easyocr.Reader([lang], gpu=False)


def _load_images(path: str) -> List[Image.Image]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input file not found: {path}")
    suffix = os.path.splitext(path)[1].lower()
    if suffix in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}:
        return [Image.open(path).convert("RGB")]
    elif suffix == ".pdf":
        if convert_from_path is None:
            raise RuntimeError("pdf2image/poppler not available to convert PDFs.")
        pages = convert_from_path(path, dpi=300)
        if not pages:
            raise RuntimeError("No pages found in PDF.")
        return [p.convert("RGB") for p in pages]
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def _preprocess(img: Image.Image) -> np.ndarray:
    arr = np.array(img)
    if cv2 is None:
        return arr
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    thr = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, 31, 10)
    return cv2.cvtColor(thr, cv2.COLOR_GRAY2RGB)


def run_ocr(path: str, lang: str = "pt", detail: bool = False) -> List[List[str]]:
    reader = _ensure_reader(lang)
    images = _load_images(path)
    pages_text: List[List[str]] = []
    for img in images:
        pre = _preprocess(img)
        results = reader.readtext(pre)
        if detail:
            lines = [f"{text} (conf={conf:.3f})" for (_, text, conf) in results]
        else:
            lines = [text for (_, text, _) in results]
        pages_text.append(lines)
    return pages_text


def run_ocr_image(img: Image.Image, lang: str = "pt", detail: bool = False) -> List[str]:
    reader = _ensure_reader(lang)
    pre = _preprocess(img)
    results = reader.readtext(pre)
    if detail:
        return [f"{text} (conf={conf:.3f})" for (_, text, conf) in results]
    else:
        return [text for (_, text, _) in results]


def save_text(pages: List[List[str]], output: Optional[str], per_page: bool) -> None:
    if not output:
        for i, lines in enumerate(pages, start=1):
            print(f"--- Page {i} ---")
            print("\n".join(lines))
        return
    out_dir = os.path.dirname(output) or "."
    os.makedirs(out_dir, exist_ok=True)
    if per_page and len(pages) > 1:
        base, ext = os.path.splitext(output)
        ext = ext or ".txt"
        for i, lines in enumerate(pages, start=1):
            page_out = f"{base}_page{i}{ext}"
            with open(page_out, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
    else:
        merged = []
        for i, lines in enumerate(pages, start=1):
            merged.append(f"--- Page {i} ---")
            merged.extend(lines)
        with open(output, "w", encoding="utf-8") as f:
            f.write("\n".join(merged))


def main():
    parser = argparse.ArgumentParser(description="Simple OCR pipeline using EasyOCR")
    parser.add_argument("input", help="Path to image or PDF file")
    parser.add_argument("-o", "--output", help="Path to save extracted text")
    parser.add_argument("-l", "--lang", default="pt", help="OCR language (default: pt)")
    parser.add_argument("-d", "--detail", action="store_true", help="Include confidence values")
    parser.add_argument("--per-page", action="store_true", help="When outputting PDFs, save one file per page")
    args = parser.parse_args()

    pages = run_ocr(args.input, lang=args.lang, detail=args.detail)
    save_text(pages, args.output, args.per_page)


if __name__ == "__main__":
    main()
