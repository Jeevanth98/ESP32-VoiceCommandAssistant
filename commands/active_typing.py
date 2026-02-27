"""
Command: Active Typing — Open Notepad and simulate typing
==========================================================
Opens Notepad via the OS, waits for the window to focus,
then uses PyAutoGUI to simulate human typing.

Demonstrates Process Synchronization between the OS shell
and a GUI automation library.
"""

from __future__ import annotations
import os
import time
import subprocess

import pyautogui
import pyperclip

from config import TYPING_INTERVAL, NOTEPAD_WAIT


def execute(text: str) -> str:
    """
    Open Notepad and type *text* into it.
    Returns a status message.
    """
    if not text:
        return "I didn't catch what to type. Could you repeat?"

    print(f"  [TYPING] Opening Notepad …")

    # Launch Notepad as a non-blocking subprocess
    subprocess.Popen(["notepad.exe"])
    time.sleep(NOTEPAD_WAIT)  # wait for the window to appear & get focus

    # Click the Notepad editing area to ensure focus
    time.sleep(0.5)
    pyautogui.click()
    time.sleep(0.3)

    print(f"  [TYPING] Typing {len(text)} characters …")

    # Use clipboard paste — handles all characters (unicode, special chars)
    # and is much faster than simulating individual keypresses
    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.3)

    return f"Typed {len(text)} characters into Notepad."
