# Central configuration for SAFE-INTERN

# ---------- RISK SCORE LIMITS ----------
TOTAL_MAX_SCORE = 100
RULE_BASED_MAX_SCORE = 80
ML_MAX_SCORE = 20

# ---------- RISK CATEGORY THRESHOLDS ----------
LOW_RISK_THRESHOLD = 30
CAUTION_RISK_THRESHOLD = 60
HIGH_RISK_THRESHOLD = 100

RISK_LABELS = {
    "low": "Low Risk Indicators",
    "medium": "Caution Advised",
    "high": "High Risk Indicators"
}

# ---------- AGENT SCORE CAPS ----------
COMPANY_AGENT_MAX_SCORE = 40
PAYMENT_AGENT_MAX_SCORE = 30
BEHAVIOR_AGENT_MAX_SCORE = 30

# ---------- ML SETTINGS ----------
ML_SCORE_SCALING = 20  # Used only if probability-based ML scoring is enabled
ML_MODEL_PATH = "ml/model.pkl"
ML_VECTORIZER_PATH = "ml/vectorizer.pkl"

# ---------- DATABASE ----------
DATABASE_PATH = "database/safe_intern.db"

# ---------- LLM SETTINGS (GOOGLE GEMINI) ----------
LLM_ENABLED = True
LLM_PROVIDER = "gemini"
LLM_MODEL_NAME = "gemini-2.0-flash"
LLM_TEMPERATURE = 0.0
LLM_MAX_TOKENS = 1024
LLM_TIMEOUT = 15
LLM_JSON_ONLY = True

# ---------- GENERAL ----------
DEFAULT_LANGUAGE = "en"
WEB_REQUEST_TIMEOUT = 5
