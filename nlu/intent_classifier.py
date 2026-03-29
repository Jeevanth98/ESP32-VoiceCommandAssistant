"""
Intent Classifier — TF-IDF + LinearSVC Supervised Pipeline
=============================================================
Replaces the earlier zero-shot BART classifier with a custom-trained
Scikit-Learn pipeline:

    preprocessor.preprocess  →  TfidfVectorizer  →  LinearSVC

The model is persisted with joblib so it only needs to be trained once.
At runtime it is loaded lazily on the first call to classify_intent().
"""

from __future__ import annotations

import os
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score

from config import INTENT_CONFIDENCE_THRESHOLD
from nlu.preprocessor import preprocess            # ← reuses your existing NLTK cleaner

# ─── Paths ───────────────────────────────────────────────────────────────────
_BASE_DIR   = os.path.dirname(os.path.dirname(__file__))      # project root
_MODEL_PATH = os.path.join(_BASE_DIR, "models", "intent_model.joblib")
_DATA_PATH  = os.path.join(_BASE_DIR, "data", "training_data.csv")

# ─── Lazy model singleton ───────────────────────────────────────────────────
_pipeline: Pipeline | None = None


# ──────────────────────────────────────────────────────────────────────────────
#  TRAINING
# ──────────────────────────────────────────────────────────────────────────────

def train_model(csv_path: str | None = None, evaluate: bool = True) -> Pipeline:
    """
    Train a TF-IDF + LinearSVC intent-classification pipeline.

    Steps
    -----
    1. Read labelled CSV  (columns: text, intent)
    2. Pre-process every utterance with ``nlu.preprocessor.preprocess``
    3. Build a Scikit-Learn Pipeline:
           TfidfVectorizer  →  CalibratedClassifierCV(LinearSVC)
       (Calibration wraps the SVM so we can get probability estimates.)
    4. Optionally evaluate with 5-fold cross-validation
    5. Fit on the *full* dataset and persist with joblib

    Returns the fitted Pipeline object.
    """
    csv_path = csv_path or _DATA_PATH

    # --- 1. Load data --------------------------------------------------------
    df = pd.read_csv(csv_path)
    print(f"[TRAIN] Loaded {len(df)} samples from {csv_path}")

    # --- 2. Pre-process -------------------------------------------------------
    df["clean"] = df["text"].astype(str).apply(preprocess)

    X = df["clean"]
    y = df["intent"]

    # --- 3. Build pipeline ----------------------------------------------------
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),     # unigrams + bigrams
            max_features=5000,
            sublinear_tf=True,      # apply 1 + log(tf)
        )),
        ("clf", CalibratedClassifierCV(
            estimator=LinearSVC(
                C=1.0,
                max_iter=10_000,
                class_weight="balanced",   # handle class imbalance
            ),
            cv=3,
        )),
    ])

    # --- 4. (Optional) Evaluate -----------------------------------------------
    if evaluate:
        scores = cross_val_score(pipeline, X, y, cv=5, scoring="accuracy")
        print(f"[TRAIN] 5-fold CV accuracy: {scores.mean():.2%} (± {scores.std():.2%})")

    # --- 5. Fit on full data & persist ----------------------------------------
    pipeline.fit(X, y)

    os.makedirs(os.path.dirname(_MODEL_PATH), exist_ok=True)
    joblib.dump(pipeline, _MODEL_PATH)
    print(f"[TRAIN] Model saved → {_MODEL_PATH}")

    # Update the in-memory singleton so restarting isn't required
    global _pipeline
    _pipeline = pipeline

    return pipeline


# ──────────────────────────────────────────────────────────────────────────────
#  PREDICTION
# ──────────────────────────────────────────────────────────────────────────────

def _load_model() -> Pipeline:
    """Load the trained model from disk (once) and cache it."""
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    if not os.path.isfile(_MODEL_PATH):
        raise FileNotFoundError(
            f"No trained model found at {_MODEL_PATH}.\n"
            "Run  python -c \"from nlu.intent_classifier import train_model; train_model()\"  first."
        )

    _pipeline = joblib.load(_MODEL_PATH)
    print(f"[NLU] Loaded intent model from {_MODEL_PATH}")
    return _pipeline


def classify_intent(cleaned_text: str) -> tuple[Optional[str], float]:
    """
    Classify a user command into one of the trained intents.

    Parameters
    ----------
    cleaned_text : str
        Pre-processed command string (output of ``preprocessor.preprocess``).

    Returns
    -------
    (intent_key, confidence)
        intent_key  – string label (e.g. "open_app"), or ``None`` if the
                       model's confidence is below ``INTENT_CONFIDENCE_THRESHOLD``.
        confidence  – float in [0, 1] from the calibrated SVM.
    """
    if not cleaned_text or not cleaned_text.strip():
        return None, 0.0

    pipe = _load_model()

    # predict_proba returns shape (1, n_classes)
    proba = pipe.predict_proba([cleaned_text])[0]
    best_idx = int(np.argmax(proba))
    best_label = pipe.classes_[best_idx]
    best_score = float(proba[best_idx])

    if best_score < INTENT_CONFIDENCE_THRESHOLD:
        return None, best_score

    return best_label, best_score


# ──────────────────────────────────────────────────────────────────────────────
#  CLI shortcut:  python -m nlu.intent_classifier
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "train":
        train_model()
    else:
        print("Usage:")
        print("  Train:   python -m nlu.intent_classifier train")
        print("  Predict: import classify_intent in your code")
