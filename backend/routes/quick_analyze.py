import os
import sys
import joblib
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
import numpy as np

# Use project root as base directory (cwd when server is started)
BASE_DIR = Path.cwd()

# Paths to model and vectorizer
MODEL_PATH = BASE_DIR / "ml" / "model.pkl"
VECTORIZER_PATH = BASE_DIR / "ml" / "vectorizer.pkl"

# Load model and vectorizer once at startup
logger = logging.getLogger("sentivision.quick_analyze")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

try:
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    logger.info(f"Loaded model from: {MODEL_PATH}")
    logger.info(f"Loaded vectorizer from: {VECTORIZER_PATH}")
except Exception as exc:
    logger.error(f"Failed to load model or vectorizer: {exc}")
    raise RuntimeError("Model loading failed, cannot start API.") from exc

# Import shared preprocessing (clean_text) – same as training pipeline
sys.path.insert(0, str(BASE_DIR / "ml"))
from preprocess import clean_text

# Sentiment label mapping – model uses 0=Negative,1=Neutral,2=Positive
LABELS = ["Negative", "Neutral", "Positive"]
CONFIDENCE_THRESHOLD = 60.0  # percent

router = APIRouter(tags=["quick-analyze"])

def _softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

@router.post("/analyze")
def analyze(payload: dict):
    """Return sentiment, confidence and per‑class probabilities for input text.

    Expected JSON: {"input_text": "..."}
    """
    text = payload.get("input_text")
    if not isinstance(text, str) or not text.strip():
        raise HTTPException(status_code=400, detail="`input_text` must be a non‑empty string.")

    # Preprocess using the shared pipeline
    cleaned = clean_text(text)
    if not cleaned:
        # Fallback to neutral when preprocessing removes everything
        return {
            "sentiment": "Neutral",
            "confidence": 0.0,
            "probabilities": {"negative": 33.33, "neutral": 33.34, "positive": 33.33},
        }

    X = vectorizer.transform([cleaned])

    # Obtain raw scores – prefer predict_proba, fallback to decision_function + softmax
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X)[0]
    elif hasattr(model, "decision_function"):
        scores = model.decision_function(X)
        # Ensure scores is 1‑D array
        if scores.ndim > 1:
            scores = scores.ravel()
        probs = _softmax(scores)
    else:
        raise HTTPException(status_code=500, detail="Model does not support probability output.")

    # Map to label order (ensure length 3)
    if probs.shape[0] != 3:
        # Align using model.classes_ if present
        if hasattr(model, "classes_"):
            ordered = np.zeros(3)
            for idx, cls in enumerate(model.classes_):
                ordered[int(cls)] = probs[idx]
            probs = ordered
        else:
            # Pad/truncate safely
            probs = np.pad(probs, (0, 3 - probs.shape[0]), "constant")

    # Convert to percentages
    probs = probs * 100
    neg, neu, pos = probs[0], probs[1], probs[2]
    # Determine predicted class and confidence
    max_conf = probs.max()
    pred_idx = int(np.argmax(probs))
    sentiment = LABELS[pred_idx]
    is_uncertain = max_conf < CONFIDENCE_THRESHOLD
    if is_uncertain:
        sentiment = "Neutral/Uncertain"

    return {
        "sentiment": sentiment,
        "confidence": round(float(max_conf), 2),
        "probabilities": {
            "negative": round(float(neg), 2),
            "neutral": round(float(neu), 2),
            "positive": round(float(pos), 2),
        },
    }
