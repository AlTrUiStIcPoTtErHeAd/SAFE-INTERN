"""
Risk engine for SAFE-INTERN.

Responsibilities:
- Combine signals from all agents
- Produce a final advisory risk score (0–100)
- Assign a risk category (Low / Caution / High Indicators)
- Provide transparent breakdown

NO accusations
NO absolute claims
NO data storage
"""

from typing import Dict, Any, Tuple, List


# ---------- CONFIGURATION ----------

AGENT_MAX_SCORES = {
    "company": 30,
    "payment": 30,
    "behavior": 20,
    "ml": 20,
}

RISK_CATEGORIES = [
    (30, "Low Risk Indicators"),
    (60, "Caution Advised"),
    (100, "High Risk Indicators"),
]


# ---------- NORMALIZED RULES ----------

COMPANY_RULES = {
    "not reachable": 10,
    "does not use https": 5,
    "free email domain": 10,
    "email domain does not match": 5,
}

PAYMENT_RULES = {
    "payment appears to be requested before": 20,
    "specific payment amount": 15,
    "payment mentioned": 8,
}

BEHAVIOR_RULES = {
    "urgency_terms": 15,
    "manipulation_terms": 20,
}


# ---------- HELPERS ----------

def _normalize(text: str) -> str:
    return text.lower().strip()


# ---------- COMPANY ----------

def score_company(result: Dict[str, Any]) -> Tuple[int, List[str]]:
    score = 0
    reasons = []

    for obs in result.get("observations", []):
        obs_norm = _normalize(obs)
        for rule, points in COMPANY_RULES.items():
            if rule in obs_norm:
                score += points
                reasons.append(f"{rule} (+{points})")

    return min(score, AGENT_MAX_SCORES["company"]), reasons


# ---------- PAYMENT ----------

def score_payment(result: Dict[str, Any]) -> Tuple[int, List[str]]:
    score = 0
    reasons = []

    for obs in result.get("observations", []):
        obs_norm = _normalize(obs)
        for rule, points in PAYMENT_RULES.items():
            if rule in obs_norm:
                score += points
                reasons.append(f"{rule} (+{points})")

    return min(score, AGENT_MAX_SCORES["payment"]), reasons


# ---------- BEHAVIOR ----------

def score_behavior(result: Dict[str, Any]) -> Tuple[int, List[str]]:
    score = 0
    reasons = []

    if result.get("urgency_terms"):
        score += BEHAVIOR_RULES["urgency_terms"]
        reasons.append("urgency language detected")

    if result.get("manipulation_terms"):
        score += BEHAVIOR_RULES["manipulation_terms"]
        reasons.append("manipulative phrasing detected")

    # Infer missing process from observation text
    obs_text = " ".join(result.get("observations", [])).lower()
    if "no clear interview" in obs_text:
        score += 10
        reasons.append("no interview or selection process mentioned")

    return min(score, AGENT_MAX_SCORES["behavior"]), reasons


# ---------- ML ----------

def score_ml(ml_result: Dict[str, Any]) -> Tuple[int, List[str]]:
    if not ml_result or not ml_result.get("ml_used"):
        return 0, ["ML analysis not performed"]

    risk_level = ml_result.get("risk_level", "low")
    probability = ml_result.get("risk_probability", 0.0)

    base_scores = {"low": 5, "medium": 12, "high": 20}
    base = base_scores.get(risk_level, 0)

    confidence = abs(probability - 0.5) * 2  # 0–1
    raw_score = base * confidence

    # Ignore weak ML noise
    if raw_score < 3:
        return 0, ["ML signal too weak to influence score"]

    score = min(int(round(raw_score)), AGENT_MAX_SCORES["ml"])

    return score, [
        f"ML language patterns indicate {risk_level} risk "
        f"(confidence={round(confidence, 2)}) (+{score})"
    ]


# ---------- CATEGORY ----------

def get_risk_category(score: int) -> str:
    for threshold, label in RISK_CATEGORIES:
        if score < threshold:
            return label
    return RISK_CATEGORIES[-1][1]


# ---------- MAIN ENGINE ----------

def calculate_risk(agent_results: Dict[str, Any]) -> Dict[str, Any]:
    breakdown: Dict[str, int] = {}
    details: Dict[str, List[str]] = {}
    total = 0

    for agent, scorer in [
        ("company", score_company),
        ("payment", score_payment),
        ("behavior", score_behavior),
        ("ml", score_ml),
    ]:
        if agent in agent_results:
            s, d = scorer(agent_results[agent])
        else:
            s, d = 0, ["not analyzed"]

        breakdown[agent] = s
        details[agent] = d
        total += s

    # ---------- COMPOUND RISK ESCALATION ----------
    strong_signals = 0

    if breakdown.get("payment", 0) >= 15:
        strong_signals += 1

    if breakdown.get("behavior", 0) >= 20:
        strong_signals += 1

    if breakdown.get("ml", 0) >= 10:
        strong_signals += 1

    if strong_signals >= 2:
        total += 15  # escalation bonus

    total = min(total, 100)

    return {
        "risk_score": total,
        "risk_category": get_risk_category(total),
        "breakdown": breakdown,
        "details": details,
    }
