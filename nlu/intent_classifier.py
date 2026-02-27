"""
Intent Classifier — Zero-Shot Classification
==============================================
Uses Hugging Face's facebook/bart-large-mnli to compute semantic
similarity between a user command and a set of intent labels.

The model is loaded lazily on first call to avoid slow import times.
"""

from __future__ import annotations
import sys
from typing import Optional

from config import (
    ZERO_SHOT_MODEL,
    INTENT_LABELS,
    INTENT_KEYS,
    INTENT_CONFIDENCE_THRESHOLD,
)

# ─── Lazy model singleton ───────────────────────────────────────────────────
_classifier = None


def _load_model():
    """Load the zero-shot pipeline once and cache it."""
    global _classifier
    if _classifier is not None:
        return _classifier

    print("[NLU] Loading zero-shot classifier — this may take a minute on first run …")
    from transformers import pipeline

    _classifier = pipeline(
        "zero-shot-classification",
        model=ZERO_SHOT_MODEL,
        device=-1,  # CPU only; change to 0 for CUDA GPU
    )
    print("[NLU] Model loaded successfully.")
    return _classifier


def classify_intent(cleaned_text: str) -> tuple[Optional[str], float]:
    """
    Classify the user's command into one of the predefined intents.

    Parameters
    ----------
    cleaned_text : str
        Pre-processed command string (output of preprocessor.preprocess).

    Returns
    -------
    (intent_key, confidence)
        intent_key  – one of config.INTENT_KEYS, or None if below threshold.
        confidence  – float 0-1 score from the model.
    """
    if not cleaned_text.strip():
        return None, 0.0

    clf = _load_model()
    result = clf(cleaned_text, candidate_labels=INTENT_LABELS, multi_label=False)

    best_label = result["labels"][0]
    best_score = result["scores"][0]

    # Map the human-readable label back to its programmatic key
    idx = INTENT_LABELS.index(best_label)
    intent_key = INTENT_KEYS[idx]

    if best_score < INTENT_CONFIDENCE_THRESHOLD:
        return None, best_score

    return intent_key, best_score
