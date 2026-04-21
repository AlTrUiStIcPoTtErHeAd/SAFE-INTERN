# utils/pdf_parser.py
"""
PDF text extraction for SAFE-INTERN.

Purpose:
- Extract raw text from uploaded PDFs
- Used ONLY in intake stage
"""

import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    if not pdf_bytes:
        return ""

    text = []

    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            text.append(page.get_text())

    return "\n".join(text).strip()
