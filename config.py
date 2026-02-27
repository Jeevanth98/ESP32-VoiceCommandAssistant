"""
ESP32 Voice Command Assistant — Configuration
===============================================
Central configuration for scan directories, model names,
thresholds, and serial port settings.
"""

import os

# ─── Scan Directories (for Fuzzy File Search & Content Mining) ──────────────
SCAN_DIRECTORIES = [
    r"D:\Sem-06",
]

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

# ─── NLU / AI Model Settings ────────────────────────────────────────────────
# Zero-Shot Classification model (intent detection)
ZERO_SHOT_MODEL = "facebook/bart-large-mnli"

# Intent labels that the classifier chooses from
INTENT_LABELS = [
    "search for a file and open it",
    "search for a keyword inside document contents",
    "type or write text in notepad",
    "summarize or give a summary of a document",
    "take a screenshot or capture the screen",
    "scroll up or scroll down or play pause or control volume or media control",
    "check system information like cpu usage ram memory battery percentage disk space or ip address",
    "set a timer or countdown or alarm for a specific duration",
    "open or launch an application or program like WhatsApp Chrome Notepad or any app",
    "close or quit or terminate or kill a running application or program",
    "search the web or Google something or look up information online",
]

# Friendly intent keys mapped 1-to-1 with INTENT_LABELS above
INTENT_KEYS = [
    "file_search",
    "content_search",
    "active_typing",
    "summarize",
    "screenshot",
    "gui_control",
    "system_info",
    "timer",
    "open_app",
    "close_app",
    "web_search",
]

# Minimum confidence for an intent to be accepted
INTENT_CONFIDENCE_THRESHOLD = 0.30

# ─── Serial / ESP32 Settings (for future hardware integration) ──────────────
SERIAL_PORT  = "COM3"      # Change to your ESP32 COM port
SERIAL_BAUD  = 115200
SERIAL_TIMEOUT = 1          # seconds

# ─── Active Typing Settings ─────────────────────────────────────────────────
TYPING_INTERVAL = 0.03     # seconds between each keystroke (pyautogui)
NOTEPAD_WAIT    = 1.5       # seconds to wait after opening Notepad

# ─── AI Summarization Settings ──────────────────────────────────────────────
SUMMARIZATION_MODEL = "facebook/bart-large-cnn"
SUMMARY_MAX_TOKENS  = 1024   # max input tokens sent to the summarizer
SUMMARY_MAX_LENGTH  = 130    # max output summary length (tokens)
SUMMARY_MIN_LENGTH  = 30     # min output summary length (tokens)

# ─── Captures / Output ──────────────────────────────────────────────────────
CAPTURES_DIR = os.path.join(os.path.dirname(__file__), "captures")
os.makedirs(CAPTURES_DIR, exist_ok=True)
