"""
Synthetic Training-Data Generator
==================================
Generates labelled utterances for all intents used by the
ESP32 Voice Command Assistant, then saves them as data/training_data.csv.

Run once:
    python generate_data.py

Each row has two columns:
    text   – the raw (unprocessed) user utterance
    intent – the ground-truth label (e.g. "open_app", "file_search")
"""

from __future__ import annotations

import csv
import itertools
import os
import random

# ─── Seed for reproducibility ───────────────────────────────────────────────
random.seed(42)

# ─── Output path ────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
OUTPUT_CSV = os.path.join(DATA_DIR, "training_data.csv")

# ─── Slot fillers ───────────────────────────────────────────────────────────
APPS = [
    "Chrome", "Notepad", "WhatsApp", "Spotify", "VS Code",
    "Firefox", "Word", "Excel", "PowerPoint", "Discord",
    "Slack", "Teams", "Zoom", "Telegram", "Calculator",
    "File Explorer", "Task Manager", "Paint", "VLC", "Steam",
    "OBS Studio", "Brave", "Edge", "Outlook", "Terminal",
]

FILES = [
    "physics notes", "my report", "assignment 3", "lab manual",
    "lecture slides", "project proposal", "research paper",
    "homework answers", "math cheat sheet", "final essay",
    "meeting notes", "resume", "thesis draft", "budget spreadsheet",
    "presentation slides", "exam timetable", "study guide",
]

KEYWORDS = [
    "quantum", "Newton", "voltage", "algorithm", "deadline",
    "frequency", "resistance", "derivative", "gravity", "momentum",
    "thermodynamics", "velocity", "acceleration", "fibonacci",
    "integration", "database", "machine learning", "statistics",
]

TEXTS_TO_TYPE = [
    "Meeting at 3 PM", "Reminder: submit assignment",
    "Buy groceries after class", "Call mom at 5",
    "Email professor about extension", "Lecture rescheduled to Thursday",
    "Project deadline is next Monday", "Pick up laundry at 6",
    "Dentist appointment tomorrow", "Finish chapter 7 tonight",
]

WEB_QUERIES = [
    "what is quantum entanglement", "who invented the transistor",
    "how to solve quadratic equations", "define machine learning",
    "meaning of entropy", "Python list comprehension tutorial",
    "how does GPS work", "what is photosynthesis",
    "latest Nobel Prize winners", "history of the internet",
    "how to make pancakes", "what is a black hole",
    "who is Alan Turing", "how does Wi-Fi work",
    "best programming languages 2025", "what is blockchain",
    # Short single-word and two-word queries (like "search vit")
    "python", "java", "javascript", "github", "stackoverflow",
    "quantum physics", "machine learning", "vit", "calculus",
    "thermodynamics", "database", "linux", "docker", "kubernetes",
    "react", "vue", "angular", "tensorflow", "pytorch",
    "algorithms", "data structures", "neural networks",
    "cloud computing", "cybersecurity", "blockchain",
]

TIMER_DURATIONS = [
    "5 minutes", "10 minutes", "30 seconds", "1 minute",
    "15 minutes", "2 minutes", "1 hour", "45 seconds",
    "20 minutes", "3 minutes", "90 seconds", "half an hour",
]

SCROLL_DIRECTIONS = ["up", "down"]

MEDIA_ACTIONS = [
    "play", "pause", "resume", "next track", "previous track",
    "volume up", "volume down", "mute", "fullscreen",
]

# ─── NEW: Slot fillers for new commands ──────────────────────────────────────

FILE_TYPES = [
    "python", "text", "javascript", "html", "css", "java",
    "c", "cpp", "json", "csv", "markdown", "sql", "yaml",
]

FILE_NAMES = [
    "notes", "utils", "main", "helper", "config", "test",
    "report", "data", "script", "readme", "index", "app",
    "server", "client", "database", "styles",
]

FOLDERS = [
    "Desktop", "Documents", "Downloads", "my Documents",
    "the Desktop", "my Desktop", "Downloads folder",
]

URLS = [
    "youtube.com", "github.com", "google.com", "stackoverflow.com",
    "reddit.com", "twitter.com", "linkedin.com", "wikipedia.org",
    "amazon.com", "netflix.com", "facebook.com", "instagram.com",
]

BRIGHTNESS_LEVELS = [
    "10", "20", "30", "40", "50", "60", "70", "80", "90", "100",
]

WINDOW_ACTIONS_FILLERS = [
    "minimize", "maximize", "snap left", "snap right",
    "show desktop", "minimize all", "switch window", "task view",
]

# ─── Template definitions per intent ────────────────────────────────────────
# Each value is a list of (template_string, slot_list | None).
# {0} is the first slot, {1} the second, etc.

TEMPLATES: dict[str, list[tuple[str, list | None]]] = {
    # ── OPEN_APP ─────────────────────────────────────────────────────────
    "open_app": [
        ("open {0}", APPS),
        ("Open {0}", APPS),
        ("launch {0}", APPS),
        ("Launch {0}", APPS),
        ("start {0}", APPS),
        ("please open {0}", APPS),
        ("can you open {0}", APPS),
        ("fire up {0}", APPS),
        ("run {0}", APPS),
        ("boot up {0}", APPS),
        ("Open {0} for me", APPS),
        ("start {0} please", APPS),
        ("I want to open {0}", APPS),
        ("open up {0}", APPS),
        ("could you launch {0}", APPS),
        ("go ahead and open {0}", APPS),
        ("I need {0} open", APPS),
        ("bring up {0}", APPS),
    ],

    # ── CLOSE_APP ────────────────────────────────────────────────────────
    "close_app": [
        ("close {0}", APPS),
        ("Close {0}", APPS),
        ("quit {0}", APPS),
        ("exit {0}", APPS),
        ("kill {0}", APPS),
        ("terminate {0}", APPS),
        ("shut down {0}", APPS),
        ("stop {0}", APPS),
        ("force close {0}", APPS),
        ("please close {0}", APPS),
        ("can you close {0}", APPS),
        ("end {0}", APPS),
        ("close {0} for me", APPS),
        ("I want to close {0}", APPS),
        ("shut {0} down", APPS),
    ],

    # ── FILE_SEARCH ──────────────────────────────────────────────────────
    "file_search": [
        ("find {0}", FILES),
        ("search for {0}", FILES),
        ("open {0}", FILES),
        ("look for {0}", FILES),
        ("locate {0}", FILES),
        ("where is {0}", FILES),
        ("find my {0}", FILES),
        ("can you find {0}", FILES),
        ("I need {0}", FILES),
        ("pull up {0}", FILES),
        ("get me {0}", FILES),
        ("open my {0}", FILES),
        ("search {0}", FILES),
        ("show me {0}", FILES),
        ("help me find {0}", FILES),
    ],

    # ── CONTENT_SEARCH ───────────────────────────────────────────────────
    "content_search": [
        ("search for {0} in my notes", KEYWORDS),
        ("find {0} in my documents", KEYWORDS),
        ("look for {0} inside my files", KEYWORDS),
        ("search {0} in my PDFs", KEYWORDS),
        ("find mentions of {0}", KEYWORDS),
        ("where does {0} appear in my notes", KEYWORDS),
        ("scan my documents for {0}", KEYWORDS),
        ("search {0} in my homework", KEYWORDS),
        ("grep {0} in my files", KEYWORDS),
        ("look up {0} in my lecture notes", KEYWORDS),
    ],

    # ── SUMMARIZE ────────────────────────────────────────────────────────
    "summarize": [
        ("summarize {0}", FILES),
        ("give me a summary of {0}", FILES),
        ("summarise {0}", FILES),
        ("can you summarize {0}", FILES),
        ("shorten {0}", FILES),
        ("brief me on {0}", FILES),
        ("TLDR of {0}", FILES),
        ("what does {0} say", FILES),
        ("condense {0}", FILES),
        ("recap {0} for me", FILES),
        ("break down {0} for me", FILES),
    ],

    # ── WEB_SEARCH ───────────────────────────────────────────────────────
    "web_search": [
        ("search {0}", WEB_QUERIES),
        ("google {0}", WEB_QUERIES),
        ("look up {0}", WEB_QUERIES),
        ("search the web for {0}", WEB_QUERIES),
        ("what is {0}", WEB_QUERIES),
        ("tell me about {0}", WEB_QUERIES),
        ("who is {0}", WEB_QUERIES),
        ("how to {0}", WEB_QUERIES),
        ("{0}", WEB_QUERIES),
        ("can you search {0}", WEB_QUERIES),
        ("find out {0}", WEB_QUERIES),
    ],

    # ── SYSTEM_INFO ──────────────────────────────────────────────────────
    "system_info": [
        ("{0}", [
            "what is my CPU usage", "how much RAM am I using",
            "check battery percentage", "show disk space",
            "what is my IP address", "system information",
            "how much memory is free", "check CPU temperature",
            "show system stats", "what is my battery level",
            "how much storage do I have left", "check system status",
            "RAM usage", "CPU usage", "disk usage",
            "show me system information", "tell me my IP address",
            "give me system stats", "computer stats",
            "memory usage", "how much disk space is left",
            "my computer info", "what is CPU utilization",
            "check my battery", "how hot is my CPU",
            "show hardware info", "computer health check",
        ]),
    ],

    # ── SCREENSHOT ───────────────────────────────────────────────────────
    "screenshot": [
        ("{0}", [
            "take a screenshot", "screenshot", "capture screen",
            "screen capture", "take a screen shot", "snap the screen",
            "grab a screenshot", "capture my screen", "take screenshot now",
            "save a screenshot", "screenshot this", "screen shot please",
            "take a picture of my screen", "capture this screen",
            "print screen", "screenshot the screen", "screen grab",
            "take screen capture", "snap a screenshot",
            "I want a screenshot", "get a screenshot",
            "can you take a screenshot", "please capture my screen",
            "save screen capture", "do a screenshot",
        ]),
    ],

    # ── TIMER ────────────────────────────────────────────────────────────
    "timer": [
        ("set a timer for {0}", TIMER_DURATIONS),
        ("timer for {0}", TIMER_DURATIONS),
        ("countdown {0}", TIMER_DURATIONS),
        ("set an alarm for {0}", TIMER_DURATIONS),
        ("remind me in {0}", TIMER_DURATIONS),
        ("start a {0} timer", TIMER_DURATIONS),
        ("{0} timer", TIMER_DURATIONS),
        ("wake me up in {0}", TIMER_DURATIONS),
        ("set timer {0}", TIMER_DURATIONS),
        ("count down from {0}", TIMER_DURATIONS),
        ("start countdown {0}", TIMER_DURATIONS),
    ],

    # ── ACTIVE_TYPING ────────────────────────────────────────────────────
    "active_typing": [
        ("write this down: {0}", TEXTS_TO_TYPE),
        ("type this: {0}", TEXTS_TO_TYPE),
        ("note this down: {0}", TEXTS_TO_TYPE),
        ("type: {0}", TEXTS_TO_TYPE),
        ("write: {0}", TEXTS_TO_TYPE),
        ("jot down: {0}", TEXTS_TO_TYPE),
        ("type out: {0}", TEXTS_TO_TYPE),
        ("write down: {0}", TEXTS_TO_TYPE),
        ("take a note: {0}", TEXTS_TO_TYPE),
        ("write this: {0}", TEXTS_TO_TYPE),
        ("note: {0}", TEXTS_TO_TYPE),
    ],

    # ── GUI_CONTROL ──────────────────────────────────────────────────────
    "gui_control": [
        ("scroll {0}", SCROLL_DIRECTIONS),
        ("page {0}", SCROLL_DIRECTIONS),
        ("{0}", MEDIA_ACTIONS),
        ("press {0}", MEDIA_ACTIONS),
        ("hit {0}", MEDIA_ACTIONS),
        ("scroll {0} please", SCROLL_DIRECTIONS),
        ("can you scroll {0}", SCROLL_DIRECTIONS),
        ("{0}", [
            "scroll up", "scroll down", "page up", "page down",
            "play the video", "pause the video", "resume playback",
            "skip to next track", "go back a track",
            "turn volume up", "turn volume down", "mute the audio",
            "go fullscreen", "exit fullscreen",
            "increase the volume", "decrease the volume",
            "play music", "stop the music", "pause playback",
        ]),
    ],

    # ══════════════════════════════════════════════════════════════════════
    # NEW INTENTS
    # ══════════════════════════════════════════════════════════════════════

    # ── CREATE_FILE ──────────────────────────────────────────────────────
    "create_file": [
        ("create a {0} file called {1} in {2}", None),     # expanded manually below
        ("make a {0} file named {1} in {2}", None),
        ("new {0} file called {1} in {2}", None),
        ("create {1}.{0} in {2}", None),
        ("make a new {0} file called {1}", None),
        ("{0}", [
            # Pre-expanded full utterances for robust training
            "create a python file called notes in Desktop",
            "create a python file called utils in Documents",
            "make a text file named readme in Downloads",
            "create a javascript file called app in Desktop",
            "new html file called index in Documents",
            "create a json file called config in Desktop",
            "make a css file named styles in Desktop",
            "create a python file called main in my Documents",
            "make a java file called server in Downloads",
            "create a csv file called data in the Desktop",
            "new markdown file called readme in Documents",
            "create a sql file called schema in Desktop",
            "make a python file called test in Documents",
            "create a text file called notes in Downloads",
            "new javascript file called script in the Desktop",
            "create a cpp file called main in Documents",
            "make a c file called hello in Desktop",
            "create a yaml file called config in Documents",
            "create notes.py in Desktop",
            "create readme.txt in Documents",
            "make index.html in Downloads",
            "create config.json in Desktop",
            "new styles.css in my Documents",
            "create main.java in Desktop",
            "create a python file called helper",
            "make a text file named draft",
            "new javascript file called utils",
            "create a html file called page",
            "create a python file in Desktop called app",
            "make a text file in Documents named log",
            "create a json file in Downloads called package",
            "new csv file in Desktop called records",
            "create a markdown file in my Documents called notes",
            "make a python file in the Desktop called script",
            "I want to create a python file called bot in Desktop",
            "can you create a text file called memo in Documents",
            "please create a html file called site in Downloads",
            "create a new python file called analyzer in Desktop",
            "I need a javascript file called handler in Documents",
        ]),
    ],

    # ── SYSTEM_POWER ─────────────────────────────────────────────────────
    "system_power": [
        ("{0}", [
            "lock the screen", "lock screen", "lock my computer",
            "lock my PC", "lock this computer", "please lock the screen",
            "can you lock the screen", "lock it",
            "shut down", "shutdown", "shut down the computer",
            "shutdown my PC", "turn off the computer", "power off",
            "shut down my computer", "please shut down",
            "turn off my PC", "shut it down",
            "restart", "restart the computer", "reboot",
            "restart my PC", "reboot the system", "please restart",
            "restart my computer", "reboot my computer",
            "sleep", "go to sleep", "put to sleep",
            "put the computer to sleep", "sleep mode",
            "enter sleep mode", "hibernate", "suspend",
            "standby", "put my PC to sleep",
            "log off", "log out", "sign out", "sign off",
            "log me off", "log me out", "sign me out",
        ]),
    ],

    # ── BRIGHTNESS ───────────────────────────────────────────────────────
    "brightness": [
        ("set brightness to {0}", BRIGHTNESS_LEVELS),
        ("brightness {0}%", BRIGHTNESS_LEVELS),
        ("{0}% brightness", BRIGHTNESS_LEVELS),
        ("set screen brightness to {0}", BRIGHTNESS_LEVELS),
        ("change brightness to {0}", BRIGHTNESS_LEVELS),
        ("{0}", [
            "brightness up", "increase brightness", "brighter",
            "make it brighter", "raise brightness", "more brightness",
            "turn up brightness", "higher brightness",
            "brightness down", "decrease brightness", "dimmer",
            "make it dimmer", "lower brightness", "less brightness",
            "turn down brightness", "dim the screen", "reduce brightness",
            "what is my brightness", "check brightness",
            "show brightness", "current brightness level",
            "how bright is my screen", "get brightness",
            "brightness level", "screen brightness",
        ]),
    ],

    # ── WINDOW_MGMT ──────────────────────────────────────────────────────
    "window_mgmt": [
        ("{0}", [
            "minimize this window", "minimize the window",
            "minimise this window", "minimise the window",
            "maximize this window", "maximize the window",
            "maximise this window", "maximise the window",
            "snap left", "snap to the left", "move window left",
            "snap right", "snap to the right", "move window right",
            "snap window left", "snap window right",
            "show desktop", "minimize all", "minimise all",
            "minimize all windows", "minimise all windows",
            "show the desktop", "go to desktop",
            "switch window", "next window", "alt tab",
            "switch to next window", "cycle windows",
            "task view", "show all windows", "show task view",
            "close this window", "close window",
            "new virtual desktop", "new desktop",
            "close virtual desktop", "close desktop",
            "move window to the left", "move window to the right",
            "tile window left", "tile window right",
            "full screen this window", "make this window full screen",
        ]),
    ],

    # ── OPEN_URL ─────────────────────────────────────────────────────────
    "open_url": [
        ("open {0}", URLS),
        ("go to {0}", URLS),
        ("visit {0}", URLS),
        ("navigate to {0}", URLS),
        ("browse to {0}", URLS),
        ("open {0} in browser", URLS),
        ("go to {0} please", URLS),
        ("take me to {0}", URLS),
        ("head to {0}", URLS),
        ("load {0}", URLS),
        ("{0}", [
            "open youtube", "go to github", "visit google",
            "navigate to stackoverflow", "open reddit",
            "go to twitter", "visit linkedin", "open wikipedia",
            "go to amazon", "open netflix", "visit facebook",
            "open instagram", "go to gmail", "open chatgpt",
            "visit notion", "open whatsapp web",
            "open youtube in browser", "take me to github",
            "head to google.com", "browse to reddit.com",
            "I want to visit stackoverflow.com",
        ]),
    ],
}


def _expand_templates() -> list[dict[str, str]]:
    """
    Expand every template × slot-filler combination into labelled rows.
    Returns a list of {"text": ..., "intent": ...} dicts.
    """
    rows: list[dict[str, str]] = []
    for intent, templates in TEMPLATES.items():
        for template_str, fillers in templates:
            if fillers is None:
                rows.append({"text": template_str, "intent": intent})
            else:
                for filler in fillers:
                    rows.append({
                        "text": template_str.format(filler),
                        "intent": intent,
                    })
    return rows


def main() -> None:
    rows = _expand_templates()
    random.shuffle(rows)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["text", "intent"])
        writer.writeheader()
        writer.writerows(rows)

    # Quick distribution summary
    from collections import Counter
    dist = Counter(r["intent"] for r in rows)
    print(f"✓ Generated {len(rows)} samples → {OUTPUT_CSV}")
    print("  Distribution:")
    for intent, count in sorted(dist.items()):
        print(f"    {intent:20s}  {count:>4d}")


if __name__ == "__main__":
    main()
