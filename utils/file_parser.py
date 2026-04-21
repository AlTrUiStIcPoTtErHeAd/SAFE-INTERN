"""Robust file parsing for text, PDF, DOCX, and image OCR."""

from __future__ import annotations

import io
from typing import Dict, Tuple

try:
    import fitz  # type: ignore
except Exception:
    fitz = None

try:
    from docx import Document  # type: ignore
except Exception:
    Document = None

try:
    from PIL import Image  # type: ignore
except Exception:
    Image = None

try:
    import pytesseract  # type: ignore
except Exception:
    pytesseract = None


def _parse_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes with PyMuPDF."""
    if fitz is None:
        raise RuntimeError("PDF parsing dependency missing: install PyMuPDF.")
    text_chunks = []
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text_chunks.append(page.get_text("text"))
    return "\n".join(text_chunks).strip()


def _parse_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX bytes."""
    if Document is None:
        raise RuntimeError("DOCX dependency missing: install python-docx.")
    document = Document(io.BytesIO(file_bytes))
    return "\n".join([paragraph.text for paragraph in document.paragraphs]).strip()


def _parse_image(file_bytes: bytes) -> str:
    """Extract OCR text from image bytes."""
    if Image is None or pytesseract is None:
        raise RuntimeError("OCR dependencies missing: install Pillow and pytesseract.")
    image = Image.open(io.BytesIO(file_bytes))
    return pytesseract.image_to_string(image).strip()


def parse_uploaded_file(filename: str, file_bytes: bytes) -> Tuple[str, Dict[str, str]]:
    """Parse uploaded file content and return text + status metadata."""
    name = (filename or "").lower().strip()
    if not name or not file_bytes:
        return "", {"status": "error", "message": "Empty upload.", "type": "unknown"}

    try:
        if name.endswith((".txt", ".eml")):
            return file_bytes.decode("utf-8", errors="ignore"), {"status": "ok", "type": "text"}
        if name.endswith(".pdf"):
            try:
                extracted = _parse_pdf(file_bytes)
                if not extracted.strip():
                    return "", {"status": "error", "message": "PDF parsed but no text was detected.", "type": "pdf"}
                return extracted, {"status": "ok", "type": "pdf"}
            except Exception as exc:
                return "", {"status": "error", "message": f"PDF parsing failed gracefully: {exc}", "type": "pdf"}
        if name.endswith(".docx"):
            return _parse_docx(file_bytes), {"status": "ok", "type": "docx"}
        if name.endswith((".png", ".jpg", ".jpeg", ".webp")):
            return _parse_image(file_bytes), {"status": "ok", "type": "image_ocr"}
        return "", {"status": "error", "message": "Unsupported file type.", "type": "unsupported"}
    except Exception as exc:
        return "", {"status": "error", "message": f"Could not parse file safely: {exc}", "type": "error"}
