"""
Command: Vision Capture — Take a screenshot
=============================================
Uses pyautogui.screenshot() to capture the current screen,
timestamps the file, and saves it to the captures/ folder.
"""

from __future__ import annotations
import os
from datetime import datetime

import pyautogui

from config import CAPTURES_DIR


def execute() -> str:
    """Take a screenshot and save it with a timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    filepath = os.path.join(CAPTURES_DIR, filename)

    print(f"  [SCREENSHOT] Capturing screen …")
    img = pyautogui.screenshot()
    img.save(filepath)
    print(f"  [SCREENSHOT] Saved to {filepath}")

    return f"Screenshot saved: {filepath}"
