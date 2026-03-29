"""
Manual Trigger Mode — Press ENTER to Record
============================================
This is a wrapper around serial_listener that adds manual recording control.
Press ENTER to start recording, then speak your command.

Usage:
    python manual_trigger.py
    
    Then:
    1. Press ENTER
    2. Speak your command
    3. Wait for silence detection (auto-stops after 1s silence)
    4. See transcription and command execution
    5. Repeat!
"""

from serial_listener import start_serial_listener
import sys

def handle_command(text: str) -> str:
    """
    Process transcribed text through NLU pipeline.
    This is the same handler from main.py
    """
    # Import NLU modules
    from nlu.preprocessor import preprocess
    from nlu.intent_classifier import classify_intent
    from nlu.entity_extractor import extract
    
    # Import command handlers
    from commands import (
        file_search, content_mining, active_typing, summarize,
        screenshot, gui_control, system_info, timer, open_app,
        web_search, close_app, create_file, system_power,
        brightness, window_mgmt, open_url
    )
    
    import re
    
    # Keyword overrides for fast routing
    _KEYWORD_OVERRIDES = [
        (re.compile(r"\b(write\s+(this\s+)?(down)?|type\s+(this)?|note\s+(this\s+)?(down)?)\s*:?\s*", re.I), "active_typing"),
        (re.compile(r"\b(scroll\s*(up|down)|page\s*(up|down))\b", re.I), "gui_control"),
        (re.compile(r"\b(play|pause|resume|next\s*track|prev\s*track|volume\s*(up|down)|mute|fullscreen)\b", re.I), "gui_control"),
        (re.compile(r"\b(screenshot|screen\s*capture|capture\s*screen|screen\s*shot)\b", re.I), "screenshot"),
        (re.compile(r"\b(timer|countdown|alarm)\b", re.I), "timer"),
        (re.compile(r"\b(create|make|new)\s+(?:a\s+)?\w+\s+file\b", re.I), "create_file"),
        (re.compile(r"\b(create|make|new)\s+\S+\.\w+\s+", re.I), "create_file"),
        (re.compile(r"\block\s+(the\s+)?screen\b|\block\s+(my\s+)?(computer|pc)\b", re.I), "system_power"),
        (re.compile(r"\b(shut\s*down|shutdown|power\s*off|turn\s*off)\s*(the\s+)?(computer|pc|system)?\b", re.I), "system_power"),
        (re.compile(r"\b(restart|reboot)\s*(the\s+)?(computer|pc|system)?\b", re.I), "system_power"),
        (re.compile(r"\b(sleep|hibernate|suspend|standby)\s*(mode)?\b", re.I), "system_power"),
        (re.compile(r"\b(log\s*off|log\s*out|sign\s*out)\b", re.I), "system_power"),
        (re.compile(r"\b(brightness|screen\s*brightness)\b", re.I), "brightness"),
        (re.compile(r"\b(minimize|maximize|close\s*window)\b", re.I), "window_mgmt"),
        (re.compile(r"\b(open|go\s*to)\s+(https?://|www\.)", re.I), "open_url"),
    ]
    
    # Fast keyword check
    for pattern, intent_name in _KEYWORD_OVERRIDES:
        if pattern.search(text):
            entities = extract(text, intent_name)
            
            # Route to handler
            if intent_name == "file_search":
                return file_search.execute(entities)
            elif intent_name == "content_mining":
                return content_mining.execute(entities)
            elif intent_name == "active_typing":
                return active_typing.execute(entities)
            elif intent_name == "summarize":
                return summarize.execute(entities)
            elif intent_name == "screenshot":
                return screenshot.execute(entities)
            elif intent_name == "gui_control":
                return gui_control.execute(entities)
            elif intent_name == "system_info":
                return system_info.execute(entities)
            elif intent_name == "timer":
                return timer.execute(entities)
            elif intent_name == "open_app":
                return open_app.execute(entities)
            elif intent_name == "web_search":
                return web_search.execute(entities)
            elif intent_name == "close_app":
                return close_app.execute(entities)
            elif intent_name == "create_file":
                return create_file.execute(entities)
            elif intent_name == "system_power":
                return system_power.execute(entities)
            elif intent_name == "brightness":
                return brightness.execute(entities)
            elif intent_name == "window_mgmt":
                return window_mgmt.execute(entities)
            elif intent_name == "open_url":
                return open_url.execute(entities)
    
    # NLU pipeline
    preprocessed = preprocess(text)
    intent = classify_intent(preprocessed)
    entities = extract(text, intent)
    
    # Route to handler
    if intent == "file_search":
        return file_search.execute(entities)
    elif intent == "content_mining":
        return content_mining.execute(entities)
    elif intent == "active_typing":
        return active_typing.execute(entities)
    elif intent == "summarize":
        return summarize.execute(entities)
    elif intent == "screenshot":
        return screenshot.execute(entities)
    elif intent == "gui_control":
        return gui_control.execute(entities)
    elif intent == "system_info":
        return system_info.execute(entities)
    elif intent == "timer":
        return timer.execute(entities)
    elif intent == "open_app":
        return open_app.execute(entities)
    elif intent == "web_search":
        return web_search.execute(entities)
    elif intent == "close_app":
        return close_app.execute(entities)
    elif intent == "create_file":
        return create_file.execute(entities)
    elif intent == "system_power":
        return system_power.execute(entities)
    elif intent == "brightness":
        return brightness.execute(entities)
    elif intent == "window_mgmt":
        return window_mgmt.execute(entities)
    elif intent == "open_url":
        return open_url.execute(entities)
    else:
        return f"Unknown intent: {intent}"


if __name__ == "__main__":
    print("╔═════════════════════════════════════════════════════════╗")
    print("║       ESP32 Voice Assistant - MANUAL TRIGGER MODE       ║")
    print("╚═════════════════════════════════════════════════════════╝")
    print()
    print("📌 How to use:")
    print("   1. Press ENTER to start recording")
    print("   2. Speak your command clearly")
    print("   3. Stop speaking (silence auto-detected after 1s)")
    print("   4. Wait for transcription and execution")
    print("   5. Repeat!")
    print()
    
    try:
        start_serial_listener(handle_command)
    except KeyboardInterrupt:
        print("\n\n[EXIT] Goodbye!")
        sys.exit(0)
