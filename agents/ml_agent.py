"""
ML agent for SAFE-INTERN.

NO training
NO LLM
"""

import os
import pickle
from database.pattern_repository import record_pattern

MODEL_PATH = "ml/model.pkl"
VECTORIZER_PATH = "ml/vectorizer.pkl"
MIN_TEXT_LENGTH = 20


def run_ml_analysis(intake: dict) -> dict:
    text = intake.get("clean_text", "")

    if not text or len(text.strip()) < MIN_TEXT_LENGTH:
        return {"ml_used": False}

    if not (os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH)):
        return {"ml_used": False}

    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    with open(VECTORIZER_PATH, "rb") as f:
        vectorizer = pickle.load(f)

    vec = vectorizer.transform([text])
    prob = model.predict_proba(vec)[0][1]

    if prob < 0.3:
        level = "low"
    elif prob < 0.6:
        level = "medium"
    else:
        level = "high"

    record_pattern("ml", level)

    return {
        "ml_used": True,
        "risk_probability": round(float(prob), 3),
        "risk_level": level
    }
