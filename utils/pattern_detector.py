"""Rule-based scam pattern detection with weighted risk scoring."""

from __future__ import annotations

import re
from typing import Dict, List


PATTERN_CONFIG: Dict[str, Dict[str, object]] = {
    "upi_ids": {"regex": r"\b[\w.\-]{2,}@[a-zA-Z]{2,}\b", "weight": 18, "description": "UPI ID or payment handle detected"},
    "payment_requests": {
        "regex": r"\b(pay now|registration amount|registration fee|security deposit|training fee|processing fee|transfer amount|payment required|scan qr to continue)\b",
        "weight": 24,
        "description": "Direct payment request language",
    },
    "otp_requests": {"regex": r"\b(share otp|send otp|verification code|one time password)\b", "weight": 20, "description": "OTP request detected"},
    "suspicious_urls": {"regex": r"(https?://[^\s]+|www\.[^\s]+)", "weight": 10, "description": "URL present (verify domain trust)"},
    "public_domains": {"regex": r"\b[\w.\-]+@(gmail\.com|yahoo\.com|outlook\.com|hotmail\.com)\b", "weight": 14, "description": "Public email domain used"},
    "fake_domains": {
        "regex": r"\b(careers-company-job\.com|hr-job-alert\.net|companycareers-gmail\.com|[\w\-]+career[s]?\-[\w\-]+\.(com|net|org))\b",
        "weight": 22,
        "description": "Suspicious or spoofed domain pattern detected",
    },
    "telegram_usernames": {"regex": r"(@[a-zA-Z0-9_]{5,}\b|\bt\.me/[a-zA-Z0-9_]+\b)", "weight": 14, "description": "Telegram contact handle detected"},
    "whatsapp_numbers": {"regex": r"\b(\+?\d{1,3}[-\s]?)?\d{10}\b", "weight": 12, "description": "WhatsApp-like phone contact detected"},
    "qr_codes": {"regex": r"\b(qr code|scan code|scan qr|scan qr to continue)\b", "weight": 16, "description": "QR code payment language"},
    "aadhaar_numbers": {"regex": r"\b\d{4}\s?\d{4}\s?\d{4}\b", "weight": 16, "description": "Aadhaar-like number found"},
    "pan_cards": {"regex": r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", "weight": 15, "description": "PAN format detected"},
    "bank_accounts": {"regex": r"\b\d{9,18}\b", "weight": 14, "description": "Possible bank account number detected"},
    "ifsc_codes": {"regex": r"\b[A-Z]{4}0[A-Z0-9]{6}\b", "weight": 15, "description": "IFSC code format found"},
    "unrealistic_salary": {
        "regex": r"\b(earn ₹?50,?000 in first month|guaranteed placement|100% selection|no interview needed|[1-9][0-9]{5,}|80k|90k|1 lakh|2 lakh)\b",
        "weight": 16,
        "description": "Unrealistic salary or guaranteed selection claim",
    },
    "urgency_language": {
        "regex": r"\b(immediately|urgent|limited seats|confirm today|confirm now|immediate joining|offer valid for 1 hour|last chance|act fast|click below to verify)\b",
        "weight": 14,
        "description": "High-pressure urgency language",
    },
}

SCAM_KEYWORDS: List[str] = [
    "telegram", "whatsapp", "registration amount", "registration fee", "security deposit", "training fee", "qr code",
    "scan qr to continue", "offer valid for 1 hour", "pay now", "confirm today", "immediate joining",
    "guaranteed placement", "100% selection", "no interview needed", "click below to verify",
]


def _clip_matches(matches: List[str]) -> List[str]:
    """Trim and cap matched values to keep UI readable."""
    return [m.strip() for m in matches if m and m.strip()][:5]


def detect_scam_patterns(text: str) -> Dict[str, object]:
    """Detect suspicious regex patterns and return weighted rule score."""
    source = (text or "").strip()
    if not source:
        return {"rule_score": 0, "found_patterns": {}, "reasons": [], "keyword_hits": [], "keyword_count": 0}

    found_patterns: Dict[str, List[str]] = {}
    reasons: List[str] = []
    weighted_score = 0
    lowered = source.lower()

    for pattern_name, config in PATTERN_CONFIG.items():
        regex = str(config["regex"])
        matches = re.findall(regex, source, flags=re.IGNORECASE)
        normalized: List[str] = []
        for match in matches:
            if isinstance(match, tuple):
                normalized.append(" ".join([str(item) for item in match if item]).strip())
            else:
                normalized.append(str(match))
        cleaned_matches = _clip_matches(normalized)
        if cleaned_matches:
            found_patterns[pattern_name] = cleaned_matches
            weighted_score += int(config["weight"])
            reasons.append(str(config["description"]))

    keyword_hits = sorted({kw for kw in SCAM_KEYWORDS if kw in lowered})
    keyword_bonus = min(20, len(keyword_hits) * 2)
    final_rule_score = max(0, min(100, weighted_score + keyword_bonus))
    return {
        "rule_score": final_rule_score,
        "found_patterns": found_patterns,
        "reasons": reasons,
        "keyword_hits": keyword_hits,
        "keyword_count": len(keyword_hits),
    }
