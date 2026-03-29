"""
Command: Open Application
==========================
Opens desktop or Windows Store applications by name.
Uses a keyword map to resolve friendly names to executable paths or
Windows protocol URIs.
"""

from __future__ import annotations
import os
import re
import subprocess


# ─── Application registry ───────────────────────────────────────────────────
# Each entry: "keyword" → (launch_command, friendly_name)
#   • For Store / UWP apps use the "shell:AppsFolder\\..." URI or protocol URI.
#   • For classic desktop apps use the executable name (must be on PATH) or full path.

APP_REGISTRY: dict[str, tuple[str, str]] = {
    # ── Browsers ──────────────────────────────────────────────────────────
    "chrome":           ("start chrome",                             "Google Chrome"),
    "google chrome":    ("start chrome",                             "Google Chrome"),
    "brave":            ("start brave",                              "Brave Browser"),
    "firefox":          ("start firefox",                            "Mozilla Firefox"),
    "edge":             ("start msedge",                             "Microsoft Edge"),
    "microsoft edge":   ("start msedge",                             "Microsoft Edge"),
    "opera":            ("start opera",                              "Opera"),

    # ── Communication ─────────────────────────────────────────────────────
    "whatsapp":         ("explorer.exe shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",  "WhatsApp"),
    "telegram":         ("start telegram",                           "Telegram"),
    "discord":          ("start discord",                            "Discord"),
    "zoom":             ("start zoom",                               "Zoom"),
    "teams":            ("explorer.exe shell:AppsFolder\\MicrosoftTeams_8wekyb3d8bbwe!MicrosoftTeams", "Microsoft Teams"),
    "microsoft teams":  ("explorer.exe shell:AppsFolder\\MicrosoftTeams_8wekyb3d8bbwe!MicrosoftTeams", "Microsoft Teams"),
    "skype":            ("start skype",                              "Skype"),
    "slack":            ("start slack",                              "Slack"),

    # ── Microsoft Office ──────────────────────────────────────────────────
    "word":             ("winword",                                 "Microsoft Word"),
    "microsoft word":   ("winword",                                 "Microsoft Word"),
    "excel":            ("excel",                                   "Microsoft Excel"),
    "microsoft excel":  ("excel",                                   "Microsoft Excel"),
    "powerpoint":       ("powerpnt",                                "Microsoft PowerPoint"),
    "microsoft powerpoint": ("powerpnt",                            "Microsoft PowerPoint"),
    "outlook":          ("outlook",                                 "Microsoft Outlook"),
    "onenote":          ("onenote",                                 "Microsoft OneNote"),
    "access":           ("msaccess",                                "Microsoft Access"),

    # ── Productivity / Editors ────────────────────────────────────────────
    "notepad":          ("notepad",                                 "Notepad"),
    "notepad++":        ("notepad++",                               "Notepad++"),
    "wordpad":          ("wordpad",                                 "WordPad"),
    "vs code":          ("code",                                    "Visual Studio Code"),
    "vscode":           ("code",                                    "Visual Studio Code"),
    "visual studio code": ("code",                                  "Visual Studio Code"),
    "visual studio":    ("devenv",                                  "Visual Studio"),
    "sublime":          ("subl",                                    "Sublime Text"),
    "sublime text":     ("subl",                                    "Sublime Text"),
    "atom":             ("atom",                                    "Atom"),

    # ── System / Utilities ────────────────────────────────────────────────
    "calculator":       ("calc",                                    "Calculator"),
    "calc":             ("calc",                                    "Calculator"),
    "paint":            ("mspaint",                                 "Paint"),
    "snipping tool":    ("snippingtool",                            "Snipping Tool"),
    "task manager":     ("taskmgr",                                 "Task Manager"),
    "control panel":    ("control",                                 "Control Panel"),
    "settings":         ("ms-settings:",                            "Windows Settings"),
    "file explorer":    ("explorer",                                "File Explorer"),
    "explorer":         ("explorer",                                "File Explorer"),
    "command prompt":   ("cmd",                                     "Command Prompt"),
    "cmd":              ("cmd",                                     "Command Prompt"),
    "powershell":       ("powershell",                              "PowerShell"),
    "terminal":         ("wt",                                      "Windows Terminal"),
    "windows terminal": ("wt",                                      "Windows Terminal"),
    "registry editor":  ("regedit",                                 "Registry Editor"),
    "device manager":   ("devmgmt.msc",                             "Device Manager"),
    "disk management":  ("diskmgmt.msc",                            "Disk Management"),

    # ── Media & Entertainment ─────────────────────────────────────────────
    "spotify":          ("start spotify",                            "Spotify"),
    "vlc":              ("start vlc",                                "VLC Media Player"),
    "media player":     ("wmplayer",                                "Windows Media Player"),
    "movies & tv":      ("explorer.exe shell:AppsFolder\\Microsoft.ZuneVideo_8wekyb3d8bbwe!Microsoft.ZuneVideo", "Movies & TV"),
    "photos":           ("explorer.exe shell:AppsFolder\\Microsoft.Windows.Photos_8wekyb3d8bbwe!App", "Photos"),
    "camera":           ("explorer.exe shell:AppsFolder\\Microsoft.WindowsCamera_8wekyb3d8bbwe!App",  "Camera"),
    "xbox":             ("explorer.exe shell:AppsFolder\\Microsoft.XboxApp_8wekyb3d8bbwe!Microsoft.XboxApp", "Xbox"),

    # ── Social Media ──────────────────────────────────────────────────────
    "instagram":        ("explorer.exe shell:AppsFolder\\Facebook.InstagramBeta_8xx8rvfyw5nnt!App",   "Instagram"),
    "facebook":         ("explorer.exe https://www.facebook.com",   "Facebook"),
    "twitter":          ("explorer.exe https://twitter.com",        "Twitter / X"),
    "x":                ("explorer.exe https://twitter.com",        "Twitter / X"),
    "reddit":           ("explorer.exe https://www.reddit.com",     "Reddit"),
    "linkedin":         ("explorer.exe https://www.linkedin.com",   "LinkedIn"),
    "youtube":          ("explorer.exe https://www.youtube.com",    "YouTube"),
    "pinterest":        ("explorer.exe https://www.pinterest.com",  "Pinterest"),
    "snapchat":         ("explorer.exe https://web.snapchat.com",   "Snapchat"),

    # ── Development ───────────────────────────────────────────────────────
    "git bash":         ("git-bash",                                "Git Bash"),
    "arduino":          ("arduino",                                 "Arduino IDE"),
    "postman":          ("postman",                                 "Postman"),
    "docker":           ("docker",                                  "Docker Desktop"),
    "android studio":   ("studio64",                                "Android Studio"),
    "pycharm":          ("pycharm64",                               "PyCharm"),
    "intellij":         ("idea64",                                  "IntelliJ IDEA"),

    # ── Cloud & Storage ───────────────────────────────────────────────────
    "google drive":     ("explorer.exe https://drive.google.com",   "Google Drive"),
    "onedrive":         ("onedrive",                                "OneDrive"),
    "dropbox":          ("dropbox",                                 "Dropbox"),

    # ── Gaming ────────────────────────────────────────────────────────────
    "steam":            ("steam",                                   "Steam"),
    "epic games":       ("EpicGamesLauncher",                       "Epic Games Launcher"),

    # ── Miscellaneous ─────────────────────────────────────────────────────
    "obs":              ("obs64",                                   "OBS Studio"),
    "obs studio":       ("obs64",                                   "OBS Studio"),
    "audacity":         ("audacity",                                "Audacity"),
    "blender":          ("blender",                                 "Blender"),
    "gimp":             ("gimp-2.10",                               "GIMP"),
    "photoshop":        ("photoshop",                               "Adobe Photoshop"),
    "premiere":         ("premiere",                                "Adobe Premiere Pro"),
    "after effects":    ("afterfx",                                 "Adobe After Effects"),
    "illustrator":      ("illustrator",                             "Adobe Illustrator"),
    "figma":            ("figma",                                   "Figma"),
    "notion":           ("notion",                                  "Notion"),
    "todoist":          ("todoist",                                 "Todoist"),
    "evernote":         ("evernote",                                "Evernote"),
    "winrar":           ("winrar",                                  "WinRAR"),
    "7zip":             ("7zFM",                                    "7-Zip"),
    "anydesk":          ("anydesk",                                 "AnyDesk"),
    "teamviewer":       ("teamviewer",                              "TeamViewer"),
}


# ─── Regex to extract app name from raw command ─────────────────────────────
_OPEN_TRIGGER = re.compile(
    r"(?:open|launch|start|run|fire\s+up|boot\s+up|bring\s+up)\s+(?:up\s+)?(?:my\s+|the\s+|a\s+)?(.+)",
    re.IGNORECASE,
)


def _normalise(name: str) -> str:
    """Lower-case and strip surrounding whitespace / articles."""
    return re.sub(r"\b(the|my|a|an|app|application|program)\b", "", name.lower()).strip()


def _resolve_app(name: str) -> tuple[str, str] | None:
    """Look up the app in the registry by progressively relaxed matching."""
    norm = _normalise(name)

    # 1. Exact match
    if norm in APP_REGISTRY:
        return APP_REGISTRY[norm]

    # 2. Substring / contains match (e.g. "google chrome browser" → "chrome")
    for key, value in APP_REGISTRY.items():
        if key in norm or norm in key:
            return value

    return None


def extract_app_name(raw_text: str) -> str:
    """Pull the application name from the user's command."""
    m = _OPEN_TRIGGER.search(raw_text)
    if m:
        return m.group(1).strip()
    # Fallback: return everything
    return raw_text.strip()


def execute(raw_text: str) -> str:
    """
    Parse the app name from *raw_text*, resolve it in the registry,
    and launch it.  If the name isn't a known application, fall back to
    file_search so that "open my physics notes" still works.
    """
    app_name = extract_app_name(raw_text)
    print(f"  [OPEN-APP] Looking up \"{app_name}\" …")

    result = _resolve_app(app_name)
    if result is None:
        # Not a known app — try fuzzy file search as a fallback
        print(f"  [OPEN-APP] \"{app_name}\" not in app registry → falling back to file search")
        from commands.file_search import execute as file_search_execute
        return file_search_execute(app_name)

    launch_cmd, friendly_name = result
    print(f"  [OPEN-APP] Launching: {launch_cmd}  ({friendly_name})")

    try:
        # shell=True handles 'start', protocol URIs (ms-settings:), .msc, and explorer.exe variants
        subprocess.Popen(launch_cmd, shell=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Opening {friendly_name}."
    except FileNotFoundError:
        return f"Could not find {friendly_name} on this computer. Is it installed?"
    except Exception as e:
        return f"Failed to open {friendly_name}: {e}"
