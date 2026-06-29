"""
SentiVision AI — Model Evaluation Module
Computes per-class metrics: Accuracy, Precision, Recall, F1.
Supports 3-class classification (Positive / Neutral / Negative).
"""

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

# Label mapping for 3-class
LABEL_NAMES = {0: 'Negative', 1: 'Neutral', 2: 'Positive'}
CLASS_ORDER = [0, 1, 2]
CLASS_NAMES = ['Negative', 'Neutral', 'Positive']

# Minimum required Neutral F1 to allow model deployment
MIN_NEUTRAL_F1 = 0.75


def evaluate_model(y_true, y_pred, model_name: str = "Model") -> dict:
    """
    Compute comprehensive evaluation metrics for 3-class sentiment.

    Returns per-class Precision / Recall / F1 and overall Accuracy.

    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels
        model_name: Display name for the model

    Returns:
        dict: Full metrics including per-class breakdown
    """
    accuracy = accuracy_score(y_true, y_pred)

    # Macro-averaged overall metrics
    precision_macro = precision_score(y_true, y_pred, average='macro', zero_division=0)
    recall_macro = recall_score(y_true, y_pred, average='macro', zero_division=0)
    f1_macro = f1_score(y_true, y_pred, average='macro', zero_division=0)

    # Per-class metrics
    precision_per = precision_score(y_true, y_pred, average=None, labels=CLASS_ORDER, zero_division=0)
    recall_per = recall_score(y_true, y_pred, average=None, labels=CLASS_ORDER, zero_division=0)
    f1_per = f1_score(y_true, y_pred, average=None, labels=CLASS_ORDER, zero_division=0)

    per_class = {}
    for i, (label_id, label_name) in enumerate(LABEL_NAMES.items()):
        per_class[label_name.lower()] = {
            'precision': round(float(precision_per[i]), 4),
            'recall': round(float(recall_per[i]), 4),
            'f1': round(float(f1_per[i]), 4),
        }

    neutral_f1 = per_class['neutral']['f1']

    return {
        'model_name': model_name,
        'accuracy': round(float(accuracy), 4),
        'precision': round(float(precision_macro), 4),
        'recall': round(float(recall_macro), 4),
        'f1_score': round(float(f1_macro), 4),
        'neutral_f1': round(float(neutral_f1), 4),
        'per_class': per_class,
    }


def check_neutral_f1_gate(metrics: dict) -> tuple:
    """
    Check if model meets the Neutral F1 deployment gate.

    Args:
        metrics: Evaluation metrics dict

    Returns:
        tuple: (passes: bool, neutral_f1: float)
    """
    neutral_f1 = metrics.get('neutral_f1', 0.0)
    passes = neutral_f1 >= MIN_NEUTRAL_F1
    return passes, neutral_f1


def get_confusion_matrix(y_true, y_pred):
    """Return confusion matrix for 3-class classification."""
    return confusion_matrix(y_true, y_pred, labels=CLASS_ORDER)


def print_confusion_matrix(cm, labels=None):
    """Print a formatted confusion matrix."""
    if labels is None:
        labels = CLASS_NAMES
    print(f"\n  Confusion Matrix:")
    header = "         " + " ".join(f"{l:>10}" for l in labels)
    print(header)
    for i, row in enumerate(cm):
        row_str = " ".join(f"{v:>10}" for v in row)
        print(f"  {labels[i]:>8} {row_str}")
    print()


def get_classification_report(y_true, y_pred, target_names=None):
    """Return sklearn classification report string."""
    if target_names is None:
        target_names = CLASS_NAMES
    return classification_report(y_true, y_pred, target_names=target_names,
                                 labels=CLASS_ORDER, zero_division=0)


def compare_models(metrics_list: list) -> tuple:
    """
    Compare multiple models and return the best one by F1 score.
    Also considers Neutral F1 gate — models that fail it are penalized.

    Args:
        metrics_list: List of metrics dicts

    Returns:
        tuple: (best_metrics_dict, comparison_table_string)
    """
    # Sort: gate-passing models first, then by neutral_f1 * overall_f1
    def sort_key(m):
        passes_gate = m.get('neutral_f1', 0) >= MIN_NEUTRAL_F1
        return (int(passes_gate), m.get('neutral_f1', 0), m.get('f1_score', 0))

    sorted_metrics = sorted(metrics_list, key=sort_key, reverse=True)
    best = sorted_metrics[0]

    # Build comparison table
    lines = []
    lines.append("\n  " + "=" * 90)
    lines.append("  MODEL COMPARISON RESULTS")
    lines.append("  " + "=" * 90)
    lines.append(
        f"  {'Model':<25} {'Accuracy':>9} {'Precision':>10} {'Recall':>8} "
        f"{'F1':>8} {'Neu-F1':>9} {'Gate':>6}"
    )
    lines.append("  " + "-" * 90)

    for m in metrics_list:
        gate_pass = "PASS" if m.get('neutral_f1', 0) >= MIN_NEUTRAL_F1 else "FAIL"
        lines.append(
            f"  {m['model_name']:<25} "
            f"{m['accuracy']:>9.4f} "
            f"{m['precision']:>10.4f} "
            f"{m['recall']:>8.4f} "
            f"{m['f1_score']:>8.4f} "
            f"{m['neutral_f1']:>9.4f} "
            f"{gate_pass:>6}"
        )

    lines.append("  " + "=" * 90)
    lines.append(f"  >> Best Model: {best['model_name']} "
                 f"(Neutral F1={best['neutral_f1']:.4f}, Overall F1={best['f1_score']:.4f})")

    if best.get('neutral_f1', 0) < MIN_NEUTRAL_F1:
        lines.append(f"  >> WARNING: Best model does NOT meet Neutral F1 >= {MIN_NEUTRAL_F1}!")
        lines.append(f"  >> Deployment gate NOT passed. Model will NOT be saved.")
    else:
        lines.append(f"  >> Deployment gate PASSED.")
    lines.append("  " + "=" * 90 + "\n")

    return best, '\n'.join(lines)


def print_per_class_metrics(metrics: dict):
    """Pretty-print per-class metrics."""
    per_class = metrics.get('per_class', {})
    print("\n  Per-Class Metrics:")
    print(f"  {'Class':<12} {'Precision':>10} {'Recall':>8} {'F1':>8}")
    print("  " + "-" * 42)
    for cls_name in ['positive', 'neutral', 'negative']:
        m = per_class.get(cls_name, {})
        print(
            f"  {cls_name.capitalize():<12} "
            f"{m.get('precision', 0):>10.4f} "
            f"{m.get('recall', 0):>8.4f} "
            f"{m.get('f1', 0):>8.4f}"
        )
    print()
