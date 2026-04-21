"""
Behavior agent (rule-based).

NO LLM
NO CrewAI
"""

from database.pattern_repository import record_pattern
import re

URGENCY_WORDS = [
    # Time pressure - basic
    "urgent", "immediately", "asap", "hurry", "rush",
    "quick", "quickly", "fast", "instant", "instantly",
    
    # Deadline pressure
    "limited time", "limited slots", "limited offer",
    "last chance", "final call", "deadline", "expires",
    "closing soon", "ending soon", "only today", "today only",
    "last day", "final day", "few hours left", "few days left",
    
    # Scarcity tactics
    "only 2 left", "only 5 left", "only few left",
    "slots filling fast", "almost full", "running out",
    "limited seats", "limited vacancies", "few slots",
    
    # Action pressure
    "apply now", "join now", "register now", "pay now",
    "act now", "call now", "message now", "reply now",
    "don't miss", "don't wait", "don't delay",
    
    # FOMO (Fear of missing out)
    "miss this opportunity", "once in lifetime",
    "rare opportunity", "golden chance", "won't get again",
    "grab now", "seize now", "before it's gone",
    
    # Countdown language
    "24 hours", "48 hours", "within hours",
    "before midnight", "by tonight", "by today",
    "in next few hours", "time running out",
    
    # Immediate response demanded
    "respond immediately", "reply asap", "immediate response",
    "urgent response required", "time sensitive",
    
    # Expanded Synonyms (New)
    "right away", "at once", "straight away", "promptly", 
    "without delay", "forthwith", "on the spot", "in a flash", 
    "instanter", "urgently", "posthaste", "immediately",
    "without hesitation", "instantaneously", "directly",
    "speedily", "rapidly", "swiftly"
]

MANIPULATION_PHRASES = [
    # Guaranteed outcomes
    "guaranteed placement", "100% placement",
    "guaranteed job", "guaranteed success",
    "guaranteed selection", "confirmed selection",
    "guaranteed salary", "guaranteed stipend",
    
    # No effort required
    "no interview required", "no interview needed",
    "no test required", "no exam needed",
    "no experience required", "no skills needed",
    "no qualification needed", "no degree required",
    
    # Instant/automatic selection
    "instant selection", "automatic selection",
    "direct selection", "pre-selected", "already selected",
    "you are selected", "you won", "you qualified",
    "congratulations selected", "auto-selected",
    
    # Too easy claims
    "easy money", "quick money", "fast money",
    "easy job", "simple work", "no work",
    "effortless", "sit at home and earn",
    
    # Unrealistic promises
    "become rich", "get rich quick", "millionaire",
    "unlimited earning", "unlimited income",
    "earn lakhs", "earn crores", "huge salary",
    
    # Exclusive/special treatment
    "special offer for you", "you have been chosen",
    "selected from thousands", "hand-picked",
    "exclusive opportunity", "vip offer",
    
    # No risk/all gain
    "risk-free", "no risk", "100% safe",
    "money back guarantee", "full refund",
    "cannot lose", "only profit",
    
    # Direct joining claims
    "direct joining", "join immediately",
    "start tomorrow", "start today",
    "no waiting period", "instant start",
    
    # Celebrity/authority false association
    "recommended by", "approved by government",
    "certified by", "authorized by",
    "official partner", "exclusive tie-up"
]



def run_behavior_agent(intake: dict) -> dict:
    text = intake.get("clean_text", "").lower()

    # Create regex patterns for efficient matching with boundaries
    urgency_pattern = r'\b(?:' + '|'.join(map(re.escape, URGENCY_WORDS)) + r')\b'
    manipulation_pattern = r'\b(?:' + '|'.join(map(re.escape, MANIPULATION_PHRASES)) + r')\b'

    urgency = re.findall(urgency_pattern, text)
    manipulation = re.findall(manipulation_pattern, text)

    # Remove duplicates
    urgency = list(set(urgency))
    manipulation = list(set(manipulation))

    # LLM INTEGRATION: Trust the intake parser if it found urgency
    if not urgency and intake.get("urgency_mentions"):
        urgency.append("Generic urgency (LLM verified)")
        record_pattern("behavior", "urgency_flag_llm")

    if urgency:
        record_pattern("behavior", "urgency_language")

    if manipulation:
        record_pattern("behavior", "manipulation_phrases")

    observations = []

    if urgency:
        observations.append(f"Urgency language detected ({len(urgency)} terms found)")
    if manipulation:
        observations.append(f"Manipulative phrases detected ({len(manipulation)} terms found)")

    if not observations:
        observations.append("No behavioral concerns detected")

    return {
        "urgency_terms": urgency,
        "manipulation_terms": manipulation,
        "observations": observations
    }
