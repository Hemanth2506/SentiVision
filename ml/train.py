"""
SentiVision AI — Model Training Pipeline
3-class sentiment: Negative (0) / Neutral (1) / Positive (2)
Trains 4 ML models, validates Neutral F1 >= 80%, saves best model.
"""

import os
import sys
import time
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV

# Add ml/ dir to path
sys.path.insert(0, os.path.dirname(__file__))

from preprocess import clean_text, preprocess_corpus, build_tfidf_vectorizer, save_vectorizer
from clean_neutral import clean_and_save
from generate_mild_negative import generate_mild_negative_examples
from evaluate import (evaluate_model, compare_models, get_confusion_matrix, print_confusion_matrix, get_classification_report, print_per_class_metrics, check_neutral_f1_gate, CLASS_NAMES, MIN_NEUTRAL_F1)

# ─── Configuration ──────────────────────────────────────────────────
DATASET_PATH = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'reviews.csv')
CLEANED_DATASET_PATH = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'reviews_cleaned.csv')
EXTRA_MILD_NEG_PATH = os.path.join(os.path.dirname(__file__), 'extra_mild_negative.txt')
MODEL_SAVE_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')
VECTORIZER_SAVE_PATH = os.path.join(os.path.dirname(__file__), 'vectorizer.pkl')
METADATA_PATH = os.path.join(os.path.dirname(__file__), 'model_metadata.json')
REGISTRY_PATH = os.path.join(os.path.dirname(__file__), 'model_registry.json')

TEST_SIZE = 0.2
RANDOM_STATE = 42
MAX_FEATURES = 20000


def load_dataset(path=DATASET_PATH):
    """Load 3-class dataset. Labels: 0=Negative, 1=Neutral, 2=Positive."""
    print("\n" + "=" * 60)
    print("  STEP 1: Loading Dataset")
    print("=" * 60)

    if not os.path.exists(path):
        print(f"\n  [x] Dataset not found at: {path}")
        print("  Run: python ml/download_dataset.py")
        sys.exit(1)

    df = pd.read_csv(path, encoding='utf-8')

    # Validate columns
    if 'text' not in df.columns or 'sentiment' not in df.columns:
        print("  [x] Dataset must have 'text' and 'sentiment' columns.")
        sys.exit(1)

    df = df.dropna(subset=['text', 'sentiment'])
    df['sentiment'] = df['sentiment'].astype(int)

    # Validate labels
    valid_labels = {0, 1, 2}
    invalid = set(df['sentiment'].unique()) - valid_labels
    if invalid:
        print(f"  [x] Invalid labels found: {invalid}. Expected 0, 1, 2.")
        sys.exit(1)

    print(f"  Dataset loaded: {len(df)} records")
    label_names = {0: 'Negative', 1: 'Neutral', 2: 'Positive'}
    print(f"  Label distribution:")
    for code in [0, 1, 2]:
        count = (df['sentiment'] == code).sum()
        pct = count / len(df) * 100
        print(f"    {label_names[code]}: {count} ({pct:.1f}%)")

    return df['text'].tolist(), df['sentiment'].tolist()


def train_models(X_train, X_test, y_train, y_test):
    """Train 4 ML models and evaluate each on 3-class task."""
    print("\n" + "=" * 60)
    print("  STEP 3: Training Models")
    print("=" * 60)

    models = {
        'Logistic Regression': LogisticRegression(
            max_iter=1000, C=1.0, solver='lbfgs',
            random_state=RANDOM_STATE
        ),
        'Naive Bayes': MultinomialNB(alpha=0.5),
        'Random Forest': RandomForestClassifier(
            n_estimators=200, max_depth=50,
            random_state=RANDOM_STATE, n_jobs=-1
        ),
        'SVM (LinearSVC)': CalibratedClassifierCV(
            LinearSVC(max_iter=3000, C=1.0, random_state=RANDOM_STATE), cv=3
        ),
    }

    results = []
    for name, model in models.items():
        print(f"\n  Training {name}...")
        start = time.time()

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        metrics = evaluate_model(y_test, y_pred, model_name=name)
        elapsed = time.time() - start
        metrics['training_time'] = round(elapsed, 2)

        print(f"  Trained in {elapsed:.1f}s | Accuracy: {metrics['accuracy']:.4f} | "
              f"Overall F1: {metrics['f1_score']:.4f} | Neutral F1: {metrics['neutral_f1']:.4f}")

        print_per_class_metrics(metrics)
        cm = get_confusion_matrix(y_test, y_pred)
        print_confusion_matrix(cm)
        report = get_classification_report(y_test, y_pred)
        print(f"  Classification Report:\n{report}")

        results.append((name, model, metrics))

    return results


def select_and_save_best_model(results):
    """Select best model by Neutral F1 + overall F1, enforce deployment gate."""
    print("\n" + "=" * 60)
    print("  STEP 4: Model Selection & Deployment Gate")
    print("=" * 60)

    metrics_list = [r[2] for r in results]
    best_metrics, comparison_table = compare_models(metrics_list)
    print(comparison_table)

    # Gate check
    passes_gate, neutral_f1 = check_neutral_f1_gate(best_metrics)

    if not passes_gate:
        print(f"\n  [GATE FAILED] Neutral F1 = {neutral_f1:.4f} < {MIN_NEUTRAL_F1}")
        print("  Model will NOT be saved. Please improve the dataset and retrain.")
        return None, None

    # Find best model object
    best_name = best_metrics['model_name']
    best_model = None
    for name, model, _ in results:
        if name == best_name:
            best_model = model
            break

    # Save model
    joblib.dump(best_model, MODEL_SAVE_PATH)
    print(f"\n  [GATE PASSED] Neutral F1 = {neutral_f1:.4f} >= {MIN_NEUTRAL_F1}")
    print(f"  Best model ({best_name}) saved to: {MODEL_SAVE_PATH}")

    # Save metadata
    version = datetime.now().strftime("%Y%m%d_%H%M%S")
    metadata = {
        "model_name": best_name,
        "version": version,
        "accuracy": best_metrics['accuracy'],
        "precision": best_metrics['precision'],
        "recall": best_metrics['recall'],
        "f1_score": best_metrics['f1_score'],
        "neutral_f1": best_metrics['neutral_f1'],
        "per_class": best_metrics.get('per_class', {}),
        "training_date": datetime.now().isoformat(),
        "classes": {
            "0": "Negative",
            "1": "Neutral",
            "2": "Positive"
        },
        "gate_passed": True,
        "gate_threshold": MIN_NEUTRAL_F1,
    }
    with open(METADATA_PATH, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"  Model metadata saved to: {METADATA_PATH}")

    # Update model registry (MLOps versioning)
    registry = []
    if os.path.exists(REGISTRY_PATH):
        try:
            with open(REGISTRY_PATH, 'r') as f:
                registry = json.load(f)
        except Exception:
            registry = []

    registry.append({
        "version": version,
        "model_name": best_name,
        "accuracy": best_metrics['accuracy'],
        "neutral_f1": best_metrics['neutral_f1'],
        "f1_score": best_metrics['f1_score'],
        "training_date": datetime.now().isoformat(),
        "is_active": True,
    })
    # Only keep latest 10 entries active
    for entry in registry[:-1]:
        entry['is_active'] = False

    with open(REGISTRY_PATH, 'w') as f:
        json.dump(registry, f, indent=2)
    print(f"  Model registry updated: {REGISTRY_PATH}")

    return best_name, best_model


def main():
    """Main training pipeline."""
    print("\n" + "=" * 60)
    print("  SentiVision AI — 3-Class Training Pipeline")
    print("  Positive / Neutral / Negative")
    print("=" * 60)
    total_start = time.time()

    # Step 0: Ensure neutral contamination is cleaned
    contamination_keywords = ["delayed", "longer than expected", "issue", "problem", "slow", "broken", "stopped working", "complaint"]
    # Create cleaned dataset (overwrites if exists)
    clean_and_save(DATASET_PATH, CLEANED_DATASET_PATH, contamination_keywords)

    # Step 0b: Generate mild‑negative examples if missing
    if not os.path.exists(EXTRA_MILD_NEG_PATH):
        generate_mild_negative_examples(EXTRA_MILD_NEG_PATH)

    # Step 1: Load dataset (cleaned version)
    texts, labels = load_dataset(CLEANED_DATASET_PATH)

    # Step 1c: Append mild‑negative examples
    if os.path.exists(EXTRA_MILD_NEG_PATH):
        with open(EXTRA_MILD_NEG_PATH, 'r', encoding='utf-8') as f:
            extra_texts = [line.strip() for line in f if line.strip()]
        texts.extend(extra_texts)
        labels.extend([0] * len(extra_texts))

    # Step 2: Preprocess and vectorize
    print("\n" + "=" * 60)
    print("  STEP 2: Preprocessing & Vectorization")
    print("=" * 60)

    cleaned_texts = preprocess_corpus(texts)
    vectorizer, features = build_tfidf_vectorizer(cleaned_texts, max_features=MAX_FEATURES)
    save_vectorizer(vectorizer, VECTORIZER_SAVE_PATH)

    # Stratified split (preserves class balance)
    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=TEST_SIZE,
        random_state=RANDOM_STATE, stratify=labels
    )
    print(f"  Train set: {X_train.shape[0]} | Test set: {X_test.shape[0]}")

    # Step 3: Train all models
    results = train_models(X_train, X_test, y_train, y_test)

    # Step 4: Select, gate-check, save best model
    best_name, best_model = select_and_save_best_model(results)

    total_elapsed = time.time() - total_start

    if best_model is not None:
        print(f"\n  Training complete in {total_elapsed:.1f}s")
        print(f"  Best model: {best_name}")
        print(f"  Files: model.pkl, vectorizer.pkl, model_metadata.json\n")

        # Validation: test required sentences
        print("\n  SENTIMENT VALIDATION TEST:")
        print("  " + "-" * 60)
        sys.path.insert(0, os.path.dirname(__file__))
        from predict import predict_sentiment

        validation_tests = [
            ("The product arrived yesterday and I started using it today.", "Neutral"),
            ("The meeting is scheduled for Monday.", "Neutral"),
            ("The package contains two items.", "Neutral"),
            ("This product is absolutely amazing!", "Positive"),
            ("Worst purchase I have ever made.", "Negative")
        ]

        all_passed = True
        for test_text, expected in validation_tests:
            result = predict_sentiment(test_text)
            sentiment = result['sentiment']
            confidence = result['confidence']
            if expected == "Neutral":
                passed = sentiment in ["Neutral", "Neutral/Uncertain"]
            else:
                passed = sentiment == expected
            status = "PASS" if passed else "FAIL"
            if not passed:
                all_passed = False
            print(f"  [{status}] Expected: {expected:<8} | Got: {sentiment:<17} ({confidence:.1f}%) | \"{test_text}\"")

        print("\n  NEGATION VALIDATION TESTS (>70% confidence Negative required):")
        print("  " + "-" * 60)
        negation_tests = [
            "The quality is not as described on the website.",
            "The product did not meet my expectations.",
            "I have not received a response from customer support yet."
        ]
        for test_text in negation_tests:
            result = predict_sentiment(test_text)
            sentiment = result['sentiment']
            confidence = result['confidence']
            passed = (sentiment == "Negative") and (confidence > 70.0)
            status = "PASS" if passed else "FAIL"
            if not passed:
                all_passed = False
            print(f"  [{status}] Expected: Negative (>70%) | Got: {sentiment:<17} ({confidence:.1f}%) | \"{test_text}\"")

        print()
        if all_passed:
            print("  All validation tests PASSED.")
        else:
            print("  WARNING: Some validation tests FAILED.")
        print()
    else:
        print(f"\n  Training complete in {total_elapsed:.1f}s — deployment gate NOT met.")


if __name__ == '__main__':
    main()
