# 🎤 Manual Trigger Mode Setup

## What Changed?

**Before:** ESP32 automatically started recording when it detected sound
**Now:** ESP32 waits for you to press ENTER, then starts recording

---

## 🔧 Setup Steps

### Step 1: Upload New ESP32 Firmware

1. Open Arduino IDE
2. Open the firmware from `ESP32_SETUP.md` (lines 53-325)
3. **Important changes in the code:**
   - Added `manualTriggerMode` variable
   - ESP32 now waits for 'S' command from PC
   - Auto-stops on silence detection
4. Upload to your ESP32

**What you'll see in Serial Monitor:**
```
╔══════════════════════════════════════════╗
║  ESP32 Voice Assistant - INMP441 I2S     ║
╚══════════════════════════════════════════╝
  Sample Rate: 16000 Hz
  Bit Depth:   16-bit
  Channels:    Mono

[READY] Waiting for manual trigger...
[INFO]  Press ENTER in the app to start recording
```

---

### Step 2: Close Arduino Serial Monitor

**Important:** Close the Arduino Serial Monitor before running Python!

The serial port can only be used by one program at a time.

---

### Step 3: Run Manual Trigger Mode

```bash
python manual_trigger.py
```

---

## 📋 How to Use

### Simple Workflow:

1. **Press ENTER**
   ```
   ▶ Press ENTER to record...
   ```

2. **You'll see:**
   ```
   🎤 [READY] Recording triggered! Speak now...
   [ESP32] 🎤 [TRIGGER] Manual recording started - speak now!
   ```

3. **Speak your command:**
   - "open chrome"
   - "take a screenshot"
   - "what's my battery level"

4. **Stop speaking** (wait 1 second for silence detection)

5. **See the result:**
   ```
   [ESP32] ⏹  [RECORDING] Stopped. Waiting for transcription...
   [SERIAL] Received 24576 bytes of audio
   [WHISPER] Transcribed: "open chrome"
   🤖 Assistant > Opening chrome …
   ```

6. **Repeat:** Press ENTER for next command

---

## 🎯 Benefits of Manual Trigger Mode

✅ **No accidental recordings** - only records when you press ENTER
✅ **Better control** - you decide when to speak
✅ **Perfect for testing** - easy to test multiple commands
✅ **Less CPU usage** - only transcribes when needed
✅ **Cleaner logs** - no background noise transcription

---

## 🔄 Switch Back to Auto Mode

If you want the old behavior (auto-detect voice):

1. Edit ESP32 firmware line 119:
   ```cpp
   bool manualTriggerMode = false;  // Auto mode
   ```

2. Re-upload firmware

3. Run:
   ```bash
   python main.py --serial
   ```

---

## 🐛 Troubleshooting

### Issue: "Port already in use"
**Solution:** Close Arduino Serial Monitor

### Issue: Nothing happens when I press ENTER
**Checklist:**
1. ✅ ESP32 firmware uploaded?
2. ✅ Arduino Serial Monitor closed?
3. ✅ Correct COM port in config.py?
4. ✅ ESP32 showing "Waiting for manual trigger..."?

### Issue: Recording starts but no audio captured
**Solution:** Check INMP441 wiring (see INMP441_WIRING_TROUBLESHOOTING.md)

### Issue: Transcription is wrong
**Solution:** See TROUBLESHOOTING_WHISPER.md

---

## ⚙️ Advanced Configuration

### Change Silence Detection Time

Edit ESP32 firmware line 109:
```cpp
#define SILENCE_DURATION  1000   // 1 second (default)
// Change to:
#define SILENCE_DURATION  1500   // 1.5 seconds (more forgiving)
```

### Change Silence Threshold

Edit ESP32 firmware line 108:
```cpp
#define SILENCE_THRESHOLD 500    // Default
// Change to:
#define SILENCE_THRESHOLD 300    // More sensitive (picks up quieter voice)
// Or:
#define SILENCE_THRESHOLD 800    // Less sensitive (ignores background noise)
```

After changing, **re-upload firmware**.

---

## 📊 Expected Behavior

```
╔═════════════════════════════════════════════════════════╗
║       ESP32 Voice Assistant - MANUAL TRIGGER MODE       ║
╚═════════════════════════════════════════════════════════╝

[SERIAL] Opening COM6 at 115200 baud …
[SERIAL] Listening on COM6 …
[SERIAL] ⚡ MANUAL MODE: Press ENTER to start recording, then speak!

▶ Press ENTER to record...
<PRESS ENTER>

🎤 [READY] Recording triggered! Speak now...
  [ESP32] 🎤 [TRIGGER] Manual recording started - speak now!
<SAY: "open chrome">
  [ESP32] ⏹  [RECORDING] Stopped. Waiting for transcription...

  [SERIAL] Received 24576 bytes of audio
  [WHISPER] Transcribed: "open chrome"
  [RAW]    "open chrome"

🤖 Assistant > Opening chrome …

▶ Press ENTER to record...
<REPEAT>
```

---

## 🎤 Pro Tips

1. **Wait for the prompt** before speaking:
   ```
   🎤 [READY] Recording triggered! Speak now...
   ```

2. **Speak immediately** after seeing the prompt (don't wait too long)

3. **Speak clearly** - imagine you're talking to a friend 2 feet away

4. **One command at a time** - don't say multiple commands in one recording

5. **Let silence happen** - stop speaking and wait 1 second for auto-stop

6. **Check transcription** - look at the `[WHISPER] Transcribed:` line to see what it heard

---

## 🔄 Comparison: Manual vs Auto Mode

| Feature | Manual Trigger | Auto Mode |
|---------|---------------|-----------|
| **Activation** | Press ENTER | Voice detection |
| **Control** | ✅ Full control | ❌ Auto starts |
| **Accuracy** | ✅ Higher (no accidental recordings) | ⚠️ May record background |
| **CPU Usage** | ✅ Lower (on-demand) | ⚠️ Higher (continuous) |
| **Testing** | ✅ Perfect | ⚠️ Harder to test |
| **Hands-free** | ❌ Requires ENTER press | ✅ Fully hands-free |
| **Best For** | Testing, development | Production use |

**Recommendation:** Use **Manual Trigger** for testing, switch to **Auto Mode** for final deployment.

---

## 📝 Summary Commands

**Upload firmware:**
1. Copy code from ESP32_SETUP.md
2. Upload to ESP32
3. Close Serial Monitor

**Run manual trigger:**
```bash
python manual_trigger.py
```

**Use it:**
1. Press ENTER
2. Speak command
3. Wait for result
4. Repeat

**Enjoy!** 🎉
