"""
ESP32 Voice Command Assistant — Main Entry Point
==================================================
Terminal-based input loop for MVP testing (no hardware required).

Pipeline per command:
  1. Read raw text from terminal (simulates Whisper transcription)
  2. Pre-process with NLTK (stop-word removal + lemmatization)
  3. Classify intent with TF-IDF + LinearSVC supervised classifier
  4. Extract entities (file name / keyword / text)
  5. Dispatch to the appropriate command handler

Serial mode (--serial):
  Listens on the configured COM port for raw audio from the ESP32,
  transcribes with Whisper, then runs the same NLU pipeline.
"""

from __future__ import annotations
import sys
import argparse

# ─── NLU imports ─────────────────────────────────────────────────────────────
from nlu.preprocessor import preprocess
from nlu.intent_classifier import classify_intent
from nlu.entity_extractor import extract, Entities

# ─── Command imports ─────────────────────────────────────────────────────────
from commands import file_search, content_mining, active_typing
from commands import summarize, screenshot, gui_control, system_info, timer
from commands import open_app, web_search, close_app
from commands import create_file, system_power, brightness, window_mgmt, open_url

import re

# ─── Keyword-based fast override for short/ambiguous commands ────────────────
_KEYWORD_OVERRIDES = [
    (re.compile(r"\b(write\s+(this\s+)?(down)?|type\s+(this)?|note\s+(this\s+)?(down)?)\s*:?\s*", re.I), "active_typing"),
    (re.compile(r"\b(scroll\s*(up|down)|page\s*(up|down))\b", re.I), "gui_control"),
    (re.compile(r"\b(play|pause|resume|next\s*track|prev\s*track|volume\s*(up|down)|mute|fullscreen)\b", re.I), "gui_control"),
    (re.compile(r"\b(screenshot|screen\s*capture|capture\s*screen|screen\s*shot)\b", re.I), "screenshot"),
    (re.compile(r"\b(timer|countdown|alarm)\b", re.I), "timer"),
    # New: file creation
    (re.compile(r"\b(create|make|new)\s+(?:a\s+)?\w+\s+file\b", re.I), "create_file"),
    (re.compile(r"\b(create|make|new)\s+\S+\.\w+\s+", re.I), "create_file"),
    # New: system power
    (re.compile(r"\block\s+(the\s+)?screen\b|\block\s+(my\s+)?(computer|pc)\b", re.I), "system_power"),
    (re.compile(r"\b(shut\s*down|shutdown|power\s*off|turn\s*off)\s*(the\s+)?(computer|pc|system)?\b", re.I), "system_power"),
    (re.compile(r"\b(restart|reboot)\s*(the\s+)?(computer|pc|system)?\b", re.I), "system_power"),
    (re.compile(r"\b(sleep|hibernate|suspend|standby)\s*(mode)?\b", re.I), "system_power"),
    (re.compile(r"\b(log\s*off|log\s*out|sign\s*out)\b", re.I), "system_power"),
    # New: brightness
    (re.compile(r"\bbright(ness)?\b", re.I), "brightness"),
    (re.compile(r"\bdim(mer)?\b", re.I), "brightness"),
    # New: window management
    (re.compile(r"\b(minimize|minimise|maximize|maximise)\s+(this\s+|the\s+|all\s+)?window", re.I), "window_mgmt"),
    (re.compile(r"\bsnap\s+(to\s+)?(the\s+)?(left|right)\b", re.I), "window_mgmt"),
    (re.compile(r"\bshow\s+(the\s+)?desktop\b", re.I), "window_mgmt"),
    (re.compile(r"\bminimize\s+all\b|\bminimise\s+all\b", re.I), "window_mgmt"),
    (re.compile(r"\btask\s+view\b", re.I), "window_mgmt"),
    # New: open URL (domain patterns like "open youtube.com")
    (re.compile(r"\b(open|go\s+to|visit|navigate\s+to|browse\s+to)\s+\S+\.\w{2,}", re.I), "open_url"),
    # Existing: open/close app, web search (keep at end for priority)
    (re.compile(r"\b(open|launch|start|run|fire\s+up|boot\s+up)\s+", re.I), "open_app"),
    (re.compile(r"\b(close|quit|exit|kill|stop|terminate|end|shut\s*down|force\s*close)\s+", re.I), "close_app"),
    # Web search: matches both "search vit" and "search what is vit"
    (re.compile(r"\b(search|google|look\s+up|what\s+is|who\s+is|how\s+to|tell\s+me\s+about|define\b|meaning\s+of)\b", re.I), "web_search"),
]


def _keyword_override(raw_text: str) -> str | None:
    """Check if the command matches a fast keyword pattern — bypasses the NLU model."""
    for pattern, intent in _KEYWORD_OVERRIDES:
        if pattern.search(raw_text):
            return intent
    return None


# ─── Command dispatcher ─────────────────────────────────────────────────────
COMMAND_MAP = {
    "file_search":    lambda ent: file_search.execute(ent.file_query),
    "content_search": lambda ent: content_mining.execute(ent.search_keyword),
    "active_typing":  lambda ent: active_typing.execute(ent.typing_text),
    "summarize":      lambda ent: summarize.execute(ent.summarize_query),
    "screenshot":     lambda ent: screenshot.execute(),
    "gui_control":    lambda ent: gui_control.execute(ent.raw),
    "system_info":    lambda ent: system_info.execute(ent.raw),
    "timer":          lambda ent: timer.execute(ent.timer_text or ent.raw),
    "open_app":       lambda ent: open_app.execute(ent.raw),
    "close_app":      lambda ent: close_app.execute(ent.raw),
    "web_search":     lambda ent: web_search.execute(ent.raw),
    # New commands
    "create_file":    lambda ent: create_file.execute(ent.raw),
    "system_power":   lambda ent: system_power.execute(ent.raw),
    "brightness":     lambda ent: brightness.execute(ent.raw),
    "window_mgmt":    lambda ent: window_mgmt.execute(ent.raw),
    "open_url":       lambda ent: open_url.execute(ent.raw),
}


def handle_command(raw_text: str) -> str:
    """Run the full NLU pipeline and execute the matched command."""

    # Step 0 — Keyword override for short/ambiguous GUI commands
    override = _keyword_override(raw_text)
    if override:
        print(f"  [FAST]   Keyword override → {override}")
        entities = extract(raw_text, override)
        handler = COMMAND_MAP.get(override)
        return handler(entities)

    # Step 1 — Pre-process
    cleaned = preprocess(raw_text)
    print(f"  [PRE]    Cleaned text : \"{cleaned}\"")

    # Step 2 — Classify intent
    intent, confidence = classify_intent(cleaned)
    print(f"  [NLU]    Intent: {intent}  |  Confidence: {confidence:.2%}")

    if intent is None:
        return (
            f"I'm not confident enough about what you want "
            f"(best score: {confidence:.0%}).  Could you rephrase?"
        )

    # Step 3 — Extract entities from the ORIGINAL text (not the cleaned one)
    entities: Entities = extract(raw_text, intent)
    print(f"  [ENTITY] {entities}")

    # Step 4 — Dispatch
    handler = COMMAND_MAP.get(intent)
    if handler is None:
        return f"Intent \"{intent}\" recognised but no handler is implemented yet."

    return handler(entities)


# ─── Interactive loop ────────────────────────────────────────────────────────

BANNER = r"""
╔══════════════════════════════════════════════════════════════════╗
║    ESP32 Voice Command Assistant  —  Phase 2 (Text Mode)        ║
║─────────────────────────────────────────────────────────────────-║
║  Type a natural-language command and press Enter.                ║
║  Examples:                                                       ║
║    • Open my physics PDF            (file search)                ║
║    • Search for quantum in my notes (content mining)             ║
║    • Write this down: Meeting at 3  (active typing)              ║
║    • Summarize my physics notes     (AI summarization)           ║
║    • Take a screenshot              (vision capture)             ║
║    • Scroll down / Play / Pause     (GUI control)                ║
║    • Open WhatsApp / Launch Chrome  (open application)           ║
║    • Close Chrome / Quit Notepad    (close application)          ║
║    • Search what is a lion          (web search)                 ║
║    • What's my CPU usage?           (system info)                ║
║    • Set a 10 minute timer          (background timer)           ║
║    • Create a python file called    (create file)                ║
║      notes in Desktop                                            ║
║    • Lock the screen / Shutdown     (system power)               ║
║    • Brightness up / Set to 70%     (brightness control)         ║
║    • Minimize all / Snap left       (window management)          ║
║    • Open youtube.com               (open URL)                   ║
║  Type 'quit' or 'exit' to stop.                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""


def _run_text_mode():
    """Interactive text-input loop (default mode)."""
    print(BANNER)

    # Pre-load the NLU model so first command isn't slow
    print("[INIT] Warming up NLU model …")
    try:
        classify_intent("hello")  # dummy call to trigger model load
    except Exception as e:
        print(f"[ERR] Failed to load NLU model: {e}")
        sys.exit(1)
    print("[INIT] Ready!\n")

    while True:
        try:
            raw = input("🎤 You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not raw:
            continue
        if raw.lower() in {"quit", "exit", "q"}:
            print("Goodbye!")
            break

        # Special meta-commands
        if raw.lower() in {"rebuild index", "rebuild file index", "refresh index"}:
            print(file_search.rebuild_index())
            continue

        print(f"  [RAW]    \"{raw}\"")
        result = handle_command(raw)
        print(f"\n🤖 Assistant > {result}\n")


def _run_serial_mode():
    """ESP32 serial mode — listen on COM port for audio, transcribe with Whisper."""
    print("[SERIAL] Starting serial listener …")

    try:
        from serial_listener import start_serial_listener
        start_serial_listener(handle_command)
    except ImportError:
        print("[ERR] serial_listener module not found. Make sure serial_listener.py exists.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERR] Serial listener failed: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="ESP32 Voice Command Assistant")
    parser.add_argument(
        "--serial", action="store_true",
        help="Start in serial mode (listen on COM port for ESP32 audio)",
    )
    args = parser.parse_args()

    if args.serial:
        _run_serial_mode()
    else:
        _run_text_mode()


if __name__ == "__main__":
    main()
