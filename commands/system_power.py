"""
Command: System Power — Lock, Shutdown, Restart, Sleep
=======================================================
Controls Windows power state with a typed y/n confirmation
before destructive operations.
"""

from __future__ import annotations
import os
import re
import subprocess

from config import SHUTDOWN_GRACE_PERIOD


def _detect_action(raw_text: str) -> str | None:
    """Parse the power action from the raw command."""
    text = raw_text.lower()

    if re.search(r"\block\b", text):
        return "lock"
    if re.search(r"\bshut\s*down\b|\bpower\s*off\b|\bturn\s*off\b", text):
        return "shutdown"
    if re.search(r"\brestart\b|\breboot\b", text):
        return "restart"
    if re.search(r"\bsleep\b|\bhibernate\b|\bstandby\b|\bsuspend\b", text):
        return "sleep"
    if re.search(r"\blog\s*off\b|\bsign\s*out\b", text):
        return "logoff"

    return None


def execute(raw_text: str) -> str:
    """
    Detect the power action and execute it.
    Destructive actions (shutdown, restart, sleep, logoff) require
    y/n typed confirmation.
    """
    action = _detect_action(raw_text)

    if action is None:
        return (
            "I couldn't figure out what power action you want.\n"
            "Try: lock screen, shutdown, restart, sleep, or log off."
        )

    # ── Lock — no confirmation needed ────────────────────────────────────
    if action == "lock":
        print("  [POWER] Locking screen …")
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=False)
        return "Screen locked."

    # ── Destructive actions — ask for confirmation ───────────────────────
    action_labels = {
        "shutdown": "SHUT DOWN",
        "restart":  "RESTART",
        "sleep":    "put to SLEEP",
        "logoff":   "LOG OFF",
    }
    label = action_labels.get(action, action.upper())

    print(f"\n  ⚠️  Are you sure you want to {label} this computer?")
    try:
        confirm = input("  Type 'y' to confirm, anything else to cancel: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return "Cancelled."

    if confirm != "y":
        return f"{action.capitalize()} cancelled."

    if action == "shutdown":
        print(f"  [POWER] Shutting down in {SHUTDOWN_GRACE_PERIOD} seconds …")
        subprocess.run(
            ["shutdown", "/s", "/t", str(SHUTDOWN_GRACE_PERIOD)],
            check=False,
        )
        return f"Shutting down in {SHUTDOWN_GRACE_PERIOD} seconds."

    elif action == "restart":
        print(f"  [POWER] Restarting in {SHUTDOWN_GRACE_PERIOD} seconds …")
        subprocess.run(
            ["shutdown", "/r", "/t", str(SHUTDOWN_GRACE_PERIOD)],
            check=False,
        )
        return f"Restarting in {SHUTDOWN_GRACE_PERIOD} seconds."

    elif action == "sleep":
        print("  [POWER] Entering sleep mode …")
        subprocess.run(
            ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
            check=False,
        )
        return "Entering sleep mode."

    elif action == "logoff":
        print("  [POWER] Logging off …")
        subprocess.run(["shutdown", "/l"], check=False)
        return "Logging off."

    return "Unknown power action."
