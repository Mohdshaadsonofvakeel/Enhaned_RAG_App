from io import BytesIO
from typing import Tuple
import re

try:
    import magic as filemagic  # linux/mac
except Exception:
    try:
        import magic  # sometimes python-magic imports as magic
        filemagic = magic
    except Exception:
        filemagic = None

from PyPDF2 import PdfReader
from docx import Document
from PIL import Image

import pytesseract

from .ai_providers.gemini_provider import ocr_image_with_gemini

def _detect_mime(content: bytes, filename: str) -> str:
    if filemagic:
        try:
            return filemagic.from_buffer(content, mime=True)
        except Exception:
            pass
    # fallback: guess from extension
    ext = (filename or "").lower()
    if ext.endswith(".pdf"):
        return "application/pdf"
    if ext.endswith(".docx"):
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if ext.endswith(".txt") or ext.endswith(".md"):
        return "text/plain"
    if any(ext.endswith(x) for x in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"]):
        return "image/*"
    return "application/octet-stream"

def extract_text_from_file(filename: str, file_bytes: bytes, use_gemini_vision: bool = True) -> Tuple[str, str]:
    """Return (text, mime_type) from a single file's bytes, using OCR for images.
    """
    mime = _detect_mime(file_bytes, filename)
    if mime == "application/pdf":
        return extract_text_from_pdf(file_bytes), mime
    elif mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(file_bytes), mime
    elif mime.startswith("text/"):
        return extract_text_from_text(file_bytes), mime
    elif mime.startswith("image/") or mime == "image/*":
        if use_gemini_vision:
            try:
                txt = ocr_image_with_gemini(file_bytes)
                if txt and txt.strip():
                    return txt, mime
            except Exception:
                pass
        # fallback to Tesseract
        return extract_text_from_image(file_bytes), mime
    else:
        # try best effort plain decoding
        return extract_text_from_text(file_bytes), mime

def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    text_parts = []
    for page in reader.pages:
        # PyPDF2 extract_text can be None
        ptxt = page.extract_text() or ""
        text_parts.append(ptxt)
    return "\n".join(text_parts)

def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(BytesIO(file_bytes))
    parts = []
    for para in doc.paragraphs:
        parts.append(para.text)
    return "\n".join(parts)

def extract_text_from_text(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode("utf-8", errors="ignore")
    except Exception:
        return file_bytes.decode("latin-1", errors="ignore")

def extract_text_from_image(file_bytes: bytes) -> str:
    img = Image.open(BytesIO(file_bytes))
    return pytesseract.image_to_string(img)

def normalize_whitespace(s: str) -> str:
    s = re.sub(r"\r\n|\r|\n", " \n ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()
