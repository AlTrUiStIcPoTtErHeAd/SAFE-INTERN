"""
Explanation engine for SAFE-INTERN.

Responsibilities:
- Convert risk score and agent breakdown into user-friendly explanations
- Use advisory, non-accusatory language
- Explain why caution may or may not be needed
- Provide clear, confidence-aligned messaging

NO accusations
NO legal conclusions
NO absolute claims
"""

from typing import Dict, Any, List


# ---------- DISCLAIMER ----------

DISCLAIMER = (
    "This assessment is advisory and based on observable patterns only. "
    "It does not confirm wrongdoing and should be used alongside independent verification."
)


# ---------- COMPANY ----------

def explain_company(details: List[str]) -> List[str]:
    explanations = []

    for d in details:
        d = d.lower()

        if "not reachable" in d:
            explanations.append(
                "The company website could not be reached, which may limit independent verification."
            )
        elif "does not use https" in d:
            explanations.append(
                "The company website does not use HTTPS, which is less common for established organizations."
            )
        elif "free email domain" in d:
            explanations.append(
                "Communication uses a free email domain instead of an official company domain."
            )
        elif "does not match website domain" in d:
            explanations.append(
                "The email domain does not match the company website domain."
            )

    if not explanations:
        return []

    return explanations


# ---------- PAYMENT ----------

def explain_payment(details: List[str]) -> List[str]:
    explanations = []

    for d in details:
        d = d.lower()

        if "requested before" in d:
            explanations.append(
                "Payment is requested before the internship begins, which is uncommon and should be verified carefully."
            )
        elif "specific payment amount" in d:
            explanations.append(
                "A specific payment amount is mentioned in the communication."
            )
        elif "payment mentioned" in d:
            explanations.append(
                "Payment-related language appears in the communication."
            )

    return explanations


# ---------- BEHAVIOR ----------

def explain_behavior(details: List[str]) -> List[str]:
    explanations = []

    for d in details:
        d = d.lower()

        if "urgency" in d:
            explanations.append(
                "Urgency-focused language is used, which may encourage rushed decisions."
            )
        elif "manipulation" in d:
            explanations.append(
                "Certain phrases suggest guaranteed outcomes or simplified processes."
            )
        elif "no clear interview" in d:
            explanations.append(
                "No clear interview or selection process is mentioned."
            )

    return explanations


# ---------- ML (CRITICAL FIX) ----------

def explain_ml(details: List[str], ml_score: int) -> List[str]:
    """
    ML explanations MUST depend on ML score strength.
    This prevents scary language when ML impact is negligible.
    """

    # 🔑 Key fix: very low ML contribution
    if ml_score <= 2:
        return []

    explanations = []

    for d in details:
        d = d.lower()

        if "low" in d:
            explanations.append(
                "Language patterns are consistent with lower-risk internship communications."
            )
        elif "medium" in d:
            explanations.append(
                "Some language patterns warrant mild caution and may benefit from verification."
            )
        elif "high" in d:
            explanations.append(
                "Language shows multiple patterns commonly associated with higher-risk internship messages."
            )

    return explanations


# ---------- RECOMMENDATIONS ----------

def generate_recommendations(risk_category: str, risk_score: int, findings: List[str]) -> List[str]:
    recs = []
    
    # 1. Verification Advice
    recs.append("Verify the company's official website and career page.")
    recs.append("Check if the email domain matches the official company domain.")
    
    # 2. Risk-Based Advice
    if risk_score > 60:
        recs.append("Do NOT pay any money. Legitimate internships do not ask for registration fees.")
        recs.append("Be skeptical of 'instant offer' or 'no interview' claims.")
        recs.append("Search for the company name + 'scam' or 'review' online.")
    elif risk_score > 30:
        recs.append("Proceed with caution. Request a formal offer letter and verify details.")
        recs.append("If asked for money (even for 'training'), stop and verify.")
    
    # 3. Specific Findings Advice
    payment_flag = any("payment" in f.lower() for f in findings)
    urgent_flag = any("urgency" in f.lower() for f in findings)
    
    if payment_flag:
        recs.append("Ignore requests for 'security deposit', 'id card fee', or 'laptop charges'.")
    
    if urgent_flag:
        recs.append("Don't feel pressured by deadlines. Take time to research.")

    return list(set(recs)) # Remove duplicates


# ---------- SUMMARY ----------

def generate_summary(risk_category: str, risk_score: int) -> str:
    if risk_score <= 5:
        return (
            f"This internship communication shows no meaningful risk indicators "
            f"(risk score: {risk_score}/100). Standard verification is recommended."
        )

    if risk_category == "Low Risk Indicators":
        return (
            f"This internship communication shows relatively few concerning patterns "
            f"(risk score: {risk_score}/100). Independent verification is recommended."
        )
    elif risk_category == "Caution Advised":
        return (
            f"This internship communication shows some concerning patterns "
            f"(risk score: {risk_score}/100). Proceed with caution and verify details carefully."
        )
    else:
        return (
            f"This internship communication shows multiple concerning patterns "
            f"(risk score: {risk_score}/100). Extra caution and thorough verification are strongly advised."
        )


# ---------- MAIN ENGINE ----------

def generate_explanation(risk_result: Dict[str, Any]) -> Dict[str, Any]:
    details = risk_result.get("details", {})
    breakdown = risk_result.get("breakdown", {})

    risk_category = risk_result.get("risk_category", "Unknown")
    risk_score = risk_result.get("risk_score", 0)
    ml_score = breakdown.get("ml", 0)

    explanations: List[str] = []
    explanations.extend(explain_company(details.get("company", [])))
    explanations.extend(explain_payment(details.get("payment", [])))
    explanations.extend(explain_behavior(details.get("behavior", [])))
    explanations.extend(explain_ml(details.get("ml", []), ml_score))
    
    recommendations = generate_recommendations(risk_category, risk_score, explanations)

    return {
        "risk_category": risk_category,
        "risk_score": risk_score,
        "summary": generate_summary(risk_category, risk_score),
        "explanations": explanations,
        "recommendations": recommendations,
        "breakdown": breakdown,
        "disclaimer": DISCLAIMER
    }
