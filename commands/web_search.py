"""
Command: Web Search
====================
Opens the default browser and performs a Google search for the
user's query.  Supports phrasing like:
  • "search what is a lion"
  • "Google how to make pasta"
  • "look up Python list comprehension"
"""

from __future__ import annotations
import re
import webbrowser
import urllib.parse


# ─── Regex to strip the leading verb / filler ────────────────────────────────
_QUERY_TRIGGER = re.compile(
    r"(?:search|google|look\s+up|what\s+is|what\s+are|who\s+is|who\s+are|"
    r"how\s+to|how\s+do|tell\s+me\s+about|find\s+out|search\s+for|"
    r"search\s+about|look\s+for|define|meaning\s+of)\s*"
    r"(?:for\s+|about\s+|on\s+)?(.+)",
    re.IGNORECASE,
)


def extract_query(raw_text: str) -> str:
    """Pull the search query from the raw command."""
    m = _QUERY_TRIGGER.search(raw_text)
    if m:
        return m.group(1).strip().rstrip("?.")
    return raw_text.strip()


def execute(raw_text: str) -> str:
    """
    Extract a search query from *raw_text* and open it in the
    default browser via Google.
    """
    query = extract_query(raw_text)
    if not query:
        return "I didn't catch what to search for.  Could you say it again?"

    url = f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}"
    print(f"  [WEB-SEARCH] Query: \"{query}\"")
    print(f"  [WEB-SEARCH] URL  : {url}")

    webbrowser.open(url)
    return f"Searching the web for \"{query}\"."
