"""Helpers for generating SAFE-INTERN downloadable reports."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict


def build_report_payload(
    source_text: str,
    ml_result: Dict[str, Any],
    pattern_result: Dict[str, Any],
    scoring: Dict[str, Any],
    integrations: Dict[str, Any],
) -> Dict[str, Any]:
    """Build normalized report payload for downloads and logs."""
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_preview": source_text[:500],
        "input_length": len(source_text),
        "scoring": scoring,
        "ml": ml_result,
        "patterns": pattern_result,
        "integrations": integrations,
    }


def render_report_json(report_payload: Dict[str, Any]) -> str:
    """Render report payload as pretty JSON string."""
    return json.dumps(report_payload, indent=2, ensure_ascii=False)


def render_text_summary(report_payload: Dict[str, Any]) -> str:
    """Create a concise text summary from report payload."""
    scoring = report_payload.get("scoring", {})
    ml = report_payload.get("ml", {})
    patterns = report_payload.get("patterns", {})
    lines = [
        "SAFE-INTERN Risk Summary",
        f"Risk Label: {scoring.get('label', 'Unknown')}",
        f"Final Score: {scoring.get('final_score', 0)}/100",
        f"Confidence: {scoring.get('confidence', 0)}%",
        f"ML Used: {ml.get('ml_used', False)}",
        f"Rule Score: {patterns.get('rule_score', 0)}",
        f"Keyword Hits: {patterns.get('keyword_count', 0)}",
    ]
    return "\n".join(lines)
