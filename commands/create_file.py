"""
Command: Create File
=====================
Creates a new file with the specified name and extension in the
specified directory.  The user must provide the file type in the
command (e.g. "create a python file called utils in Desktop").

Supports folder aliases (Desktop, Documents, Downloads) and absolute paths.
"""

from __future__ import annotations
import os
import re

from config import FILE_EXTENSION_MAP, FOLDER_ALIASES


# ─── Regex patterns for extracting file info ─────────────────────────────────

# "create a python file called notes in Documents"
_CREATE_PATTERN_1 = re.compile(
    r"(?:create|make|new)\s+(?:a\s+)?(\w+)\s+file\s+(?:called|named|with\s+name)\s+"
    r"([a-zA-Z0-9_\- ]+?)\s+(?:in|on|at|inside|under)\s+(.+)",
    re.IGNORECASE,
)

# "create a python file in Documents called notes"
_CREATE_PATTERN_2 = re.compile(
    r"(?:create|make|new)\s+(?:a\s+)?(\w+)\s+file\s+(?:in|on|at|inside|under)\s+"
    r"(.+?)\s+(?:called|named)\s+([a-zA-Z0-9_\- ]+)",
    re.IGNORECASE,
)

# "create a file called notes.py in Documents"
_CREATE_PATTERN_3 = re.compile(
    r"(?:create|make|new)\s+(?:a\s+)?file\s+(?:called|named|with\s+name)\s+"
    r"([a-zA-Z0-9_\- ]+\.\w+)\s+(?:in|on|at|inside|under)\s+(.+)",
    re.IGNORECASE,
)

# "create notes.py in Documents"
_CREATE_PATTERN_4 = re.compile(
    r"(?:create|make|new)\s+([a-zA-Z0-9_\- ]+\.\w+)\s+(?:in|on|at|inside|under)\s+(.+)",
    re.IGNORECASE,
)

# "create a python file called notes" (no directory — defaults to Desktop)
_CREATE_PATTERN_5 = re.compile(
    r"(?:create|make|new)\s+(?:a\s+)?(\w+)\s+file\s+(?:called|named|with\s+name)\s+"
    r"([a-zA-Z0-9_\- ]+)$",
    re.IGNORECASE,
)


def _resolve_folder(folder_text: str) -> str:
    """Resolve a folder alias or path to an absolute path."""
    folder = folder_text.strip().rstrip("/\\")
    norm = folder.lower().replace(" ", "").replace("_", "")

    # Check aliases
    for alias, path in FOLDER_ALIASES.items():
        if norm == alias.replace(" ", "").replace("_", ""):
            return path

    # "my documents" → "documents", etc.
    cleaned = re.sub(r"\b(my|the|a|an)\b", "", norm).strip()
    for alias, path in FOLDER_ALIASES.items():
        if cleaned == alias.replace(" ", "").replace("_", ""):
            return path

    # Treat as absolute path
    if os.path.isabs(folder):
        return folder

    # Treat as relative to Desktop
    desktop = FOLDER_ALIASES.get("desktop", os.path.expanduser("~"))
    return os.path.join(desktop, folder)


def _resolve_extension(ext_word: str) -> str | None:
    """Map a friendly name like 'python' to '.py'."""
    key = ext_word.lower().strip()
    return FILE_EXTENSION_MAP.get(key)


def _parse_command(raw_text: str) -> tuple[str, str, str] | None:
    """
    Extract (filename, extension, folder_path) from the raw command.
    Returns None if parsing fails.
    """
    text = raw_text.strip()

    # Pattern 1: "create a python file called notes in Documents"
    m = _CREATE_PATTERN_1.search(text)
    if m:
        ext_word, filename, folder = m.group(1), m.group(2).strip(), m.group(3).strip()
        ext = _resolve_extension(ext_word)
        if ext:
            return filename, ext, _resolve_folder(folder)

    # Pattern 2: "create a python file in Documents called notes"
    m = _CREATE_PATTERN_2.search(text)
    if m:
        ext_word, folder, filename = m.group(1), m.group(2).strip(), m.group(3).strip()
        ext = _resolve_extension(ext_word)
        if ext:
            return filename, ext, _resolve_folder(folder)

    # Pattern 3: "create a file called notes.py in Documents"
    m = _CREATE_PATTERN_3.search(text)
    if m:
        full_name, folder = m.group(1).strip(), m.group(2).strip()
        name, ext = os.path.splitext(full_name)
        return name, ext, _resolve_folder(folder)

    # Pattern 4: "create notes.py in Documents"
    m = _CREATE_PATTERN_4.search(text)
    if m:
        full_name, folder = m.group(1).strip(), m.group(2).strip()
        name, ext = os.path.splitext(full_name)
        return name, ext, _resolve_folder(folder)

    # Pattern 5: "create a python file called notes" (no folder → Desktop)
    m = _CREATE_PATTERN_5.search(text)
    if m:
        ext_word, filename = m.group(1), m.group(2).strip()
        ext = _resolve_extension(ext_word)
        if ext:
            desktop = FOLDER_ALIASES.get("desktop", os.path.expanduser("~"))
            return filename, ext, desktop

    return None


def execute(raw_text: str) -> str:
    """
    Parse the command, create the file, and open it.
    """
    parsed = _parse_command(raw_text)
    if parsed is None:
        return (
            "I couldn't understand the file creation command.\n"
            "Try: \"Create a python file called utils in Desktop\"\n"
            "  or: \"Create notes.txt in Documents\""
        )

    filename, ext, folder_path = parsed
    full_name = f"{filename}{ext}"
    full_path = os.path.join(folder_path, full_name)

    print(f"  [CREATE-FILE] Name: {full_name}")
    print(f"  [CREATE-FILE] Path: {full_path}")

    # Check if file already exists
    if os.path.isfile(full_path):
        return f"File \"{full_name}\" already exists at {folder_path}."

    # Ensure directory exists
    try:
        os.makedirs(folder_path, exist_ok=True)
    except OSError as e:
        return f"Could not create directory \"{folder_path}\": {e}"

    # Create the file
    try:
        with open(full_path, "w", encoding="utf-8") as fh:
            # Add a minimal header for code files
            if ext == ".py":
                fh.write(f'# {filename}.py\n\n')
            elif ext == ".html":
                fh.write(f'<!DOCTYPE html>\n<html>\n<head>\n  <title>{filename}</title>\n</head>\n<body>\n\n</body>\n</html>\n')
            elif ext in (".js", ".ts"):
                fh.write(f'// {filename}{ext}\n\n')
            elif ext in (".c", ".cpp", ".h"):
                fh.write(f'// {filename}{ext}\n\n')
            elif ext == ".java":
                fh.write(f'public class {filename} {{\n\n}}\n')
            # All other extensions: empty file
    except OSError as e:
        return f"Could not create file: {e}"

    # Open the file with the default application
    try:
        os.startfile(full_path)
    except Exception:
        pass  # Not critical if opening fails

    return f"Created \"{full_name}\" in {folder_path} and opened it."
