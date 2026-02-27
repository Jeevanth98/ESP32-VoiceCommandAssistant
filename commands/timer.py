"""
Command: Timer — Background countdown with notification
========================================================
Uses the threading library to run a countdown in the background.
When the timer finishes, it prints a notification and (in the future)
sends a 'B' trigger back to the ESP32 to ring the physical buzzer.
"""

from __future__ import annotations
import re
import threading
import time
import winsound


# ─── Active timers registry ─────────────────────────────────────────────────
_active_timers: dict[str, threading.Thread] = {}


def _parse_duration(raw_text: str) -> int | None:
    """
    Extract the duration in seconds from user text.
    Supports: "10 minutes", "5 min", "30 seconds", "1 hour", "90 sec",
              "2 hours 30 minutes", etc.
    Returns total seconds or None if parsing fails.
    """
    text = raw_text.lower()
    total = 0
    found = False

    # Hours
    m = re.search(r"(\d+)\s*(?:hours?|hrs?)\b", text)
    if m:
        total += int(m.group(1)) * 3600
        found = True

    # Minutes
    m = re.search(r"(\d+)\s*(?:minutes?|mins?)\b", text)
    if m:
        total += int(m.group(1)) * 60
        found = True

    # Seconds
    m = re.search(r"(\d+)\s*(?:seconds?|secs?)\b", text)
    if m:
        total += int(m.group(1))
        found = True

    # Bare number with no unit → assume minutes
    if not found:
        m = re.search(r"(\d+)", text)
        if m:
            total = int(m.group(1)) * 60
            found = True

    return total if found and total > 0 else None


def _format_duration(seconds: int) -> str:
    """Human-readable duration string."""
    parts = []
    if seconds >= 3600:
        h = seconds // 3600
        parts.append(f"{h}h")
        seconds %= 3600
    if seconds >= 60:
        m = seconds // 60
        parts.append(f"{m}m")
        seconds %= 60
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    return " ".join(parts)


def _timer_worker(name: str, seconds: int):
    """Background thread that sleeps then beeps."""
    print(f"  [TIMER] ⏱ \"{name}\" started — {_format_duration(seconds)}")
    time.sleep(seconds)
    print(f"\n  [TIMER] 🔔 Timer \"{name}\" is done!")

    # Audible alert (Windows system beep)
    try:
        for _ in range(3):
            winsound.Beep(1000, 500)  # 1kHz for 500ms
            time.sleep(0.2)
    except Exception:
        pass  # winsound may fail on non-Windows or no speaker

    # Future: send "B" over serial to ESP32 to ring the buzzer
    # serial_conn.write(b"B")

    _active_timers.pop(name, None)


def execute(raw_text: str) -> str:
    """
    Parse the timer duration from *raw_text*, start a background
    countdown thread, and return a confirmation.
    """
    seconds = _parse_duration(raw_text)

    if seconds is None:
        return (
            "I couldn't figure out the duration. "
            "Try something like: \"Set a 10 minute timer\" or \"Timer 30 seconds\"."
        )

    name = f"timer_{len(_active_timers) + 1}"
    duration_str = _format_duration(seconds)

    t = threading.Thread(target=_timer_worker, args=(name, seconds), daemon=True)
    _active_timers[name] = t
    t.start()

    return f"Timer set for {duration_str}. I'll beep when it's done."
