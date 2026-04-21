# utils/guardrails.py
"""
Guardrails for SAFE-INTERN.

Purpose:
- Enforce advisory-only language
- Prevent accusations or legal conclusions
- Replace forbidden words before user display
- Validate output safety before UI rendering

Runs AFTER explanation_engine
Runs BEFORE Streamlit UI
"""

from typing import Dict, Any, List, Tuple
import re
from config.guardrail_words import FORBIDDEN_WORDS, SAFE_REPLACEMENTS


# ---------- ACCUSATORY PATTERNS ----------

ACCUSATORY_PATTERNS = [
    r'\bthis is (a )?(scam|fraud)\b',
    r'\bdefinitely (a )?(scam|fraud)\b',
    r'\bobviously (a )?(scam|fraud)\b',
    r'\bguaranteed (to be )?(a )?(scam|fraud)\b',
]


# ---------- CORE SANITIZATION ----------

def sanitize_text(text: str) -> str:
    """
    Sanitize user-facing text by:
    - Replacing forbidden words
    - Removing accusatory statements
    """

    if not text:
        return ""

    sanitized = text

    # Replace forbidden words
    for bad_word in FORBIDDEN_WORDS:
        if bad_word.lower() in sanitized.lower():
            replacement = SAFE_REPLACEMENTS.get(
                bad_word, "potential risk indicator"
            )
            sanitized = _replace_case_insensitive(
                sanitized, bad_word, replacement
            )

    # Remove accusatory patterns
    for pattern in ACCUSATORY_PATTERNS:
        sanitized = re.sub(
            pattern,
            "shows patterns that may require careful verification",
            sanitized,
            flags=re.IGNORECASE
        )

    return sanitized


def _replace_case_insensitive(text: str, target: str, replacement: str) -> str:
    pattern = re.compile(r'\b' + re.escape(target) + r'\b', re.IGNORECASE)
    return pattern.sub(replacement, text)


# ---------- STRUCTURED GUARDRAILS ----------

def apply_guardrails(output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively apply guardrails to explanation output.
    """

    guarded = {}

    for key, value in output.items():
        if isinstance(value, str):
            guarded[key] = sanitize_text(value)

        elif isinstance(value, list):
            guarded[key] = [
                sanitize_text(v) if isinstance(v, str) else v
                for v in value
            ]

        elif isinstance(value, dict):
            guarded[key] = apply_guardrails(value)

        else:
            guarded[key] = value

    return guarded


def apply_full_guardrails(output: Dict[str, Any]) -> Dict[str, Any]:
    guarded = apply_guardrails(output)
    is_safe, violations = final_output_check(guarded)

    if not is_safe:
        # last-resort sanitization (safe fallback)
        guarded = apply_guardrails(guarded)

    return guarded


# ---------- FINAL SAFETY VALIDATION ----------

def final_output_check(output: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Ensure no forbidden or accusatory language remains.
    """

    violations = []

    def scan(obj: Any, path: str = "root"):
        if isinstance(obj, str):
            for word in FORBIDDEN_WORDS:
                if word.lower() in obj.lower():
                    violations.append(f"Forbidden word '{word}' at {path}")

            for pattern in ACCUSATORY_PATTERNS:
                if re.search(pattern, obj, re.IGNORECASE):
                    violations.append(f"Accusatory pattern at {path}")

        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                scan(item, f"{path}[{i}]")

        elif isinstance(obj, dict):
            for k, v in obj.items():
                scan(v, f"{path}.{k}")

    scan(output)

    return len(violations) == 0, violations
