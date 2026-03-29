"""
Command: Open URL
==================
Opens a specific URL or website in the default browser.
Differs from web_search in that it navigates directly to a URL
rather than performing a Google search.

Examples:
  • "open youtube.com"
  • "go to github.com"
  • "visit stackoverflow.com"
"""

from __future__ import annotations
import re
import webbrowser


# ─── Pattern to extract URLs / domain-like strings ──────────────────────────
# Matches things like "youtube.com", "https://github.com/user/repo", etc.
_URL_PATTERN = re.compile(
    r"((?:https?://)?[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z]{2,})+(?:/[^\s]*)?)",
    re.IGNORECASE,
)

# Patterns to strip the leading verb
_VERB_STRIP = re.compile(
    r"(?:open|go\s+to|visit|navigate\s+to|browse\s+to|head\s+to|load)\s+",
    re.IGNORECASE,
)

# Common shorthand → full URL
_SHORTCUTS = {
    "youtube":       "https://www.youtube.com",
    "google":        "https://www.google.com",
    "github":        "https://github.com",
    "stackoverflow": "https://stackoverflow.com",
    "stack overflow": "https://stackoverflow.com",
    "gmail":         "https://mail.google.com",
    "twitter":       "https://twitter.com",
    "x":             "https://twitter.com",
    "reddit":        "https://www.reddit.com",
    "facebook":      "https://www.facebook.com",
    "instagram":     "https://www.instagram.com",
    "linkedin":      "https://www.linkedin.com",
    "whatsapp web":  "https://web.whatsapp.com",
    "netflix":       "https://www.netflix.com",
    "amazon":        "https://www.amazon.com",
    "wikipedia":     "https://www.wikipedia.org",
    "chatgpt":       "https://chat.openai.com",
    "notion":        "https://www.notion.so",
}


def _extract_url(raw_text: str) -> str | None:
    """Extract a URL or domain from the command."""
    # Strip leading verb
    text = _VERB_STRIP.sub("", raw_text).strip()

    # Check explicit URL pattern
    m = _URL_PATTERN.search(text)
    if m:
        url = m.group(1)
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url

    # Check shortcuts
    for shortcut, url in _SHORTCUTS.items():
        if shortcut in text.lower():
            return url

    return None


def execute(raw_text: str) -> str:
    """Extract a URL from the command and open it in the browser."""
    url = _extract_url(raw_text)

    if url is None:
        return (
            "I couldn't find a URL in your command.\n"
            "Try: \"open youtube.com\" or \"go to github.com\""
        )

    print(f"  [OPEN-URL] Opening: {url}")
    webbrowser.open(url)
    return f"Opening {url} in your browser."
