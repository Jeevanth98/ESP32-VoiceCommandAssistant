"""
Entity Extractor — Extract targets from user commands
======================================================
Pulls out the relevant *operand* for each intent:
  • file_search    → filename / description to search for
  • content_search → keyword(s) + optional target directory hint
  • active_typing  → the text the user wants typed

Uses simple regex + heuristic patterns (no heavy NER model needed
for the structured commands we support).
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from nlu.preprocessor import tokenize_raw


@dataclass
class Entities:
    """Container for extracted entities."""
    file_query: str = ""          # e.g. "physics pdf"
    search_keyword: str = ""      # e.g. "quantum"
    typing_text: str = ""         # e.g. "Meeting notes for today"
    summarize_query: str = ""     # e.g. "physics notes"
    timer_text: str = ""          # e.g. "10 minutes"
    raw: str = ""                 # original command (unmodified)


# ─── Pattern banks ───────────────────────────────────────────────────────────

# Patterns that signal "everything after this is the file to find"
_FILE_TRIGGERS = re.compile(
    r"(?:open|find|search\s+for|look\s+for|locate|launch|show)\s+(?:my\s+|the\s+|a\s+)?(.+)",
    re.IGNORECASE,
)

# Patterns for content mining: "search for X in my notes"
_CONTENT_TRIGGERS = re.compile(
    r"(?:search|find|look)\s+(?:for\s+)?(.+?)\s+(?:in|inside|within|from)\s+(?:my\s+)?(?:notes?|files?|documents?|folder|directory|pdf|docx)",
    re.IGNORECASE,
)

# Alternate content pattern: "search X in my files"
_CONTENT_TRIGGERS_ALT = re.compile(
    r"(?:search|find|look)\s+(?:for\s+)?(.+?)$",
    re.IGNORECASE,
)

# Patterns for active typing
_TYPING_TRIGGERS = re.compile(
    r"(?:write\s+(?:this\s+)?(?:down)?|type\s+(?:this)?|note\s+(?:this\s+)?(?:down)?)\s*:?\s*(.+)",
    re.IGNORECASE,
)

# Patterns for summarization: "summarize my physics pdf"
_SUMMARIZE_TRIGGERS = re.compile(
    r"(?:summarize|summary\s+of|give\s+(?:me\s+)?(?:a\s+)?summary\s+of|brief|tldr)\s+(?:my\s+|the\s+|a\s+)?(.+)",
    re.IGNORECASE,
)

# Patterns for timer: "set a 10 minute timer"
_TIMER_TRIGGERS = re.compile(
    r"(?:set|start|begin|create)\s+(?:a\s+)?(.+?)\s*(?:timer|alarm|countdown)",
    re.IGNORECASE,
)
_TIMER_TRIGGERS_ALT = re.compile(
    r"(?:timer|alarm|countdown)\s+(?:for\s+|of\s+)?(.+)",
    re.IGNORECASE,
)


def extract(raw_text: str, intent: str | None) -> Entities:
    """
    Given the *original* (un-preprocessed) user command and the classified
    intent, pull out the relevant entities.
    """
    ent = Entities(raw=raw_text)
    text = raw_text.strip()

    if intent == "file_search":
        m = _FILE_TRIGGERS.search(text)
        if m:
            ent.file_query = m.group(1).strip()
        else:
            # fallback: use everything after the first verb
            ent.file_query = text

    elif intent == "content_search":
        m = _CONTENT_TRIGGERS.search(text)
        if m:
            ent.search_keyword = m.group(1).strip()
        else:
            # Try alternate simpler pattern
            m = _CONTENT_TRIGGERS_ALT.search(text)
            if m:
                ent.search_keyword = m.group(1).strip()
            else:
                ent.search_keyword = text

    elif intent == "active_typing":
        m = _TYPING_TRIGGERS.search(text)
        if m:
            ent.typing_text = m.group(1).strip()
        else:
            # If no trigger matched, treat everything as the text to type
            ent.typing_text = text

    elif intent == "summarize":
        m = _SUMMARIZE_TRIGGERS.search(text)
        if m:
            ent.summarize_query = m.group(1).strip()
        else:
            ent.summarize_query = text

    elif intent == "timer":
        m = _TIMER_TRIGGERS.search(text)
        if m:
            ent.timer_text = m.group(1).strip()
        else:
            m = _TIMER_TRIGGERS_ALT.search(text)
            if m:
                ent.timer_text = m.group(1).strip()
            else:
                ent.timer_text = text

    # screenshot, gui_control, system_info → no entity needed, raw text is enough

    return ent
