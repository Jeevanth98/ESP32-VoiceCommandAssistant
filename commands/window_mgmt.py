"""
Command: Window Management
============================
Simulates Windows keyboard shortcuts to manage application windows:
minimize, maximize, snap left/right, show desktop.
"""

from __future__ import annotations
import re
import pyautogui


# ─── Action mapping ──────────────────────────────────────────────────────────
_ACTIONS: dict[str, tuple[list[str], str]] = {
    # key: (hotkey_sequence, description)
    "minimize_all":  (["win", "d"],    "Toggled show desktop (minimized all windows)"),
    "minimize":      (["win", "down"], "Minimized the current window"),
    "maximize":      (["win", "up"],   "Maximized the current window"),
    "snap_left":     (["win", "left"], "Snapped window to the left"),
    "snap_right":    (["win", "right"],  "Snapped window to the right"),
    "close_window":  (["alt", "F4"],   "Closed the current window"),
    "switch_window": (["alt", "tab"],  "Switched to the next window"),
    "new_desktop":   (["win", "ctrl", "d"],   "Created a new virtual desktop"),
    "close_desktop": (["win", "ctrl", "F4"],  "Closed the current virtual desktop"),
    "task_view":     (["win", "tab"],  "Opened Task View"),
}


def _detect_action(raw_text: str) -> str | None:
    """Parse the window management action from raw text."""
    text = raw_text.lower()

    # Show desktop / minimize all
    if re.search(r"show\s+desktop|minimize\s+all|minimise\s+all|desktop", text):
        return "minimize_all"

    # Snap
    if re.search(r"snap\s+(?:to\s+)?(?:the\s+)?left|(?:move|window)\s+(?:to\s+)?(?:the\s+)?left", text):
        return "snap_left"
    if re.search(r"snap\s+(?:to\s+)?(?:the\s+)?right|(?:move|window)\s+(?:to\s+)?(?:the\s+)?right", text):
        return "snap_right"

    # Maximize
    if re.search(r"maximi[sz]e", text):
        return "maximize"

    # Minimize (single window — must come after minimize_all check)
    if re.search(r"minimi[sz]e", text):
        return "minimize"

    # Close window
    if re.search(r"close\s+(?:this\s+)?window|alt\s+f4", text):
        return "close_window"

    # Switch window
    if re.search(r"switch\s+window|next\s+window|alt\s+tab", text):
        return "switch_window"

    # Virtual desktops
    if re.search(r"new\s+(?:virtual\s+)?desktop", text):
        return "new_desktop"
    if re.search(r"close\s+(?:virtual\s+)?desktop", text):
        return "close_desktop"

    # Task view
    if re.search(r"task\s+view|all\s+windows|show\s+(?:all\s+)?windows", text):
        return "task_view"

    return None


def execute(raw_text: str) -> str:
    """Detect the window action and simulate the hotkey."""
    action_key = _detect_action(raw_text)

    if action_key is None:
        return (
            "I couldn't figure out the window action. Try:\n"
            "  • minimize / maximize\n"
            "  • snap left / snap right\n"
            "  • show desktop / minimize all\n"
            "  • switch window / task view"
        )

    keys, description = _ACTIONS[action_key]
    print(f"  [WINDOW] Sending hotkey: {' + '.join(keys)}")
    pyautogui.hotkey(*keys)

    return description + "."
