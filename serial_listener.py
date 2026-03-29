"""
Serial Listener — ESP32 Audio Receiver + Whisper Pipeline
==========================================================
Background thread that:
  1. Listens on the configured COM port for audio data from ESP32
  2. Waits for user to press ENTER to trigger recording
  3. Receives raw 16-bit PCM audio frames
  4. Passes audio to Whisper for transcription
  5. Feeds transcribed text into the NLU pipeline
  6. Sends feedback bytes back to ESP32 (buzzer, acknowledgement)

Serial Protocol (ESP32 → PC):
  Header:  0xAA (1 byte)  — signals "audio data incoming"
  Length:  4 bytes (little-endian uint32) — payload size in bytes
  Payload: raw 16-bit PCM audio at 16 kHz mono
  End:     0x55 (1 byte, optional) — marks end of utterance

Serial Protocol (PC → ESP32):
  'A' — acknowledged (ready for more data)
  'R' — result/response follows (next bytes are a UTF-8 string)
  'B' — buzzer trigger (timer done, notification, etc.)
  'W' — wake word detected, start listening
  'S' — start recording (manual trigger mode)
"""

from __future__ import annotations
import struct
import threading
import time
import sys
import select

import serial

from config import (
    SERIAL_PORT,
    SERIAL_BAUD,
    SERIAL_TIMEOUT,
    SERIAL_HEADER_BYTE,
    SERIAL_END_BYTE,
    AUDIO_SAMPLE_RATE,
    AUDIO_BIT_DEPTH,
    WAKE_WORD,
)
from stt.whisper_stt import transcribe_audio_bytes


def _read_audio_frame(ser: serial.Serial) -> bytes | None:
    """
    Read a single audio frame from the serial port.

    Expects:
      0xAA  [4-byte length LE]  [payload bytes]

    Returns the raw PCM payload bytes, or None on timeout/error.
    """
    # Wait for header byte
    header = ser.read(1)
    if not header or header[0] != SERIAL_HEADER_BYTE:
        return None

    # Read 4-byte length
    length_bytes = ser.read(4)
    if len(length_bytes) < 4:
        return None

    payload_length = struct.unpack("<I", length_bytes)[0]
    if payload_length == 0 or payload_length > 1_000_000:  # sanity cap at 1 MB
        return None

    # Read payload
    payload = ser.read(payload_length)
    if len(payload) < payload_length:
        print(f"  [SERIAL] Incomplete frame: got {len(payload)}/{payload_length} bytes")
        return None

    return payload


def _send_response(ser: serial.Serial, code: str, message: str = ""):
    """Send a response code (and optional message) back to ESP32."""
    try:
        ser.write(code.encode("ascii"))
        if message:
            msg_bytes = message.encode("utf-8")
            ser.write(struct.pack("<H", len(msg_bytes)))
            ser.write(msg_bytes)
        ser.flush()
    except serial.SerialException:
        pass


def start_serial_listener(command_handler):
    """
    Main entry point for serial mode.

    Parameters
    ----------
    command_handler : callable
        Function that takes a raw text string and returns a response string.
        This is typically ``main.handle_command``.
    """
    print(f"[SERIAL] Opening {SERIAL_PORT} at {SERIAL_BAUD} baud …")

    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=SERIAL_BAUD,
            timeout=SERIAL_TIMEOUT,
        )
    except serial.SerialException as e:
        print(f"[ERR] Could not open serial port {SERIAL_PORT}: {e}")
        print("      Make sure the ESP32 is connected and the port is correct.")
        print(f"      You can change the port in config.py (current: {SERIAL_PORT})")
        sys.exit(1)

    print(f"[SERIAL] Listening on {SERIAL_PORT} …")
    print(f"[SERIAL] Wake word: \"{WAKE_WORD}\"")
    print(f"[SERIAL] Audio format: {AUDIO_SAMPLE_RATE} Hz, {AUDIO_BIT_DEPTH}-bit, mono")
    print("[SERIAL] ⚡ MANUAL MODE: Press ENTER to start recording, then speak!")
    print("[SERIAL] Press Ctrl+C to stop.\n")

    _send_response(ser, "A")  # Signal ready

    audio_buffer = bytearray()
    is_recording = False
    
    # Start keyboard listener thread
    def keyboard_listener():
        """Background thread to listen for Enter key"""
        while True:
            try:
                # Wait for Enter key
                input()  # Blocking call - waits for Enter
                print("\n🎤 [READY] Recording triggered! Speak now...")
                _send_response(ser, "S")  # Send 'S' to ESP32 to start recording
            except EOFError:
                break
            except KeyboardInterrupt:
                break
    
    keyboard_thread = threading.Thread(target=keyboard_listener, daemon=True)
    keyboard_thread.start()

    try:
        while True:
            # Check for incoming data
            if ser.in_waiting == 0:
                time.sleep(0.01)
                continue

            # Read a byte to determine what's coming
            peek = ser.read(1)
            if not peek:
                continue

            byte_val = peek[0]

            # ── Audio frame header ───────────────────────────────────
            if byte_val == SERIAL_HEADER_BYTE:
                # Read length + payload
                length_bytes = ser.read(4)
                if len(length_bytes) < 4:
                    continue

                payload_length = struct.unpack("<I", length_bytes)[0]
                if payload_length == 0 or payload_length > 1_000_000:
                    continue

                payload = ser.read(payload_length)
                if len(payload) < payload_length:
                    continue

                audio_buffer.extend(payload)
                _send_response(ser, "A")  # Acknowledge frame

            # ── End-of-utterance marker ──────────────────────────────
            elif byte_val == SERIAL_END_BYTE:
                if not audio_buffer:
                    continue

                print(f"\n  [SERIAL] Received {len(audio_buffer)} bytes of audio")

                # --- Save to WAV for debugging ---
                import wave
                wav_path = "debug_audio.wav"
                try:
                    with wave.open(wav_path, "wb") as wf:
                        wf.setnchannels(1)           # Mono
                        wf.setsampwidth(2)           # 16-bit
                        wf.setframerate(16000)       # 16 kHz
                        wf.writeframes(bytes(audio_buffer))
                    print(f"  [DEBUG] Saved audio to {wav_path}. Listen to check quality!")
                except Exception as e:
                    print(f"  [DEBUG] Could not save WAV: {e}")

                # Transcribe
                text = transcribe_audio_bytes(
                    bytes(audio_buffer),
                    sample_rate=AUDIO_SAMPLE_RATE,
                    bit_depth=AUDIO_BIT_DEPTH,
                )
                audio_buffer.clear()

                if not text:
                    print("  [SERIAL] No speech detected")
                    _send_response(ser, "A")
                    continue

                # Check for wake word
                text_lower = text.lower().strip()
                if WAKE_WORD in text_lower:
                    # Strip the wake word from the command
                    command_text = text_lower.replace(WAKE_WORD, "").strip()
                    if not command_text:
                        print(f"  [SERIAL] Wake word detected — waiting for command …")
                        _send_response(ser, "W")  # Signal: listening
                        continue
                    text = command_text

                print(f"  [RAW]    \"{text}\"")

                # Process through NLU pipeline
                result = command_handler(text)
                print(f"\n🤖 Assistant > {result}\n")

                # Send result back to ESP32
                _send_response(ser, "R", result)

            # ── Unknown byte — could be text/debug from ESP32 ────────
            else:
                # Read remaining line (debug output from ESP32)
                try:
                    rest = ser.readline().decode("utf-8", errors="ignore")
                    line = chr(byte_val) + rest.strip()
                    if line:
                        print(f"  [ESP32] {line}")
                except Exception:
                    pass

    except KeyboardInterrupt:
        print("\n[SERIAL] Stopped by user.")
    except serial.SerialException as e:
        print(f"\n[SERIAL] Connection lost: {e}")
    finally:
        ser.close()
        print("[SERIAL] Port closed.")
