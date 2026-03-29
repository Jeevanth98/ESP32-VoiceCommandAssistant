"""
ESP32 Voice Command Assistant — Configuration
===============================================
Central configuration for scan directories, model names,
thresholds, serial port settings, and new command parameters.
"""

import os
import json

# ─── Project root ───────────────────────────────────────────────────────────
_PROJECT_ROOT = os.path.dirname(__file__)

# ─── Scan Directories (for Fuzzy File Search & Content Mining) ──────────────
#
# Resolution order:
#   1. VOICE_ASSISTANT_SCAN_DIRS env var  (semicolon-separated)
#   2. scan_dirs.txt in project root  (one path per line, # = comment)
#   3. All fixed drives detected via psutil
#

_SCAN_DIRS_FILE = os.path.join(_PROJECT_ROOT, "scan_dirs.txt")


def _resolve_scan_directories() -> list[str]:
    """Determine which directories to index for file/content search."""

    # 1. Environment variable
    env = os.environ.get("VOICE_ASSISTANT_SCAN_DIRS", "").strip()
    if env:
        return [p.strip() for p in env.split(";") if p.strip()]

    # 2. Config file
    if os.path.isfile(_SCAN_DIRS_FILE):
        dirs = []
        with open(_SCAN_DIRS_FILE, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    dirs.append(line)
        if dirs:
            return dirs

    # 3. Auto-detect all fixed drives
    try:
        import psutil
        parts = psutil.disk_partitions(all=False)
        drives = []
        for p in parts:
            # Include only fixed drives (not CD-ROM, etc.)
            if "fixed" in p.opts.lower() or "rw" in p.opts.lower():
                drives.append(p.mountpoint)
        if drives:
            return drives
    except ImportError:
        pass

    # Ultimate fallback
    return [r"D:\Sem-06"]


SCAN_DIRECTORIES = _resolve_scan_directories()


# File extensions recognised by the fuzzy file-search module
SEARCHABLE_EXTENSIONS = {
    # Documents
    ".pdf", ".docx", ".doc", ".txt", ".pptx", ".xlsx", ".csv",
    # Code
    ".py", ".c", ".cpp", ".h", ".ino", ".java", ".js", ".html", ".css",
    # Images (for opening, not content mining)
    ".png", ".jpg", ".jpeg", ".gif", ".bmp",
    # Archives / misc
    ".zip", ".rar",
}

# Extensions that the Content-Mining module can actually *read* inside
READABLE_EXTENSIONS = {".pdf", ".docx", ".txt"}

# ─── Fuzzy Search Settings ──────────────────────────────────────────────────
FUZZY_MATCH_THRESHOLD = 60          # Minimum similarity score (0-100) for a match
FUZZY_MAX_RESULTS     = 5           # Top-N results returned to the user

# ─── File Index Cache ───────────────────────────────────────────────────────
FILE_INDEX_CACHE_PATH = os.path.join(_PROJECT_ROOT, "data", "file_index_cache.json")

# ─── NLU / AI Model Settings ────────────────────────────────────────────────
# Minimum confidence for the TF-IDF + LinearSVC classifier to accept an intent
INTENT_CONFIDENCE_THRESHOLD = 0.30

# ─── Serial / ESP32 Settings ────────────────────────────────────────────────
SERIAL_PORT    = "COM6"      # Your ESP32 COM port
SERIAL_BAUD    = 115200
SERIAL_TIMEOUT = 1           # seconds

# ESP32 audio format (for Whisper STT)
AUDIO_SAMPLE_RATE = 16000    # 16 kHz
AUDIO_BIT_DEPTH   = 16       # 16-bit PCM
AUDIO_CHANNELS    = 1        # Mono

# Protocol bytes
SERIAL_HEADER_BYTE = 0xAA    # Audio chunk incoming
SERIAL_END_BYTE    = 0x55    # End of utterance

# ─── Wake Word ──────────────────────────────────────────────────────────────
WAKE_WORD = ""  # Disabled for easier testing - process every command
                # Set to "hey assistant" to require wake word

# ─── Whisper STT Settings ───────────────────────────────────────────────────
WHISPER_MODEL = "small"      # Options: tiny, base, small, medium, large
                              # "small" = better accuracy (~244 MB, recommended)
                              # "base" = faster but less accurate (~74 MB)

# ─── Active Typing Settings ─────────────────────────────────────────────────
NOTEPAD_WAIT = 1.5           # seconds to wait after opening Notepad

# ─── AI Summarization Settings ──────────────────────────────────────────────
SUMMARIZATION_MODEL = "facebook/bart-large-cnn"
SUMMARY_MAX_TOKENS  = 1024   # max input tokens sent to the summarizer
SUMMARY_MAX_LENGTH  = 130    # max output summary length (tokens)
SUMMARY_MIN_LENGTH  = 30     # min output summary length (tokens)

# ─── System Power Settings ──────────────────────────────────────────────────
SHUTDOWN_GRACE_PERIOD = 5    # seconds before shutdown/restart executes

# ─── Brightness Settings ────────────────────────────────────────────────────
BRIGHTNESS_STEP = 10         # percentage change for "brightness up/down"

# ─── Create File Settings ───────────────────────────────────────────────────
# Map of friendly extension names → actual extensions
FILE_EXTENSION_MAP = {
    "python":     ".py",
    "py":         ".py",
    "text":       ".txt",
    "txt":        ".txt",
    "javascript": ".js",
    "js":         ".js",
    "html":       ".html",
    "css":        ".css",
    "java":       ".java",
    "c":          ".c",
    "cpp":        ".cpp",
    "c++":        ".cpp",
    "json":       ".json",
    "csv":        ".csv",
    "markdown":   ".md",
    "md":         ".md",
    "xml":        ".xml",
    "yaml":       ".yaml",
    "yml":        ".yaml",
    "sql":        ".sql",
    "bat":        ".bat",
    "ps1":        ".ps1",
    "sh":         ".sh",
    "docx":       ".docx",
    "pdf":        ".pdf",
    "word":       ".docx",
    "excel":      ".xlsx",
    "xlsx":       ".xlsx",
}

# Map of friendly folder aliases → actual paths
FOLDER_ALIASES = {
    "desktop":    os.path.join(os.path.expanduser("~"), "Desktop"),
    "documents":  os.path.join(os.path.expanduser("~"), "Documents"),
    "downloads":  os.path.join(os.path.expanduser("~"), "Downloads"),
    "pictures":   os.path.join(os.path.expanduser("~"), "Pictures"),
    "music":      os.path.join(os.path.expanduser("~"), "Music"),
    "videos":     os.path.join(os.path.expanduser("~"), "Videos"),
}

# ─── Captures / Output ──────────────────────────────────────────────────────
CAPTURES_DIR = os.path.join(_PROJECT_ROOT, "captures")
os.makedirs(CAPTURES_DIR, exist_ok=True)
