"""
Command: AI Summarization — Abstractive summary of documents
=============================================================
Finds a document via fuzzy search, extracts its text, and sends
it to the Hugging Face facebook/bart-large-cnn summarization model.
Generates a concise 2-3 line summary (Abstractive Summarization).
"""

from __future__ import annotations
import os
from pathlib import Path

from thefuzz import fuzz, process

from config import (
    SCAN_DIRECTORIES,
    SEARCHABLE_EXTENSIONS,
    FUZZY_MATCH_THRESHOLD,
    SUMMARIZATION_MODEL,
    SUMMARY_MAX_TOKENS,
    SUMMARY_MAX_LENGTH,
    SUMMARY_MIN_LENGTH,
)
from utils.text_extraction import extract_text

# ─── Lazy model singleton ───────────────────────────────────────────────────
_summarizer = None


def _load_model():
    global _summarizer
    if _summarizer is not None:
        return _summarizer

    print("  [SUMMARIZE] Loading summarization model — first run may take a while …")
    from transformers import pipeline

    _summarizer = pipeline(
        "summarization",
        model=SUMMARIZATION_MODEL,
        device=-1,  # CPU
    )
    print("  [SUMMARIZE] Model loaded.")
    return _summarizer


def _find_file(query: str) -> str | None:
    """Fuzzy-search for a file matching the query and return its path."""
    index: dict[str, str] = {}
    for root_dir in SCAN_DIRECTORIES:
        if not os.path.isdir(root_dir):
            continue
        for dirpath, _, filenames in os.walk(root_dir):
            for fname in filenames:
                ext = os.path.splitext(fname)[1].lower()
                if ext in {".pdf", ".docx", ".txt"}:
                    full = os.path.join(dirpath, fname)
                    display = f"{Path(fname).stem} {ext.lstrip('.')}".lower()
                    index[display] = full
    if not index:
        return None

    matches = process.extract(
        query.lower(), list(index.keys()), scorer=fuzz.token_set_ratio, limit=1
    )
    if matches and matches[0][1] >= FUZZY_MATCH_THRESHOLD:
        return index[matches[0][0]]
    return None


def execute(file_query: str) -> str:
    """
    Find a document matching *file_query*, extract text, summarize it.
    """
    if not file_query:
        return "Which document should I summarize? Please include the file name."

    print(f"  [SUMMARIZE] Looking for \"{file_query}\" …")
    path = _find_file(file_query)
    if path is None:
        return f"Could not find a document matching \"{file_query}\"."

    print(f"  [SUMMARIZE] Found: {path}")
    text = extract_text(path)
    if not text or len(text.strip()) < 50:
        return f"The file \"{os.path.basename(path)}\" has too little text to summarize."

    # Truncate to max tokens (rough char estimate: 1 token ≈ 4 chars)
    max_chars = SUMMARY_MAX_TOKENS * 4
    if len(text) > max_chars:
        text = text[:max_chars]
        print(f"  [SUMMARIZE] Text truncated to ~{SUMMARY_MAX_TOKENS} tokens.")

    summarizer = _load_model()
    print(f"  [SUMMARIZE] Generating summary …")

    result = summarizer(
        text,
        max_length=SUMMARY_MAX_LENGTH,
        min_length=SUMMARY_MIN_LENGTH,
        do_sample=False,
    )

    summary = result[0]["summary_text"]
    fname = os.path.basename(path)
    return f"Summary of \"{fname}\":\n\n{summary}"
