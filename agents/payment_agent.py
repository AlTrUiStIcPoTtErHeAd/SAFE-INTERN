"""
Payment agent (rule-based).

NO LLM
NO CrewAI
"""

import re
from database.pattern_repository import record_pattern

PAYMENT_KEYWORDS = [
    # Basic payment terms
    "fee", "payment", "deposit", "registration",
    "joining fee", "processing fee", "charges",
    
    # Registration & admin fees
    "registration fee", "enrollment fee", "application fee",
    "processing charges", "administrative fee", "handling charges",
    "documentation fee", "verification fee", "background check fee",
    
    # Training & materials
    "training fee", "course fee", "material fee", "kit fee",
    "certification fee", "exam fee", "study material cost",
    "training charges", "learning material fee",
    
    # Security & refundable deposits
    "security deposit", "refundable deposit", "caution deposit",
    "security money", "guarantee deposit", "bond amount",
    
    # Equipment & infrastructure
    "laptop fee", "equipment fee", "software fee",
    "infrastructure charges", "setup fee", "installation charges",
    
    # ID & documentation
    "id card fee", "identity card charges", "badge fee",
    "uniform fee", "dress code charges",
    
    # Miscellaneous fees
    "onboarding fee", "orientation fee", "induction charges",
    "profile fee", "resume fee", "subscription fee",
    "membership fee", "access fee", "activation fee",
    "renewal fee", "maintenance fee", "service charges",
    
    # Indirect payment mentions
    "pay for", "cost of", "price of", "amount for",
    "invest in", "investment required", "contribution",
    "advance payment", "token amount", "booking amount"
]

UPFRONT_KEYWORDS = [
       # Direct demands
    "pay first", "before joining", "upfront",
    "immediate payment", "pay now", "pay immediately",
    
    # Time pressure
    "pay today", "pay within", "deadline to pay",
    "payment before", "advance payment required",
    "pay in advance", "prepayment", "pre-payment",
    
    # Urgent payment language
    "urgent payment", "pay asap", "pay right now",
    "instant payment", "immediate transfer", "quick payment",
    
    # Expanded Synonyms (New)
    "pay forthwith", "transfer straight away", "deposit at once",
    "remit immediately", "wire instantly", "settle now",
    "pay without delay", "transfer posthaste", "deposit directly",
    # Before conditions
    "before interview", "before selection", "before offer",
    "before starting", "before onboarding", "before confirmation",
    "prior to joining", "prior to selection",
    
    # Account/transfer mentions
    "transfer now", "send money", "transfer amount",
    "deposit now", "deposit immediately", "make payment",
    "complete payment", "submit payment", "process payment",
    
    # Conditional payment
    "pay to confirm", "pay to secure", "pay to book",
    "payment for confirmation", "payment to proceed",
    "payment required to", "must pay before",
    
    # Digital payment urgency
    "send via upi", "paytm now", "phonepe immediately",
    "google pay now", "transfer via", "send to account",
    
    # Deadline pressure
    "payment due", "pay by", "payment within 24 hours",
    "last date to pay", "payment deadline", "final date",
    
    # First payment emphasis
    "first payment", "initial payment", "opening payment",
    "starting payment", "one-time payment", "one time fee"
]


def run_payment_agent(intake: dict) -> dict:
    text = intake.get("clean_text", "").lower()
    observations = []

    # Create regex patterns for efficient matching with boundaries
    # Use word boundary OR non-word character lookahead/behind for symbols
    payment_pattern = r'(?:\b|(?<=\s))(' + '|'.join(map(re.escape, PAYMENT_KEYWORDS)) + r')(?:\b|(?=\s))'
    upfront_pattern = r'(?:\b|(?<=\s))(' + '|'.join(map(re.escape, UPFRONT_KEYWORDS)) + r')(?:\b|(?=\s))'

    payment_matches = re.findall(payment_pattern, text, flags=re.IGNORECASE)
    upfront_matches = re.findall(upfront_pattern, text, flags=re.IGNORECASE)

    if payment_matches:
        observations.append(f"Payment mentioned ({len(set(payment_matches))} terms)")

    if upfront_matches:
        observations.append(f"Payment appears to be requested before joining ({len(set(upfront_matches))} terms)")

    # LLM INTEGRATION: Trust the intake parser if it found payment requirements
    if not payment_matches and (intake.get("payment_required") or intake.get("payment_mentions")):
        observations.append("Payment mentioned (LLM verified)")
        record_pattern("payment", "payment_flag_llm")

    if re.search(r"(₹|rs\.?|inr|\$)\s?\d+", text):
        observations.append("Specific payment amount mentioned")

    for obs in observations:
        record_pattern("payment", obs.lower())

    if not observations:
        observations.append("No payment risk patterns detected")

    return {"observations": observations}
