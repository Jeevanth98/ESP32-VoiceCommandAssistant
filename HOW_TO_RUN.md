# 🚨 IMPORTANT: How to Run the Serial Listener

## ❌ WRONG Way (doesn't work):
```bash
python serial_listener.py
```
↑ This file is a module, not a script!

---

## ✅ CORRECT Way:

### Option 1: Manual Trigger Mode (Recommended)
```bash
python manual_trigger.py
```

**How it works:**
1. Press ENTER when you want to record
2. Speak your command
3. Silence detected → auto-stops → transcribes → executes
4. Repeat!

**Benefits:**
- ✅ No accidental recordings
- ✅ You control when to record
- ✅ Perfect for testing

---

### Option 2: Original Serial Mode
```bash
python main.py --serial
```

This uses the original continuous listening mode.

This will:
1. Wait for you to press ENTER
2. Send trigger signal to ESP32
3. ESP32 starts recording your voice
4. Auto-stops on silence (1 second)
5. Transcribes with Whisper
6. Executes command
7. Waits for next ENTER press

---

## Quick Test Commands

### Test text mode (no hardware needed):
```bash
python main.py
```
Then type commands like:
- `open chrome`
- `what's my battery level`
- `take a screenshot`

### Test manual trigger mode (with ESP32):
```bash
python manual_trigger.py
```
Then:
1. Press ENTER
2. Speak: "open chrome"
3. Wait for it to execute
4. Press ENTER again for next command

---

## Expected Output with Manual Trigger:

```
╔═════════════════════════════════════════════════════════╗
║       ESP32 Voice Assistant - MANUAL TRIGGER MODE       ║
╚═════════════════════════════════════════════════════════╝

📌 How to use:
   1. Press ENTER to start recording
   2. Speak your command clearly
   3. Stop speaking (silence auto-detected after 1s)
   4. Wait for transcription and execution
   5. Repeat!

[SERIAL] Opening COM6 at 115200 baud …
[SERIAL] Listening on COM6 …
[SERIAL] Wake word: ""
[SERIAL] Audio format: 16000 Hz, 16-bit, mono
[SERIAL] ⚡ MANUAL MODE: Press ENTER to start recording, then speak!
[SERIAL] Press Ctrl+C to stop.

▶ Press ENTER to record...
<you press ENTER>

🎤 [READY] Recording triggered! Speak now...
  [ESP32] 🎤 [TRIGGER] Manual recording started - speak now!
<you speak: "open chrome">
  [ESP32] ⏹  [RECORDING] Stopped. Waiting for transcription...

  [SERIAL] Received 24576 bytes of audio
  [WHISPER] Transcribed: "open chrome"
  [RAW]    "open chrome"

🤖 Assistant > Opening chrome …

▶ Press ENTER to record...
```

---

## 🎤 Speaking Tips:

- **Press ENTER first!** Then speak immediately
- **Distance:** 2-6 inches from microphone
- **Volume:** Normal speaking voice
- **Speed:** Speak clearly, don't rush
- **Stop:** Just stop speaking - silence will auto-detect

**Example workflow:**
1. Press ENTER → Wait for "🎤 [READY] Recording triggered!"
2. Speak: "open chrome"
3. Stop speaking
4. Wait 1 second (silence detection)
5. See transcription and execution
6. Press ENTER for next command

---

## ⚠️ Troubleshooting:

**Wake word not working?** → See `TROUBLESHOOTING_WHISPER.md`
**Commands not accurate?** → See `TROUBLESHOOTING_WHISPER.md`
**No audio received?** → See `INMP441_WIRING_TROUBLESHOOTING.md`

---

## Summary

**Manual Trigger Mode (Recommended):**
```bash
python manual_trigger.py
```
Press ENTER → Speak → Auto-stop → Execute → Repeat

**Original Continuous Mode:**
```bash
python main.py --serial
```
Auto-detects voice and records continuously

**NOT:**
```bash
python serial_listener.py  ❌
```
