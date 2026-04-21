# config/guardrail_words.py
"""
Guardrail vocabulary for SAFE-INTERN.

Purpose:
- Prevent accusations
- Prevent legal claims
- Ensure advisory-only language
"""

# ❌ Words that must NEVER appear in user output
FORBIDDEN_WORDS = {
    "scam",
    "fraud",
    "fake",
    "cheat",
    "criminal",
    "illegal",
    "con",
    "hoax",
    "ponzi",
    "extortion"
}

# ✅ Safe replacements (neutral & advisory)
SAFE_REPLACEMENTS = {
    "scam": "potential risk indicator",
    "fraud": "potentially misleading pattern",
    "fake": "unverified",
    "cheat": "unethical behavior",
    "criminal": "serious concern",
    "illegal": "possibly non-compliant",
    "con": "misleading practice",
    "hoax": "unverified claim",
    "ponzi": "high-risk financial pattern",
    "extortion": "coercive behavior"
}
