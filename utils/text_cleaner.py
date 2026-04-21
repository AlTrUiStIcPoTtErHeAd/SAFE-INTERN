# utils/text_cleaner.py
"""
Minimal text cleaning utilities for SAFE-INTERN.

Purpose:
- Normalize raw text
- Remove noise
- Preserve meaning
- NO NLP
- NO scoring
"""

import re
from typing import List, Dict, Any


# ---------- REGEX ----------

EMAIL_PATTERN = re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w{2,}\b')
URL_PATTERN = re.compile(r'https?://\S+|www\.\S+')
PHONE_PATTERN = re.compile(r'\+?\d[\d\s\-]{7,}\d')


# ---------- BASIC CLEAN ----------

def basic_clean_text(text: str) -> str:
    if not text:
        return ""

    text = str(text)

    # Normalize newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove non-printable chars
    text = re.sub(r'[\x00-\x1F\x7F]', ' ', text)

    # Normalize spaces
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)

    return text.strip()


# ---------- EXTRACTION ----------

def extract_emails(text: str) -> List[str]:
    return list(set(EMAIL_PATTERN.findall(text)))


def extract_urls(text: str) -> List[str]:
    return list(set(URL_PATTERN.findall(text)))


def extract_phones(text: str) -> List[str]:
    return list(set(PHONE_PATTERN.findall(text)))


# ---------- VALIDATION ----------

def validate_text(text: str, min_length: int = 10) -> Dict[str, Any]:
    cleaned = basic_clean_text(text)
    length = len(cleaned)

    if length < min_length:
        return {
            "valid": False,
            "length": length,
            "reason": "Text too short"
        }

    return {
        "valid": True,
        "length": length,
        "words": len(cleaned.split())
    }
