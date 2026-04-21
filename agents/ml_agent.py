"""ML analysis agent with robust fallback model lifecycle."""

from __future__ import annotations

import os
import pickle
from itertools import product
from typing import Dict, List, Tuple

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression

    SKLEARN_AVAILABLE = True
except Exception:
    TfidfVectorizer = object  # type: ignore[assignment]
    LogisticRegression = object  # type: ignore[assignment]
    SKLEARN_AVAILABLE = False

MODEL_PATH = "ml/model.pkl"
VECTORIZER_PATH = "ml/vectorizer.pkl"
MIN_TEXT_LENGTH = 10


def _build_training_data() -> Tuple[List[str], List[int]]:
    """Build synthetic scam/safe dataset for bootstrap model training."""
    scam_openers = [
        "limited seats internship",
        "urgent internship hiring",
        "work from home internship",
        "telegram internship message",
        "whatsapp internship offer",
        "gmail recruiter outreach",
        "no interview internship offer",
        "unknown startup internship",
        "crypto internship program",
        "task job internship",
        "campus ambassador internship",
        "review job internship",
        "certificate based internship",
        "remote joining internship",
    ]
    scam_actions = [
        "pay registration fee now",
        "send security deposit immediately",
        "pay onboarding fee via upi",
        "scan qr code to confirm slot",
        "share aadhaar pan passport now",
        "send bank account and ifsc today",
        "provide otp to verify profile",
        "download suspicious pdf attachment",
        "click urgent phishing portal link",
        "confirm seat now or lose offer",
        "pay for internship certificate",
        "join telegram hr for payment",
        "whatsapp only communication accepted",
        "resume shortlisting after payment",
    ]
    scam_tails = [
        "salary 90000 per month for freshers",
        "offer letter from non company domain",
        "urgent immediate joining no discussion",
        "limited seats close in 15 minutes",
        "only today payment accepted",
        "no official interview required",
        "fake internship portal asks deposit",
        "fake linkedin recruiter pushes urgency",
        "training mandatory after payment",
        "unknown attachment contains offer",
    ]

    safe_openers = [
        "official internship opportunity",
        "verified company internship opening",
        "campus internship recruitment",
        "software internship posting",
        "data science internship role",
        "product internship position",
        "research internship call",
        "engineering internship application",
        "design internship role",
        "operations internship listing",
        "finance internship opportunity",
        "marketing internship role",
    ]
    safe_actions = [
        "apply through company careers page",
        "complete interview and assessment rounds",
        "communicate with official domain hr",
        "review signed offer letter from company",
        "no registration fee required ever",
        "stipend discussed after interview",
        "office location and mentor details shared",
        "background verified by placement cell",
        "offer follows standard policy and terms",
        "candidate can verify role on linkedin page",
        "documents requested only after onboarding",
        "privacy and data handling policy shared",
    ]
    safe_tails = [
        "no payment or deposit at any stage",
        "company email domain used consistently",
        "clear internship timeline and responsibilities",
        "official interview panel confirmation",
        "transparent stipend and joining process",
        "formal communication and documented process",
        "internship certificate only after completion",
        "recruiter profile matches official company",
        "all details available on company website",
        "candidate can ask questions before accepting",
    ]

    scam_samples = [f"{a} {b} {c}" for a, b, c in product(scam_openers, scam_actions, scam_tails)][:220]
    safe_samples = [f"{a} {b} {c}" for a, b, c in product(safe_openers, safe_actions, safe_tails)][:220]
    labels = [1] * len(scam_samples) + [0] * len(safe_samples)
    return scam_samples + safe_samples, labels


def _train_default_model() -> Tuple[LogisticRegression, TfidfVectorizer]:
    """Train and persist a default TF-IDF + LogisticRegression model."""
    if not SKLEARN_AVAILABLE:
        raise RuntimeError("scikit-learn is not installed")
    data, labels = _build_training_data()
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_df=0.95, sublinear_tf=True)
    features = vectorizer.fit_transform(data)
    model = LogisticRegression(max_iter=1200, solver="liblinear", random_state=42)
    model.fit(features, labels)
    os.makedirs("ml", exist_ok=True)
    with open(VECTORIZER_PATH, "wb") as vec_file:
        pickle.dump(vectorizer, vec_file)
    with open(MODEL_PATH, "wb") as model_file:
        pickle.dump(model, model_file)
    return model, vectorizer


def _load_or_train() -> Tuple[LogisticRegression, TfidfVectorizer, bool]:
    """Load persisted model assets or retrain if unavailable/corrupt."""
    if not SKLEARN_AVAILABLE:
        raise RuntimeError("scikit-learn is not installed")
    if not (os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH)):
        model, vectorizer = _train_default_model()
        return model, vectorizer, True

    try:
        with open(MODEL_PATH, "rb") as model_file:
            model = pickle.load(model_file)
        with open(VECTORIZER_PATH, "rb") as vec_file:
            vectorizer = pickle.load(vec_file)
        if not getattr(vectorizer, "vocabulary_", None):
            model, vectorizer = _train_default_model()
            return model, vectorizer, True
        return model, vectorizer, False
    except Exception:
        model, vectorizer = _train_default_model()
        return model, vectorizer, True


def run_ml_analysis(intake: Dict[str, str]) -> Dict[str, object]:
    """Run resilient ML inference and return fallback-safe risk metadata."""
    text = ((intake or {}).get("clean_text", "") or "").strip()
    if len(text) < MIN_TEXT_LENGTH:
        return {"ml_used": False, "reason": "Input too short for ML scoring"}
    if not SKLEARN_AVAILABLE:
        return {"ml_used": False, "error": "scikit-learn not available"}

    try:
        model, vectorizer, retrained = _load_or_train()
    except Exception as exc:
        return {"ml_used": False, "error": f"Model bootstrap failed: {exc}"}

    try:
        features = vectorizer.transform([text])
    except Exception:
        try:
            model, vectorizer = _train_default_model()
            retrained = True
            features = vectorizer.transform([text])
        except Exception as exc:
            return {"ml_used": False, "error": f"Vectorizer transform failed: {exc}"}

    try:
        probability = float(model.predict_proba(features)[0][1])
    except Exception:
        try:
            model, vectorizer = _train_default_model()
            retrained = True
            features = vectorizer.transform([text])
            probability = float(model.predict_proba(features)[0][1])
    except Exception as exc:
        return {
            "ml_used": False,
            "error": f"Model prediction failed: {exc}",
            "fallback": "Rule-based detection only",
        }

    risk_percent = max(0, min(100, int(round(probability * 100))))
    return {
        "ml_used": True,
        "retrained": retrained,
        "risk_probability": round(probability, 4),
        "risk_percent": risk_percent,
        "model_type": "TF-IDF + LogisticRegression",
    }