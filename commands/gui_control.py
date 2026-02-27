"""
Command: GUI Automation — Scroll & Media Control
==================================================
Uses PyAutoGUI virtual keypresses to interact with the active
window: scroll up/down, play/pause media, volume, next/prev track.
"""

from __future__ import annotations
import re
import pyautogui


# ─── Action mapping ──────────────────────────────────────────────────────────
_ACTIONS: dict[str, tuple[str, str]] = {
    # key: (pyautogui action, friendly description)
    "scroll_down":    ("pagedown",        "Scrolled down"),
    "scroll_up":      ("pageup",          "Scrolled up"),
    "play":           ("playpause",       "Toggled play/pause"),
    "pause":          ("playpause",       "Toggled play/pause"),
    "play_pause":     ("playpause",       "Toggled play/pause"),
    "next_track":     ("nexttrack",       "Skipped to next track"),
    "prev_track":     ("prevtrack",       "Went to previous track"),
    "volume_up":      ("volumeup",        "Volume up"),
    "volume_down":    ("volumedown",      "Volume down"),
    "mute":           ("volumemute",      "Toggled mute"),
    "fullscreen":     ("f11",             "Toggled fullscreen"),
    "escape":         ("escape",          "Pressed Escape"),
    "space":          ("space",           "Pressed Space"),
    "enter":          ("enter",           "Pressed Enter"),
}


def _detect_action(raw_text: str) -> str | None:
    """
    Parse the raw command to decide which GUI action to perform.
    Returns a key from _ACTIONS or None.
    """
    text = raw_text.lower()

    # Scroll
    if re.search(r"scroll\s*(down|below)", text):
        return "scroll_down"
    if re.search(r"scroll\s*(up|above)", text):
        return "scroll_up"

    # Media
    if re.search(r"(next|skip)\s*(track|song)", text):
        return "next_track"
    if re.search(r"(prev|previous|back)\s*(track|song)", text):
        return "prev_track"
    if re.search(r"play|resume", text) and "youtube" not in text:
        if "pause" in text:
            return "play_pause"
        return "play"
    if "pause" in text:
        return "pause"

    # Volume
    if re.search(r"volume\s*(up|increase|raise|louder)", text):
        return "volume_up"
    if re.search(r"volume\s*(down|decrease|lower|softer|quieter)", text):
        return "volume_down"
    if "mute" in text:
        return "mute"

    # Misc
    if "fullscreen" in text or "full screen" in text:
        return "fullscreen"
    if "escape" in text or "close" in text:
        return "escape"

    # Default: press space (useful for play on YouTube etc.)
    if "space" in text:
        return "space"

    return None


def execute(raw_text: str) -> str:
    """
    Detect the intended GUI action from *raw_text* and simulate
    the corresponding keypress.
    """
    action_key = _detect_action(raw_text)

    if action_key is None:
        return "I couldn't figure out which control to send. Try: scroll down, play, pause, volume up, mute, next track …"

    key, description = _ACTIONS[action_key]
    print(f"  [GUI] Sending keypress: {key}")
    pyautogui.press(key)

    return description + "."
