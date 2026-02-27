"""
Command: Content Mining — Search inside documents
===================================================
Iterates through every readable file in SCAN_DIRECTORIES, extracts
text via PyPDF2 / python-docx / plain read, and searches for a
keyword.  Reports file name, line number, and a context snippet.
"""

from __future__ import annotations
import os

from config import SCAN_DIRECTORIES, READABLE_EXTENSIONS
from utils.text_extraction import extract_text


def execute(keyword: str) -> str:
    """
    Search for *keyword* inside all readable documents.
    Returns a formatted result string with file, line, and context.
    """
    if not keyword:
        return "I didn't catch what to search for. Could you say it again?"

    keyword_lower = keyword.lower()
    hits: list[dict] = []

    print(f"  [CONTENT-MINE] Searching for \"{keyword}\" in documents …")

    for root_dir in SCAN_DIRECTORIES:
        if not os.path.isdir(root_dir):
            continue
        for dirpath, _, filenames in os.walk(root_dir):
            for fname in filenames:
                ext = os.path.splitext(fname)[1].lower()
                if ext not in READABLE_EXTENSIONS:
                    continue
                filepath = os.path.join(dirpath, fname)
                text = extract_text(filepath)
                if not text:
                    continue

                # Search line-by-line for the keyword
                for line_no, line in enumerate(text.splitlines(), start=1):
                    if keyword_lower in line.lower():
                        snippet = line.strip()
                        if len(snippet) > 120:
                            snippet = snippet[:120] + "…"
                        hits.append({
                            "file": fname,
                            "path": filepath,
                            "line": line_no,
                            "snippet": snippet,
                        })

    if not hits:
        return f"No documents contain \"{keyword}\"."

    # Build readable output
    lines = [f"Found \"{keyword}\" in {len(hits)} location(s):\n"]
    # Group by file for readability
    seen_files: dict[str, list] = {}
    for h in hits:
        seen_files.setdefault(h["file"], []).append(h)

    for fname, file_hits in seen_files.items():
        lines.append(f"  [{fname}]")
        for fh in file_hits[:5]:          # cap per-file hits at 5
            lines.append(f"    Line {fh['line']}: {fh['snippet']}")
        if len(file_hits) > 5:
            lines.append(f"    … and {len(file_hits) - 5} more matches")
        lines.append("")

    return "\n".join(lines)
