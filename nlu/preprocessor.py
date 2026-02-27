"""
NLU Preprocessor — Stop-Word Removal & Lemmatization
=====================================================
Cleans raw transcribed text before intent classification.
Uses NLTK for stop-word filtering and WordNet lemmatization.
"""

import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# ─── One-time NLTK data download (silent if already present) ────────────────
_NLTK_DATA = ["punkt", "punkt_tab", "stopwords", "wordnet", "omw-1.4"]
for _pkg in _NLTK_DATA:
    nltk.download(_pkg, quiet=True)

# ─── Initialise once ────────────────────────────────────────────────────────
_lemmatizer = WordNetLemmatizer()
_stop_words = set(stopwords.words("english"))

# Words we want to KEEP even though NLTK considers them stop-words,
# because they carry meaning for our command set.
_KEEP_WORDS = {"open", "search", "find", "write", "type", "my", "in", "for", "down"}


def preprocess(text: str) -> str:
    """
    Clean and normalise a raw command string.

    Pipeline:
        1. Lower-case
        2. Strip non-alphanumeric chars (keep spaces)
        3. Tokenize
        4. Remove stop-words (except domain-important ones)
        5. Lemmatize each token
        6. Rejoin into a single string

    Returns the cleaned string (may be empty if input was all noise).
    """
    text = text.lower().strip()
    # Keep alphanumeric, spaces, and basic punctuation that helps entity extraction
    text = re.sub(r"[^a-z0-9\s:.\-]", "", text)

    tokens = word_tokenize(text)

    cleaned = []
    for tok in tokens:
        if tok in _KEEP_WORDS or tok not in _stop_words:
            lemma = _lemmatizer.lemmatize(tok, pos="v")  # verb-first lemmatization
            lemma = _lemmatizer.lemmatize(lemma, pos="n")  # then noun
            cleaned.append(lemma)

    return " ".join(cleaned)


def tokenize_raw(text: str) -> list[str]:
    """Return lowered tokens *without* stop-word removal (useful for entity extraction)."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s:.\-]", "", text)
    return word_tokenize(text)
