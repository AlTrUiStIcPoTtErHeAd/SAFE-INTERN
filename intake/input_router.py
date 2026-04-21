"""
Routes user input to the correct extractor
and returns raw text for intake processing.

Supported input types:
- Plain text
- PDF files
- URLs
"""

from typing import Optional, Tuple, Dict, Union

from utils.pdf_parser import extract_text_from_pdf
from utils.url_fetcher import fetch_text_from_url
from utils.text_cleaner import basic_clean_text


MAX_TEXT_LENGTH = 50000


def route_input(
    text_input: Optional[str] = None,
    pdf_file: Optional[bytes] = None,
    url: Optional[str] = None,
    return_metadata: bool = False
) -> Union[str, Tuple[str, Dict[str, any]]]:
    """
    Extract and normalize user input.

    Returns:
        - clean_text (str)
        - OR (clean_text, metadata) if return_metadata=True
    """

    raw_text = ""
    metadata: Dict[str, any] = {}

    # ---------- TEXT INPUT ----------
    if text_input and text_input.strip():
        raw_text = text_input.strip()
        metadata["input_type"] = "text"

        if len(raw_text) > MAX_TEXT_LENGTH:
            raise ValueError("Text input too long")

    # ---------- PDF INPUT ----------
    elif pdf_file:
        raw_text = extract_text_from_pdf(pdf_file)
        metadata["input_type"] = "pdf"
        metadata["file_size_bytes"] = len(pdf_file)

    # ---------- URL INPUT ----------
    elif url and url.strip():
        raw_text = fetch_text_from_url(url.strip())
        metadata["input_type"] = "url"
        metadata["url"] = url.strip()

    else:
        raise ValueError("No valid input provided")

    # ---------- BASIC CLEANING ----------
    clean_text = basic_clean_text(raw_text)

    if return_metadata:
        metadata["text_length"] = len(clean_text)
        return clean_text, metadata

    return clean_text
