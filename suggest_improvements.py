"""
NLU Improvement Suggestions
============================
Analyzes current model performance and suggests specific improvements:
- Data augmentation strategies
- Hyperparameter tuning recommendations
- Feature engineering ideas
- Architecture improvements

Run after evaluate_model.py to get actionable improvement suggestions.
"""

from __future__ import annotations

import os
import pandas as pd
import numpy as np
from collections import Counter
import joblib

from nlu.preprocessor import preprocess
from nlu.intent_classifier import _DATA_PATH, _MODEL_PATH


def analyze_and_suggest():
    """Analyze training data and model to suggest improvements."""
    
    print("="*70)
    print("NLU Improvement Analysis & Suggestions")
    print("="*70)
    print()
    
    # Load data
    if not os.path.isfile(_DATA_PATH):
        print(f"❌ Training data not found at {_DATA_PATH}")
        return
    
    df = pd.read_csv(_DATA_PATH)
    
    # === 1. Data Quality Analysis ===
    print("="*70)
    print("1. Training Data Quality Analysis")
    print("="*70)
    print()
    
    # Check duplicates
    duplicates = df.duplicated(subset=["text"], keep=False).sum()
    if duplicates > 0:
        print(f"⚠️  Found {duplicates} duplicate text samples")
        print("   Suggestion: Remove exact duplicates to reduce overfitting")
        print()
    
    # Check text length distribution
    df["text_len"] = df["text"].str.len()
    print(f"Text length statistics:")
    print(f"  Mean: {df['text_len'].mean():.1f} characters")
    print(f"  Median: {df['text_len'].median():.1f} characters")
    print(f"  Min: {df['text_len'].min()} characters")
    print(f"  Max: {df['text_len'].max()} characters")
    print()
    
    # Check for very short samples
    very_short = (df["text_len"] < 10).sum()
    if very_short > 0:
        print(f"⚠️  {very_short} samples are very short (<10 chars)")
        print("   These may not provide enough context for classification")
        print()
    
    # === 2. Class Balance Analysis ===
    print("="*70)
    print("2. Class Balance Analysis")
    print("="*70)
    print()
    
    intent_counts = df["intent"].value_counts()
    max_samples = intent_counts.max()
    min_samples = intent_counts.min()
    imbalance_ratio = max_samples / min_samples
    
    print(f"Imbalance ratio: {imbalance_ratio:.2f}:1")
    print(f"  Largest class: {intent_counts.index[0]} ({max_samples} samples)")
    print(f"  Smallest class: {intent_counts.index[-1]} ({min_samples} samples)")
    print()
    
    if imbalance_ratio > 3:
        print("⚠️  Significant class imbalance detected!")
        print()
        print("Suggestions:")
        print("  1. Generate more samples for underrepresented intents")
        print("  2. Use class_weight='balanced' in classifier (already enabled)")
        print("  3. Consider oversampling minority classes")
        print()
        
        # Show top 5 underrepresented
        print("Most underrepresented intents:")
        for intent, count in intent_counts.tail(5).items():
            target = max_samples // 2
            needed = max(0, target - count)
            print(f"  {intent:20s}: {count:4d} samples (add ~{needed} more)")
        print()
    else:
        print("✅ Classes are reasonably balanced")
        print()
    
    # === 3. Vocabulary Analysis ===
    print("="*70)
    print("3. Vocabulary Analysis")
    print("="*70)
    print()
    
    df["clean"] = df["text"].apply(preprocess)
    
    # Get all words
    all_words = []
    for text in df["clean"]:
        all_words.extend(text.split())
    
    word_counts = Counter(all_words)
    vocab_size = len(word_counts)
    
    print(f"Total vocabulary size: {vocab_size} unique words")
    print(f"Total word occurrences: {len(all_words)}")
    print()
    
    # Show most common words
    print("Most frequent words:")
    for word, count in word_counts.most_common(10):
        print(f"  {word:15s}: {count:4d} occurrences")
    print()
    
    # Check for rare words (appear only once)
    rare_words = [word for word, count in word_counts.items() if count == 1]
    if len(rare_words) > vocab_size * 0.3:  # More than 30% rare words
        print(f"⚠️  {len(rare_words)} words appear only once ({len(rare_words)/vocab_size*100:.1f}%)")
        print("   Suggestion: Add more diverse training examples")
        print()
    
    # === 4. Intent Similarity Analysis ===
    print("="*70)
    print("4. Intent Overlap & Confusion Risk")
    print("="*70)
    print()
    
    # For each pair of intents, check for overlapping keywords
    intents = df["intent"].unique()
    
    # Build keyword sets for each intent
    intent_keywords = {}
    for intent in intents:
        intent_samples = df[df["intent"] == intent]["clean"]
        words = []
        for text in intent_samples:
            words.extend(text.split())
        # Get top 10 most common words for this intent
        intent_keywords[intent] = set([w for w, _ in Counter(words).most_common(10)])
    
    # Find pairs with high overlap
    high_overlap_pairs = []
    for i, intent1 in enumerate(intents):
        for intent2 in intents[i+1:]:
            overlap = intent_keywords[intent1] & intent_keywords[intent2]
            overlap_pct = len(overlap) / max(len(intent_keywords[intent1]), len(intent_keywords[intent2])) * 100
            if overlap_pct > 30:  # More than 30% overlap
                high_overlap_pairs.append((intent1, intent2, overlap_pct, overlap))
    
    if high_overlap_pairs:
        print("⚠️  Detected intent pairs with high keyword overlap:")
        print()
        for intent1, intent2, pct, overlap in high_overlap_pairs[:5]:  # Show top 5
            print(f"  {intent1} <-> {intent2}: {pct:.1f}% overlap")
            print(f"    Shared words: {', '.join(list(overlap)[:5])}")
            print()
        print("  Suggestion: Review these intents for potential confusion")
        print("  Add more distinguishing examples for each")
        print()
    else:
        print("✅ No significant intent overlap detected")
        print()
    
    # === 5. Hyperparameter Tuning Suggestions ===
    print("="*70)
    print("5. Hyperparameter Tuning Suggestions")
    print("="*70)
    print()
    
    if os.path.isfile(_MODEL_PATH):
        pipeline = joblib.load(_MODEL_PATH)
        
        # Current settings
        print("Current TF-IDF settings:")
        tfidf = pipeline.named_steps["tfidf"]
        print(f"  ngram_range: {tfidf.ngram_range}")
        print(f"  max_features: {tfidf.max_features}")
        print(f"  sublinear_tf: {tfidf.sublinear_tf}")
        print()
        
        print("Current classifier settings:")
        clf = pipeline.named_steps["clf"].base_estimator
        print(f"  C: {clf.C}")
        print(f"  class_weight: {clf.class_weight}")
        print()
        
        print("Tuning suggestions:")
        print("  1. Try different ngram ranges:")
        print("     - (1, 3) for trigrams (capture longer phrases)")
        print("     - (1, 1) for unigrams only (faster, simpler)")
        print()
        print("  2. Adjust max_features:")
        print(f"     - Current: {tfidf.max_features}")
        print("     - Try: 3000 (simpler) or 10000 (more features)")
        print()
        print("  3. Tune regularization (C parameter):")
        print("     - Current: 1.0")
        print("     - Try: 0.5 (more regularization) or 2.0 (less regularization)")
        print()
    
    # === 6. Data Augmentation Suggestions ===
    print("="*70)
    print("6. Data Augmentation Strategies")
    print("="*70)
    print()
    
    print("Recommended augmentation techniques:")
    print()
    print("  1. Synonym replacement:")
    print("     'open chrome' → 'launch chrome', 'start chrome'")
    print()
    print("  2. Random insertion:")
    print("     'open chrome' → 'please open chrome', 'can you open chrome'")
    print()
    print("  3. Random swap:")
    print("     'search for quantum' → 'quantum search for'")
    print()
    print("  4. Paraphrasing:")
    print("     'what is my cpu usage' → 'show me cpu usage', 'check cpu usage'")
    print()
    print("  5. Add typos/errors (simulate speech-to-text errors):")
    print("     'open chrome' → 'open chrom', 'open crome'")
    print()
    
    # === 7. Advanced Techniques ===
    print("="*70)
    print("7. Advanced Improvement Techniques")
    print("="*70)
    print()
    
    print("If accuracy is still not satisfactory, consider:")
    print()
    print("  1. Feature Engineering:")
    print("     - Add word embeddings (Word2Vec, GloVe)")
    print("     - Include POS tags as features")
    print("     - Add character n-grams")
    print()
    print("  2. Model Architecture:")
    print("     - Try different classifiers (Random Forest, XGBoost)")
    print("     - Ensemble multiple models")
    print("     - Use deep learning (LSTM, BERT) for complex patterns")
    print()
    print("  3. Active Learning:")
    print("     - Identify low-confidence predictions")
    print("     - Manually label and add them to training set")
    print()
    print("  4. Error Analysis:")
    print("     - Analyze misclassified samples")
    print("     - Identify common error patterns")
    print("     - Generate targeted training data")
    print()
    
    print("="*70)
    print("Analysis complete!")
    print("="*70)


if __name__ == "__main__":
    try:
        analyze_and_suggest()
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
