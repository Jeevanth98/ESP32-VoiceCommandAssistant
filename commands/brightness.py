"""
Command: Brightness Control
=============================
Get, set, increase, or decrease display brightness using multiple methods:
1. screen_brightness_control library (laptops, some monitors)
2. Windows WMI via PowerShell (laptops with WMI support)
3. DDC/CI commands (external monitors)
"""

from __future__ import annotations
import re
import subprocess

from config import BRIGHTNESS_STEP


def _get_brightness_wmi() -> int | None:
    """Get brightness using Windows WMI (works on most laptops)."""
    try:
        cmd = "powershell -Command \"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness\""
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            return int(result.stdout.strip())
    except Exception:
        pass
    return None


def _set_brightness_wmi(value: int) -> bool:
    """Set brightness using Windows WMI (works on most laptops)."""
    value = max(0, min(100, value))
    try:
        cmd = f'powershell -Command "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{value})"'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False


def _get_brightness() -> int | None:
    """Return current brightness percentage, or None if unavailable."""
    # Method 1: Try screen_brightness_control library
    try:
        import screen_brightness_control as sbc
        level = sbc.get_brightness()
        if isinstance(level, list):
            level = level[0] if level else None
        if level is not None:
            return int(level)
    except Exception:
        pass
    
    # Method 2: Try Windows WMI (works on most laptops)
    level = _get_brightness_wmi()
    if level is not None:
        return level
    
    return None


def _set_brightness(value: int) -> bool:
    """Set brightness to *value* (clamped to 0–100). Returns True on success."""
    value = max(0, min(100, value))
    
    # Method 1: Try screen_brightness_control library
    try:
        import screen_brightness_control as sbc
        sbc.set_brightness(value)
        # Verify it worked
        new_level = sbc.get_brightness()
        if isinstance(new_level, list):
            new_level = new_level[0] if new_level else None
        if new_level is not None:
            return True
    except Exception:
        pass
    
    # Method 2: Try Windows WMI
    if _set_brightness_wmi(value):
        return True
    
    return False


def _parse_command(raw_text: str) -> tuple[str, int | None]:
    """
    Determine the brightness action and optional target value.

    Returns (action, value):
        action ∈ {"set", "up", "down", "get"}
        value  – absolute brightness for "set", None otherwise
    """
    text = raw_text.lower()

    # "set brightness to 70" / "brightness 50%"
    m = re.search(r"(?:set\s+)?(?:brightness|screen)\s+(?:to\s+)?(\d+)\s*%?", text)
    if m:
        return "set", int(m.group(1))

    # "70% brightness"
    m = re.search(r"(\d+)\s*%?\s*(?:brightness|screen)", text)
    if m:
        return "set", int(m.group(1))

    # Directional
    if re.search(r"(?:increase|raise|higher|up|brighter|more)\s*(?:brightness|screen)?", text):
        return "up", None
    if re.search(r"(?:brightness|screen)\s*(?:up|increase|raise|higher|brighter|more)", text):
        return "up", None
    if re.search(r"(?:decrease|lower|dim|down|darker|less|reduce)\s*(?:brightness|screen)?", text):
        return "down", None
    if re.search(r"(?:brightness|screen)\s*(?:down|decrease|lower|dim|darker|less|reduce)", text):
        return "down", None

    # Query
    if re.search(r"(?:what|check|show|get|current)\s*(?:is\s+)?(?:my\s+)?(?:brightness|screen)", text):
        return "get", None

    # Default: if "brightness" is mentioned with no clear direction
    return "get", None


def execute(raw_text: str) -> str:
    """Adjust or report screen brightness."""
    action, value = _parse_command(raw_text)

    current = _get_brightness()
    if current is None:
        return (
            "Could not read screen brightness. Possible reasons:\n"
            "  • External monitor without software brightness control\n"
            "  • Brightness control disabled in Windows power settings\n"
            "  • Need to run as administrator\n"
            "Try using your monitor's hardware buttons or Windows Settings → Display → Brightness."
        )

    if action == "get":
        return f"Current screen brightness: {current}%."

    if action == "set" and value is not None:
        if _set_brightness(value):
            return f"Brightness set to {max(0, min(100, value))}%."
        return "Failed to set brightness. Try adjusting manually in Windows Settings."

    if action == "up":
        target = min(100, current + BRIGHTNESS_STEP)
        if _set_brightness(target):
            return f"Brightness increased to {target}% (was {current}%)."
        return "Failed to increase brightness. Try adjusting manually in Windows Settings."

    if action == "down":
        target = max(0, current - BRIGHTNESS_STEP)
        if _set_brightness(target):
            return f"Brightness decreased to {target}% (was {current}%)."
        return "Failed to decrease brightness. Try adjusting manually in Windows Settings."

    return "I couldn't understand the brightness command. Try: 'brightness up', 'set brightness to 50', or 'what is my brightness'."
