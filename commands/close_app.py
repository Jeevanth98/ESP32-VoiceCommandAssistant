"""
Command: Close Application
============================
Closes a running application by name.
Checks if the process is currently running, and if so terminates it.
Uses the same APP_REGISTRY from open_app to resolve friendly names
to process names, plus a dedicated PROCESS_MAP for cases where
the launch command differs from the actual process name.
"""

from __future__ import annotations
import re
import psutil

from commands.open_app import APP_REGISTRY, _normalise


# ─── Process-name overrides ─────────────────────────────────────────────────
# Some apps have a launch command that differs from the running process name.
# key = registry keyword, value = list of possible process names (without .exe)
PROCESS_MAP: dict[str, list[str]] = {
    "chrome":           ["chrome"],
    "google chrome":    ["chrome"],
    "brave":            ["brave"],
    "firefox":          ["firefox"],
    "edge":             ["msedge"],
    "microsoft edge":   ["msedge"],
    "opera":            ["opera"],
    "whatsapp":         ["WhatsApp"],
    "telegram":         ["Telegram"],
    "discord":          ["Discord", "Update"],       # Discord's main process
    "zoom":             ["Zoom"],
    "teams":            ["ms-teams", "Teams"],
    "microsoft teams":  ["ms-teams", "Teams"],
    "skype":            ["Skype"],
    "slack":            ["slack"],
    "word":             ["WINWORD"],
    "microsoft word":   ["WINWORD"],
    "excel":            ["EXCEL"],
    "microsoft excel":  ["EXCEL"],
    "powerpoint":       ["POWERPNT"],
    "microsoft powerpoint": ["POWERPNT"],
    "outlook":          ["OUTLOOK"],
    "onenote":          ["onenote", "ONENOTE"],
    "notepad":          ["notepad"],
    "notepad++":        ["notepad++"],
    "vs code":          ["Code"],
    "vscode":           ["Code"],
    "visual studio code": ["Code"],
    "visual studio":    ["devenv"],
    "sublime":          ["sublime_text"],
    "sublime text":     ["sublime_text"],
    "calculator":       ["Calculator", "calc"],
    "calc":             ["Calculator", "calc"],
    "paint":            ["mspaint"],
    "task manager":     ["Taskmgr"],
    "spotify":          ["Spotify"],
    "vlc":              ["vlc"],
    "obs":              ["obs64"],
    "obs studio":       ["obs64"],
    "postman":          ["Postman"],
    "docker":           ["Docker Desktop"],
    "steam":            ["steam"],
    "blender":          ["blender"],
    "figma":            ["Figma"],
    "notion":           ["Notion"],
    "pycharm":          ["pycharm64"],
    "intellij":         ["idea64"],
    "android studio":   ["studio64"],
    "arduino":          ["arduino"],
    "audacity":         ["audacity"],
    "gimp":             ["gimp-2.10"],
    "anydesk":          ["AnyDesk"],
    "teamviewer":       ["TeamViewer"],
}


# ─── Regex to extract app name from close command ────────────────────────────
_CLOSE_TRIGGER = re.compile(
    r"(?:close|quit|exit|kill|stop|terminate|end|shut\s*down|force\s*close)\s+"
    r"(?:the\s+|my\s+|a\s+)?(.+)",
    re.IGNORECASE,
)


def _get_process_names(app_key: str) -> list[str]:
    """
    Return a list of possible process names (without .exe) for a given
    app keyword.  Checks PROCESS_MAP first, then falls back to extracting
    the base executable from APP_REGISTRY's launch command.
    """
    # 1. Explicit process map
    if app_key in PROCESS_MAP:
        return PROCESS_MAP[app_key]

    # 2. Derive from APP_REGISTRY launch command
    entry = APP_REGISTRY.get(app_key)
    if entry:
        launch_cmd = entry[0]
        # For "explorer.exe shell:..." → not useful, skip
        if launch_cmd.startswith("explorer.exe"):
            # Try the UWP package name
            parts = launch_cmd.split("\\")
            if len(parts) > 1:
                # e.g. "5319275A.WhatsAppDesktop_..." → "WhatsApp"
                return [entry[1]]  # Use the friendly name as a fallback
            return []
        # For protocol URIs like "ms-settings:" → skip
        if ":" in launch_cmd and not launch_cmd.endswith(".msc"):
            return []
        # Strip path separators, take the base name
        base = launch_cmd.rsplit("\\", 1)[-1].rsplit("/", 1)[-1]
        return [base]

    return []


def _find_running_processes(process_names: list[str]) -> list[psutil.Process]:
    """
    Scan all running processes and return those whose name contains
    any of the given process_names (case-insensitive substring match).

    This handles cases where the real process name differs from the
    simple expected name, e.g.:
      • WhatsApp  → WhatsApp.Root.exe
      • brave     → brave.exe, BraveCrashHandler.exe
      • Discord   → Discord.exe, Update.exe
    """
    targets = [n.lower() for n in process_names]
    found: list[psutil.Process] = []

    for proc in psutil.process_iter(["pid", "name"]):
        try:
            pname = proc.info["name"] or ""
            pname_lower = pname.lower().removesuffix(".exe")

            for target in targets:
                # Exact match (e.g. "chrome" == "chrome")
                if pname_lower == target.lower():
                    found.append(proc)
                    break
                # Substring: process name starts with target
                # e.g. "whatsapp" in "whatsapp.root"
                if target.lower() in pname_lower:
                    found.append(proc)
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return found


def extract_app_name(raw_text: str) -> str:
    """Pull the application name from a close command."""
    m = _CLOSE_TRIGGER.search(raw_text)
    if m:
        return m.group(1).strip()
    return raw_text.strip()


def execute(raw_text: str) -> str:
    """
    Parse the app name from *raw_text*, check if it's running,
    and terminate it if found.
    """
    app_name = extract_app_name(raw_text)
    norm = _normalise(app_name)
    print(f"  [CLOSE-APP] Looking up \"{app_name}\" (normalised: \"{norm}\") …")

    # Resolve the app in the registry
    entry = APP_REGISTRY.get(norm)

    # Try relaxed match if exact fails
    if entry is None:
        for key, value in APP_REGISTRY.items():
            if key in norm or norm in key:
                entry = value
                norm = key
                break

    if entry is None:
        return (
            f"I don't recognise \"{app_name}\" as a known application. "
            f"Try saying the exact name (e.g. 'close Chrome', 'close WhatsApp')."
        )

    friendly_name = entry[1]
    process_names = _get_process_names(norm)

    if not process_names:
        return f"I don't know which process to look for when closing {friendly_name}."

    print(f"  [CLOSE-APP] Searching for processes: {process_names}")
    running = _find_running_processes(process_names)

    if not running:
        return f"{friendly_name} is not currently running."

    # Terminate all matching processes
    killed = 0
    for proc in running:
        try:
            print(f"  [CLOSE-APP] Terminating PID {proc.pid} ({proc.info['name']})")
            proc.terminate()
            killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"  [CLOSE-APP] Could not kill PID {proc.pid}: {e}")

    if killed == 0:
        return f"Found {friendly_name} running but couldn't close it (access denied). Try running as administrator."

    return f"Closed {friendly_name} ({killed} process{'es' if killed > 1 else ''} terminated)."
