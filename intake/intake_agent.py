"""
Intake agent for SAFE-INTERN.

Responsibilities:
- Convert raw cleaned text into structured IntakeSchema
- Uses OpenRouter LLM (JSON-only)
- Safe fallback if LLM fails

ONLY FILE USING OPENROUTER
"""

from typing import Dict, Any
import os
import re
import json
import requests

from intake.schema import IntakeSchema, build_intake_schema
from config.settings import (
    LLM_ENABLED,
    LLM_MODEL_NAME,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


# ------------------------------------------------------------------
# FALLBACK (DETERMINISTIC & SAFE)
# ------------------------------------------------------------------

def fallback_structuring(text: str) -> Dict[str, Any]:
    email_match = re.search(
        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text
    )
    url_match = re.search(r"https?://\S+|www\.\S+", text)

    payment_keywords = ["fee", "payment", "deposit", "registration", "charges"]
    urgency_keywords = ["urgent", "immediately", "limited", "asap", "hurry"]

    return {
        "clean_text": text,

        # Company / contact
        "company_name": None,
        "contact_person": None,
        "email": email_match.group(0) if email_match else None,
        "phone": None,
        "website": url_match.group(0) if url_match else None,
        "social_media": [],

        # Job info
        "job_title": None,
        "job_description": None,
        "location": None,
        "duration": None,
        "compensation": None,
        "start_date": None,

        # Indicators
        "payment_mentions": any(k in text.lower() for k in payment_keywords),
        "payment_required": False,
        "payment_amount": None,

        "urgency_mentions": any(k in text.lower() for k in urgency_keywords),
        "urgency_phrases": [],

        "interview_process_described": False,
        "communication_channels": [],

        # Analysis helpers
        "missing_information": [],
        "unusual_patterns": {},
        "entities": {},

        # Metadata
        "input_length": len(text),
        "language_detected": None,
    }


# ------------------------------------------------------------------
# GOOGLE GEMINI LLM
# ------------------------------------------------------------------

import google.generativeai as genai

def run_llm_intake(text: str) -> Dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(LLM_MODEL_NAME)

    system_prompt = """
    You are an intake parser for an internship safety system.

    Rules:
    - Output ONLY valid JSON
    - No explanations
    - No accusations or judgments
    - Use null when information is missing

    Required keys:
    clean_text, company_name, email, website,
    payment_mentions, payment_required,
    urgency_mentions, input_length
    """

    prompt = f"{system_prompt}\n\nInput Text:\n{text}\n\nOutput JSON:"

    try:
        response = model.generate_content(prompt)
        content = response.text
        
        # Clean markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
            
        raw = json.loads(content)
        # print(f"DEBUG: Gemini Parsed JSON: {raw}")

        # 🔐 NORMALIZE to schema-compatible dict
        base = fallback_structuring(text)
        base.update({k: raw.get(k) for k in raw if k in base})
        
        return base

    except Exception as e:
        # print(f"DEBUG: Gemini Error: {e}")
        raise e


# ------------------------------------------------------------------
# MAIN ENTRY
# ------------------------------------------------------------------

def run_intake(text: str) -> IntakeSchema:
    if not text or not text.strip():
        raise ValueError("Input text is empty")

    if not LLM_ENABLED:
        structured = fallback_structuring(text)
    else:
        try:
            structured = run_llm_intake(text)
        except Exception as e:
            print(f"DEBUG: Intake Exception: {e}")
            structured = fallback_structuring(text)

    return build_intake_schema(structured)
