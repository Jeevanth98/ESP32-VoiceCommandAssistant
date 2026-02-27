"""
Command: Fuzzy File Search & Open
==================================
Scans configured directories for filenames that fuzzy-match the user's
query, ranks them, and opens the best match with the default application.
"""

from __future__ import annotations
import os
from pathlib import Path

from thefuzz import fuzz, process

from config import (
    SCAN_DIRECTORIES,
    SEARCHABLE_EXTENSIONS,
    FUZZY_MATCH_THRESHOLD,
    FUZZY_MAX_RESULTS,
)


def _build_file_index() -> dict[str, str]:
    """
    Walk all SCAN_DIRECTORIES and return {display_name: full_path}.
    display_name is the filename without extension (lower-cased) so that
    fuzzy matching works on natural names like "physics pdf".
    """
    index: dict[str, str] = {}
    for root_dir in SCAN_DIRECTORIES:
        if not os.path.isdir(root_dir):
            print(f"  [WARN] Scan directory not found: {root_dir}")
            continue
        for dirpath, _, filenames in os.walk(root_dir):
            for fname in filenames:
                ext = os.path.splitext(fname)[1].lower()
                if ext in SEARCHABLE_EXTENSIONS:
                    full = os.path.join(dirpath, fname)
                    # Key: "filename ext" so user can say "physics pdf"
                    display = f"{Path(fname).stem} {ext.lstrip('.')}".lower()
                    index[display] = full
    return index


def execute(file_query: str) -> str:
    """
    Search for *file_query* across indexed directories,
    open the best match, and return a user-friendly result string.
    """
    if not file_query:
        return "I didn't catch the file name. Could you repeat?"

    print(f"  [FILE-SEARCH] Building file index …")
    index = _build_file_index()

    if not index:
        return "No files found in the configured scan directories."

    query = file_query.lower()
    matches = process.extract(
        query,
        list(index.keys()),
        scorer=fuzz.token_set_ratio,
        limit=FUZZY_MAX_RESULTS,
    )

    # Filter by threshold
    good = [(name, score, index[name]) for name, score, *_ in matches if score >= FUZZY_MATCH_THRESHOLD]

    if not good:
        return f"No files matching \"{file_query}\" found (best score below {FUZZY_MATCH_THRESHOLD})."

    best_name, best_score, best_path = good[0]
    print(f"  [FILE-SEARCH] Best match: {best_name} (score {best_score})")
    print(f"                Path: {best_path}")

    # Open the file with the default application
    try:
        os.startfile(best_path)
        result = f"Opened \"{os.path.basename(best_path)}\" (match score: {best_score}%)."
    except Exception as e:
        result = f"Found the file but couldn't open it: {e}"

    # Also show runner-up matches
    if len(good) > 1:
        result += "\n  Other matches:"
        for name, score, path in good[1:]:
            result += f"\n    • {os.path.basename(path)}  (score {score}%)"

    return result
