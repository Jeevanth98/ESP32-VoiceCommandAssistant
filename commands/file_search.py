"""
Command: Fuzzy File Search & Open
==================================
Scans configured directories for filenames that fuzzy-match the user's
query, ranks them, and opens the best match with the default application.

Includes a persistent file-index cache (JSON) so that subsequent
searches are instant.  The cache is rebuilt on first use or when the
user says "rebuild index".
"""

from __future__ import annotations
import json
import os
from pathlib import Path

from thefuzz import fuzz, process

from config import (
    SCAN_DIRECTORIES,
    SEARCHABLE_EXTENSIONS,
    FUZZY_MATCH_THRESHOLD,
    FUZZY_MAX_RESULTS,
    FILE_INDEX_CACHE_PATH,
)


# ─── Module-level cached index ──────────────────────────────────────────────
_file_index: dict[str, str] | None = None


def _build_file_index(force: bool = False) -> dict[str, str]:
    """
    Walk all SCAN_DIRECTORIES and return {display_name: full_path}.
    Uses a JSON cache file to avoid re-scanning on every call.

    Parameters
    ----------
    force : bool
        If True, re-scans the filesystem even if a cache exists.
    """
    global _file_index

    # Return in-memory cache if available (and not forced)
    if _file_index is not None and not force:
        return _file_index

    # Try loading from disk cache
    if not force and os.path.isfile(FILE_INDEX_CACHE_PATH):
        try:
            with open(FILE_INDEX_CACHE_PATH, "r", encoding="utf-8") as fh:
                _file_index = json.load(fh)
            print(f"  [FILE-SEARCH] Loaded {len(_file_index)} entries from cache")
            return _file_index
        except (json.JSONDecodeError, IOError):
            pass  # Corrupted cache — rebuild

    # Full scan
    print("  [FILE-SEARCH] Building file index (this may take a moment) …")
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

    # Persist to disk
    try:
        os.makedirs(os.path.dirname(FILE_INDEX_CACHE_PATH), exist_ok=True)
        with open(FILE_INDEX_CACHE_PATH, "w", encoding="utf-8") as fh:
            json.dump(index, fh, ensure_ascii=False)
        print(f"  [FILE-SEARCH] Cached {len(index)} entries → {FILE_INDEX_CACHE_PATH}")
    except IOError as e:
        print(f"  [WARN] Could not write cache: {e}")

    _file_index = index
    return _file_index


def rebuild_index() -> str:
    """Force-rebuild the file index from scratch."""
    idx = _build_file_index(force=True)
    return f"File index rebuilt: {len(idx)} files indexed."


def execute(file_query: str) -> str:
    """
    Search for *file_query* across indexed directories,
    open the best match, and return a user-friendly result string.
    """
    if not file_query:
        return "I didn't catch the file name. Could you repeat?"

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
