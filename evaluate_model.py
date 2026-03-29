"""
Model Evaluation and Analysis Script
=====================================
Comprehensive evaluation of the NLU intent classifier with:
  - Cross-validation accuracy
  - Per-intent precision, recall, F1-score
  - Confusion matrix
  - Confidence score distribution
  - Misclassification analysis

Run: python evaluate_model.py
"""

from __future__ import annotations

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_predict, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
)
import joblib

from nlu.preprocessor import preprocess
from nlu.intent_classifier import _load_model, _DATA_PATH, _MODEL_PATH


def evaluate_model():
    """Full evaluation of the trained intent classifier."""
    
    print("="*70)
    print("ESP32 Voice Command Assistant — NLU Model Evaluation")
    print("="*70)
    print()

    # --- Load data -----------------------------------------------------------
    if not os.path.isfile(_DATA_PATH):
        print(f"❌ Training data not found at {_DATA_PATH}")
        print("   Run: python generate_data.py")
        return

    if not os.path.isfile(_MODEL_PATH):
        print(f"❌ Trained model not found at {_MODEL_PATH}")
        print("   Run: python -m nlu.intent_classifier train")
        return

    df = pd.read_csv(_DATA_PATH)
    print(f"📊 Loaded {len(df)} samples from training data")
    print(f"📦 Number of intents: {df['intent'].nunique()}")
    print()

    # --- Preprocess -----------------------------------------------------------
    print("🔄 Preprocessing text samples...")
    df["clean"] = df["text"].astype(str).apply(preprocess)
    X = df["clean"]
    y = df["intent"]
    
    # --- Load model -----------------------------------------------------------
    print(f"🧠 Loading model from {_MODEL_PATH}")
    pipeline = _load_model()
    print()

    # --- Cross-validation accuracy --------------------------------------------
    print("="*70)
    print("1. Cross-Validation Performance")
    print("="*70)
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipeline, X, y, cv=cv, scoring="accuracy")
    
    print(f"5-fold CV accuracy:")
    for i, score in enumerate(cv_scores, 1):
        print(f"  Fold {i}: {score:.2%}")
    print(f"\n  Mean:    {cv_scores.mean():.2%}")
    print(f"  Std Dev: {cv_scores.std():.2%}")
    print()

    # --- Per-intent metrics ---------------------------------------------------
    print("="*70)
    print("2. Per-Intent Classification Report")
    print("="*70)
    
    y_pred = cross_val_predict(pipeline, X, y, cv=cv)
    
    print(classification_report(y, y_pred, digits=4))
    print()

    # --- Confusion matrix -----------------------------------------------------
    print("="*70)
    print("3. Overall Accuracy")
    print("="*70)
    
    overall_acc = accuracy_score(y, y_pred)
    print(f"Overall accuracy: {overall_acc:.2%}")
    print()

    # --- Intent distribution --------------------------------------------------
    print("="*70)
    print("4. Training Data Distribution")
    print("="*70)
    
    intent_counts = df["intent"].value_counts().sort_values(ascending=False)
    print("\nSamples per intent:")
    for intent, count in intent_counts.items():
        print(f"  {intent:20s} : {count:4d} samples")
    print()

    # --- Misclassification analysis -------------------------------------------
    print("="*70)
    print("5. Misclassification Analysis")
    print("="*70)
    
    df_results = df.copy()
    df_results["predicted"] = y_pred
    df_results["correct"] = df_results["intent"] == df_results["predicted"]
    
    misclassified = df_results[~df_results["correct"]]
    
    if len(misclassified) == 0:
        print("\n✅ Perfect classification! No errors found.")
    else:
        print(f"\n❌ Found {len(misclassified)} misclassified samples ({len(misclassified)/len(df)*100:.2f}%):")
        print()
        
        # Show first 10 errors
        for idx, row in misclassified.head(10).iterrows():
            print(f"  Text: \"{row['text']}\"")
            print(f"    Expected: {row['intent']}")
            print(f"    Predicted: {row['predicted']}")
            print()
    
    # --- Confidence distribution ----------------------------------------------
    print("="*70)
    print("6. Confidence Score Distribution")
    print("="*70)
    
    # Get probability predictions
    probas = pipeline.predict_proba(X)
    max_probas = np.max(probas, axis=1)
    
    print(f"\nConfidence statistics:")
    print(f"  Mean confidence: {max_probas.mean():.2%}")
    print(f"  Median confidence: {np.median(max_probas):.2%}")
    print(f"  Min confidence: {max_probas.min():.2%}")
    print(f"  Max confidence: {max_probas.max():.2%}")
    print()
    
    # Show confidence buckets
    print("Confidence distribution:")
    bins = [0, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0]
    for i in range(len(bins)-1):
        count = ((max_probas >= bins[i]) & (max_probas < bins[i+1])).sum()
        pct = count / len(max_probas) * 100
        print(f"  {bins[i]:.2f} - {bins[i+1]:.2f}: {count:5d} samples ({pct:5.2f}%)")
    print()

    # --- Recommendations ------------------------------------------------------
    print("="*70)
    print("7. Recommendations")
    print("="*70)
    print()
    
    if overall_acc >= 0.99:
        print("✅ Excellent performance! Model is working very well.")
    elif overall_acc >= 0.95:
        print("✅ Good performance! Model is working well.")
        print("   Consider:")
        print("   - Adding more training examples for confused intents")
        print("   - Fine-tuning hyperparameters")
    elif overall_acc >= 0.90:
        print("⚠️  Acceptable performance, but could be improved.")
        print("   Recommendations:")
        print("   - Check misclassified samples above")
        print("   - Add more diverse training examples")
        print("   - Balance class distribution if needed")
        print("   - Tune hyperparameters (C, ngram_range, max_features)")
    else:
        print("❌ Performance needs improvement.")
        print("   Recommendations:")
        print("   - Review training data quality")
        print("   - Add significantly more training examples")
        print("   - Check for overlapping intents")
        print("   - Consider feature engineering")
    
    print()
    
    # Check class imbalance
    max_samples = intent_counts.max()
    min_samples = intent_counts.min()
    imbalance_ratio = max_samples / min_samples
    
    if imbalance_ratio > 3:
        print("⚠️  Class imbalance detected!")
        print(f"   Ratio: {imbalance_ratio:.1f}:1 (max: {max_samples}, min: {min_samples})")
        print("   Consider generating more samples for underrepresented intents.")
        print()
    
    # Check low-confidence predictions
    low_conf_count = (max_probas < 0.5).sum()
    if low_conf_count > len(df) * 0.05:  # More than 5%
        print(f"⚠️  {low_conf_count} predictions have low confidence (<50%).")
        print("   This may indicate ambiguous training data or overlapping intents.")
        print()
    
    print("="*70)
    print("Evaluation complete!")
    print("="*70)


if __name__ == "__main__":
    try:
        evaluate_model()
    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
