"""
SentiVision AI — Prediction Module
True 3-class sentiment prediction: Negative (0) / Neutral (1) / Positive (2)
Includes confidence thresholding and XAI keyword extraction.
"""

import os
import sys
import json
import joblib
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from preprocess import clean_text

# ─── Paths ─────────────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), 'vectorizer.pkl')
METADATA_PATH = os.path.join(os.path.dirname(__file__), 'model_metadata.json')

# ─── Global cache ──────────────────────────────────────────────────
_model = None
_vectorizer = None
_metadata = None

# ─── Label mapping ─────────────────────────────────────────────────
# Model classes: 0 = Negative, 1 = Neutral, 2 = Positive
LABEL_MAP = {0: 'Negative', 1: 'Neutral', 2: 'Positive'}
CONFIDENCE_THRESHOLD = 60.0  # Below this → "Neutral/Uncertain"


def load_model():
    """Load model, vectorizer, and metadata. Cached after first load."""
    global _model, _vectorizer, _metadata

    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. Run 'python ml/train.py' first."
            )
        _model = joblib.load(MODEL_PATH)
        print(f"  * Model loaded from {MODEL_PATH}")

    if _vectorizer is None:
        if not os.path.exists(VECTORIZER_PATH):
            raise FileNotFoundError(
                f"Vectorizer not found at {VECTORIZER_PATH}. Run 'python ml/train.py' first."
            )
        _vectorizer = joblib.load(VECTORIZER_PATH)
        print(f"  * Vectorizer loaded from {VECTORIZER_PATH}")

    if _metadata is None and os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, 'r') as f:
            _metadata = json.load(f)

    return _model, _vectorizer


def reload_model():
    """Force-reload model from disk (used after retraining)."""
    global _model, _vectorizer, _metadata
    _model = None
    _vectorizer = None
    _metadata = None
    return load_model()


def get_model_metadata() -> dict:
    """Return current model metadata."""
    if _metadata is None and os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, 'r') as f:
            return json.load(f)
    return _metadata or {}


def _get_class_index(model, class_id: int):
    """Find the index of a class in model.classes_ array."""
    if hasattr(model, 'classes_'):
        classes = list(model.classes_)
        if class_id in classes:
            return classes.index(class_id)
    return class_id


def predict_sentiment(text: str) -> dict:
    """
    Predict sentiment for a single text (3-class: Positive/Neutral/Negative).

    Rules:
    - Max probability class is chosen
    - If max confidence < 60% → label becomes "Neutral/Uncertain"
    - Returns probabilities for all 3 classes

    Returns:
        dict with keys: text, cleaned_text, sentiment, confidence,
                        probabilities {positive, neutral, negative},
                        key_words {positive, neutral, negative},
                        is_uncertain
    """
    model, vectorizer = load_model()

    cleaned = clean_text(text)

    if not cleaned.strip():
        return {
            'text': text,
            'cleaned_text': '',
            'sentiment': 'Neutral',
            'confidence': 0.0,
            'probabilities': {'positive': 33.33, 'neutral': 33.34, 'negative': 33.33},
            'key_words': {'positive': [], 'neutral': [], 'negative': []},
            'is_uncertain': True,
        }

    # Vectorize
    features = vectorizer.transform([cleaned])

    # Get probabilities for all 3 classes
    if hasattr(model, 'predict_proba'):
        proba_raw = model.predict_proba(features)[0]
    else:
        proba_raw = np.array([0.33, 0.34, 0.33])

    # Map probabilities to labels based on model.classes_
    proba_map = {}
    if hasattr(model, 'classes_'):
        for i, cls in enumerate(model.classes_):
            proba_map[int(cls)] = float(proba_raw[i]) if i < len(proba_raw) else 0.0
    else:
        # Fallback: assume classes are [0, 1, 2]
        for i in range(3):
            proba_map[i] = float(proba_raw[i]) if i < len(proba_raw) else 0.0

    neg_prob = proba_map.get(0, 0.0) * 100
    neu_prob = proba_map.get(1, 0.0) * 100
    pos_prob = proba_map.get(2, 0.0) * 100

    # Normalize
    total = pos_prob + neu_prob + neg_prob
    if total > 0:
        pos_prob = pos_prob / total * 100
        neu_prob = neu_prob / total * 100
        neg_prob = neg_prob / total * 100

    # Find predicted class
    predicted_class = int(np.argmax([neg_prob, neu_prob, pos_prob]))
    # Map index back: 0→Negative, 1→Neutral, 2→Positive
    class_labels = ['Negative', 'Neutral', 'Positive']
    predicted_label = class_labels[predicted_class]
    confidence = max(neg_prob, neu_prob, pos_prob)

    # Apply confidence threshold
    is_uncertain = confidence < CONFIDENCE_THRESHOLD
    if is_uncertain:
        sentiment = 'Neutral/Uncertain'
    else:
        sentiment = predicted_label

    # XAI: extract influential words per class
    key_words = get_key_words(cleaned, features, model, vectorizer)

    return {
        'text': text,
        'cleaned_text': cleaned,
        'sentiment': sentiment,
        'confidence': round(confidence, 2),
        'probabilities': {
            'positive': round(pos_prob, 2),
            'neutral': round(neu_prob, 2),
            'negative': round(neg_prob, 2),
        },
        'key_words': key_words,
        'is_uncertain': is_uncertain,
    }


def predict_batch(texts: list) -> list:
    """Predict sentiment for a list of texts."""
    return [predict_sentiment(t) for t in texts]


def get_key_words(cleaned_text: str, features, model, vectorizer, top_n: int = 6) -> dict:
    """
    Extract most influential words for each sentiment class using model coefficients.

    For multiclass models (OvR LogReg, SVM):
    - coef_ shape is (n_classes, n_features)
    - coef_[0] = Negative, coef_[1] = Neutral, coef_[2] = Positive

    Returns:
        dict: {'positive': [...], 'neutral': [...], 'negative': [...]}
    """
    feature_names = vectorizer.get_feature_names_out()
    positive_words = []
    neutral_words = []
    negative_words = []

    try:
        # Get coefficients
        coef = None
        if hasattr(model, 'coef_'):
            coef = model.coef_
        elif hasattr(model, 'calibrated_classifiers_'):
            base = model.calibrated_classifiers_[0].estimator
            if hasattr(base, 'coef_'):
                coef = base.coef_

        if coef is None:
            # RandomForest: use feature_importances_
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                non_zero = features.nonzero()[1]
                scored = [(feature_names[i], importances[i]) for i in non_zero]
                scored.sort(key=lambda x: x[1], reverse=True)
                positive_words = [w for w, _ in scored[:top_n]]
                negative_words = [w for w, _ in scored[top_n:top_n * 2]]
            return {'positive': positive_words, 'neutral': neutral_words, 'negative': negative_words}

        # coef_ shape: (n_classes, n_features) for multinomial
        non_zero_indices = features.nonzero()[1]
        if len(non_zero_indices) == 0:
            return {'positive': [], 'neutral': [], 'negative': []}

        # Ensure coef is 2D with 3 rows
        if coef.ndim == 1:
            # Binary classifier — treat as pos vs neg
            scored_pos = []
            scored_neg = []
            for idx in non_zero_indices:
                word = feature_names[idx]
                score = coef[idx] * features[0, idx]
                if score > 0:
                    scored_pos.append((word, abs(score)))
                else:
                    scored_neg.append((word, abs(score)))
            scored_pos.sort(key=lambda x: x[1], reverse=True)
            scored_neg.sort(key=lambda x: x[1], reverse=True)
            positive_words = [w for w, _ in scored_pos[:top_n]]
            negative_words = [w for w, _ in scored_neg[:top_n]]
            return {'positive': positive_words, 'neutral': neutral_words, 'negative': negative_words}

        # True 3-class (n_classes >= 2)
        # For multinomial: coef[class_idx, feature_idx]
        # class 0 = Negative, 1 = Neutral, 2 = Positive
        n_classes = coef.shape[0]

        # Get class indices from model.classes_
        classes = list(model.classes_) if hasattr(model, 'classes_') else [0, 1, 2]

        def get_class_coef(class_id):
            if class_id in classes:
                idx = classes.index(class_id)
                if idx < n_classes:
                    return coef[idx]
            return None

        coef_neg = get_class_coef(0)
        coef_neu = get_class_coef(1)
        coef_pos = get_class_coef(2)

        def extract_top_words(coef_row, top_n):
            if coef_row is None:
                return []
            scored = [
                (feature_names[idx], float(coef_row[idx]) * float(features[0, idx]))
                for idx in non_zero_indices
                if idx < len(coef_row)
            ]
            scored.sort(key=lambda x: x[1], reverse=True)
            return [w for w, _ in scored[:top_n] if _ > 0]

        positive_words = extract_top_words(coef_pos, top_n)
        neutral_words = extract_top_words(coef_neu, top_n)
        negative_words = extract_top_words(coef_neg, top_n)

    except Exception as e:
        print(f"  Warning: keyword extraction failed: {e}")

    return {
        'positive': positive_words[:top_n],
        'neutral': neutral_words[:top_n],
        'negative': negative_words[:top_n],
    }


if __name__ == '__main__':
    # Quick validation test
    tests = [
        ("This product is absolutely amazing, I love it!", "Positive"),
        ("Terrible quality, worst purchase ever, completely broken.", "Negative"),
        ("The product arrived yesterday and I started using it today.", "Neutral"),
        ("The meeting is scheduled for Monday.", "Neutral"),
        ("The package contains two items.", "Neutral"),
        ("The laptop has 16GB RAM and a 512GB SSD.", "Neutral"),
        ("The event starts at 10 AM.", "Neutral"),
    ]

    print("\n  SentiVision AI — 3-Class Prediction Test\n")
    for text, expected in tests:
        result = predict_sentiment(text)
        sentiment = result['sentiment']
        confidence = result['confidence']
        passed = expected.lower() in sentiment.lower()
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] Expected: {expected:<10} Got: {sentiment} ({confidence:.1f}%)")
        print(f"         \"{text[:60]}\"")
        print(f"         Keywords: +{result['key_words']['positive'][:3]} "
              f"-{result['key_words']['negative'][:3]}")
        print()
