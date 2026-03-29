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
    3. Wait for silence detection (auto-stops after 1s silence or 3s max)
    4. See transcription and command execution
    5. Repeat!
"""

from serial_listener import start_serial_listener
import sys

# Import the working command handler from main.py
from main import handle_command


if __name__ == "__main__":
    print("╔═════════════════════════════════════════════════════════╗")
    print("║       ESP32 Voice Assistant - MANUAL TRIGGER MODE       ║")
    print("╚═════════════════════════════════════════════════════════╝")
    print()
    print("📌 How to use:")
    print("   1. Press ENTER to start recording")
    print("   2. Speak your command clearly")
    print("   3. Stop speaking (auto-stops after 1s silence or 3s max)")
    print("   4. Wait for transcription and execution")
    print("   5. Repeat!")
    print()
    
    try:
        start_serial_listener(handle_command)
    except KeyboardInterrupt:
        print("\n\n[EXIT] Goodbye!")
        sys.exit(0)
