"""Planner/orchestrator that remains stable with optional dependencies."""

from __future__ import annotations

from typing import Any, Dict

from agents import ml_agent
from utils.pattern_detector import detect_scam_patterns

try:
    import crewai  # noqa: F401

    CREWAI_AVAILABLE = True
except Exception:
    CREWAI_AVAILABLE = False

try:
    import google.generativeai as genai  # noqa: F401

    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

try:
    import spacy  # noqa: F401

    SPACY_AVAILABLE = True
except Exception:
    SPACY_AVAILABLE = False


def _risk_label(score: int) -> str:
    """Convert numeric risk score to user-facing label."""
    if score < 20:
        return "Safe"
    if score < 40:
        return "Low Risk"
    if score < 65:
        return "Medium Risk"
    if score < 85:
        return "High Risk"
    return "Scam Likely"


def _combine_scores(ml_result: Dict[str, Any], rule_result: Dict[str, Any]) -> Dict[str, int]:
    """Combine ML and rule scores into final score and confidence."""
    ml_percent = int(ml_result.get("risk_percent", 0)) if ml_result.get("ml_used") else 0
    rule_score = int(rule_result.get("rule_score", 0))
    final_score = max(0, min(100, int(round(ml_percent * 0.6 + rule_score * 0.4))))
    confidence = min(100, max(15, int(round(45 + abs(ml_percent - 50) * 0.7 + abs(rule_score - 50) * 0.5))))
    return {
        "ml_percent": ml_percent,
        "rule_score": rule_score,
        "final_score": final_score,
        "confidence": confidence,
    }


def run_planner(intake_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run full planner flow with robust optional dependency guards."""
    normalized = intake_data if isinstance(intake_data, dict) else {"clean_text": str(intake_data or "")}
    text = str(normalized.get("clean_text", "") or "")
    ml_result = ml_agent.run_ml_analysis({"clean_text": text})
    pattern_result = detect_scam_patterns(text)
    score_payload = _combine_scores(ml_result, pattern_result)
    return {
        "ml": ml_result,
        "patterns": pattern_result,
        "scoring": {**score_payload, "label": _risk_label(score_payload["final_score"])},
        "integrations": {
            "crewai_enabled": False if not CREWAI_AVAILABLE else False,
            "gemini_available": GEMINI_AVAILABLE,
            "spacy_available": SPACY_AVAILABLE,
        },
    }
