"""
Command: Active Typing — Open Notepad and simulate typing
==========================================================
Opens Notepad via the OS, waits for the window to focus,
then uses clipboard paste to insert text.

**Append mode**: If Notepad is already open from a previous command,
the new text is appended below the previous content (Ctrl+End → Enter)
instead of opening a new window.
"""

from __future__ import annotations
import os
import time
import subprocess
import ctypes
import ctypes.wintypes

import pyautogui
import pyperclip

from config import NOTEPAD_WAIT

# ─── Win32 helpers for reliable window focus ─────────────────────────────────

def _find_notepad_window():
    """Find an existing Notepad window handle.
    Tries both Windows 11 'NotepadW' and classic 'Notepad' class names.
    Returns the first match or None.
    """
    FindWindow = ctypes.windll.user32.FindWindowW
    for cls in ("NotepadW", "Notepad"):
        hwnd = FindWindow(cls, None)
        if hwnd:
            return hwnd
    return None


def _focus_window(hwnd) -> bool:
    """Bring a window to the foreground and give it focus."""
    if not hwnd:
        return False
    user32 = ctypes.windll.user32
    SW_RESTORE = 9
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, SW_RESTORE)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.3)
    return True


def execute(text: str) -> str:
    """
    Open Notepad (or focus an existing window) and type *text* into it.
    If Notepad is already open, appends below the previous content.
    Returns a status message.
    """
    if not text:
        return "I didn't catch what to type. Could you repeat?"

    # ── Check for an existing Notepad window ────────────────────────────
    hwnd = _find_notepad_window()
    is_existing = hwnd is not None

    if is_existing:
        print("  [TYPING] Found existing Notepad window — appending …")
        _focus_window(hwnd)
    else:
        print("  [TYPING] No Notepad window found — opening a new one …")
        subprocess.Popen(["notepad.exe"])
        time.sleep(NOTEPAD_WAIT)

        hwnd = _find_notepad_window()
        if hwnd:
            _focus_window(hwnd)
            print("  [TYPING] Focused new Notepad window via Win32")
        else:
            # Fallback: Alt-Tab to switch to the most recent window
            print("  [TYPING] Window handle not found — using Alt+Tab fallback")
            pyautogui.hotkey("alt", "tab")
            time.sleep(0.5)

    # ── Click inside the editing area to ensure cursor is active ─────────
    time.sleep(0.3)
    pyautogui.click(pyautogui.size()[0] // 2, pyautogui.size()[1] // 2)
    time.sleep(0.3)

    # ── If appending, move to end of existing text and add a newline ─────
    if is_existing:
        pyautogui.hotkey("ctrl", "End")     # Jump to the very end
        time.sleep(0.1)
        pyautogui.press("enter")             # New line
        time.sleep(0.1)

    print(f"  [TYPING] Pasting {len(text)} characters …")

    # Use clipboard paste — handles unicode, special chars, and is fast
    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.3)

    action = "Appended" if is_existing else "Typed"
    return f"{action} {len(text)} characters into Notepad."
