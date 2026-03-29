# 🎤 Wake Word & Transcription Troubleshooting

## 🔴 Common Issues

### Issue 1: Wake Word Not Working

**Symptoms:**
- Commands don't execute
- Wake word "hey assistant" not detected

**Root Causes & Solutions:**

#### A) Whisper is transcribing incorrectly
The wake word detection looks for **exact text match**: `"hey assistant"` in the transcribed text.

**Test what Whisper is hearing:**
1. When you run `python main.py --serial`
2. Speak into the mic
3. Look for this line in the output:
   ```
   [WHISPER] Transcribed: "your text here"
   ```

**Common transcription mistakes:**
- "hey assistant" → "a system"
- "hey assistant" → "hey assistance" 
- "hey assistant" → "a assistant"
- Background noise confusing Whisper

**Solutions:**
- Speak **clearly** and **close to the microphone** (2-6 inches)
- Say the wake word **slower** with a slight pause: "Hey ... Assistant"
- Reduce background noise (turn off TV, fans, etc.)
- Try upgrading Whisper model (see below)

---

#### B) Wake word requirement is too strict

**Current behavior:**
- **Must say:** "hey assistant" + command in **one utterance**
- **Example:** "hey assistant turn on the lights"

**If you pause after "hey assistant":**
- ESP32 sends first part → Whisper transcribes "hey assistant"
- System responds: "Wake word detected — waiting for command"
- You must say the **full command again** including wake word

**Workaround:**
Say wake word + command **without pausing**:
```
"hey assistant open chrome"  ✅
"hey assistant ... [pause] ... open chrome"  ❌
```

**Better Solution - Disable Wake Word:**
Edit `config.py` line 106:
```python
WAKE_WORD = ""  # Disabled - process every command
```

Now any speech will be processed without wake word!

---

### Issue 2: Commands Not Captured Exactly

**Symptoms:**
- You say "open chrome" → Whisper hears "open room"
- You say "take screenshot" → Whisper hears "cake screen shot"

**Root Causes:**

#### A) Using "base" Whisper model (default)
The "base" model is fast but less accurate.

**Check your model:**
```python
# In config.py line 109
WHISPER_MODEL = "base"  # Current
```

**Model Comparison:**

| Model  | Size  | Speed       | Accuracy | Recommendation |
|--------|-------|-------------|----------|----------------|
| tiny   | 39 MB | Very Fast   | Poor     | ❌ Too inaccurate |
| base   | 74 MB | Fast        | OK       | ⚠️ Current (mediocre) |
| small  | 244 MB| Medium      | Good     | ✅ **RECOMMENDED** |
| medium | 769 MB| Slow        | Great    | ✅ For high accuracy |
| large  | 1.5 GB| Very Slow   | Best     | 💻 Requires GPU |

**Upgrade to "small" model:**
1. Edit `config.py` line 109:
   ```python
   WHISPER_MODEL = "small"  # Much better accuracy
   ```

2. First run will download the model (244 MB)
3. Transcription will be more accurate but ~2-3x slower

---

#### B) Poor audio quality from ESP32

**Check audio level in output:**
When ESP32 sends audio, you should see:
```
[SERIAL] Received 32768 bytes of audio
```

**Minimum:** 8,000 bytes (0.5 seconds)
**Ideal:** 16,000-64,000 bytes (1-4 seconds)

**If too short (<8000 bytes):**
- Speak louder
- Move mic closer to your mouth
- Adjust `SILENCE_THRESHOLD` in ESP32 firmware (see below)

**If you see debug messages from ESP32:**
```
[ESP32] [ERROR] I2S read failed
[ESP32] Avg Energy: 0
```
→ Hardware problem (see INMP441_WIRING_TROUBLESHOOTING.md)

---

#### C) ESP32 VAD (Voice Activity Detection) cutting off speech

The ESP32 stops recording after 1 second of silence.

**Check ESP32_SETUP.md firmware line 60:**
```cpp
#define SILENCE_THRESHOLD 500    // amplitude threshold
#define SILENCE_DURATION  1000   // ms of silence before ending
```

**If commands are cut short, increase SILENCE_DURATION:**
```cpp
#define SILENCE_DURATION  1500   // 1.5 seconds (more forgiving)
```

**If it's recording too much background noise:**
```cpp
#define SILENCE_THRESHOLD 800    // Higher = less sensitive
```

After changing, **re-upload firmware** to ESP32.

---

## 🔧 Quick Fixes Summary

### Fix 1: Disable Wake Word (Easiest)
```python
# config.py line 106
WAKE_WORD = ""
```
Now every command is processed immediately!

### Fix 2: Upgrade Whisper Model (Best)
```python
# config.py line 109
WHISPER_MODEL = "small"  # or "medium" for best quality
```

### Fix 3: Speak Correctly
- **Close to mic:** 2-6 inches
- **Clear & steady:** Don't rush
- **One phrase:** "hey assistant open chrome" (no pause)
- **Quiet environment:** Reduce background noise

### Fix 4: Adjust ESP32 Sensitivity
```cpp
// ESP32_SETUP.md firmware
#define SILENCE_DURATION  1500   // Give more time
#define SILENCE_THRESHOLD 600    // Adjust to your voice
```

---

## 🧪 Testing & Debugging

### Test 1: Check what Whisper is hearing
```bash
python main.py --serial
```

Watch for these lines:
```
[SERIAL] Received 32768 bytes of audio
[WHISPER] Transcribed: "hey assistant open chrome"
[RAW]    "open chrome"
```

**The transcribed text should match what you said!**

### Test 2: Test Whisper with a WAV file
Create a test WAV file with your voice, then:
```python
from stt.whisper_stt import transcribe_wav_file
text = transcribe_wav_file("test_audio.wav")
print(text)
```

If this is wrong too → Whisper model issue (upgrade model)
If this is correct → ESP32 audio quality issue

### Test 3: Check ESP32 is sending audio
Look for:
```
[SERIAL] Received 32768 bytes of audio  ✅ Good (2 seconds)
[SERIAL] Received 8192 bytes of audio   ⚠️ Short (0.5 seconds)
[SERIAL] Received 0 bytes of audio      ❌ Problem!
```

---

## 🎯 Recommended Configuration

**For Best Results:**

1. **config.py:**
   ```python
   WAKE_WORD = ""           # Disable wake word for testing
   WHISPER_MODEL = "small"  # Better accuracy
   ```

2. **ESP32 firmware (ESP32_SETUP.md):**
   ```cpp
   #define SILENCE_THRESHOLD 500    // Keep default
   #define SILENCE_DURATION  1500   // Increase to 1.5s
   ```

3. **Speaking style:**
   - Mic distance: 2-6 inches
   - Volume: Normal speaking voice
   - Speed: Don't rush
   - Environment: Quiet room

4. **Restart:**
   ```bash
   # Re-upload ESP32 firmware if you changed it
   # Then restart Python:
   python main.py --serial
   ```

---

## 📊 Expected Behavior (After Fixes)

```
[SERIAL] Opening COM6 at 115200 baud …
[SERIAL] Listening on COM6 …
[SERIAL] Wake word: ""  ← Empty if disabled
[SERIAL] Press Ctrl+C to stop.

  [SERIAL] Received 24576 bytes of audio
  [WHISPER] Loading Whisper 'small' model …  ← First time only
  [WHISPER] Model loaded (device: cpu).
  [WHISPER] Transcribed: "open chrome"
  [RAW]    "open chrome"

🤖 Assistant > Opening chrome …

```

---

## 🆘 Still Not Working?

1. **Check ESP32 is sending audio:**
   - Look for `[SERIAL] Received XXXXX bytes`
   - If you see 0 bytes → Hardware issue (check INMP441_WIRING_TROUBLESHOOTING.md)

2. **Check Whisper is installed:**
   ```bash
   pip list | findstr whisper
   # Should show: openai-whisper
   ```

3. **Try manual test:**
   ```bash
   python
   >>> from stt.whisper_stt import transcribe_wav_file
   >>> # If this import fails, Whisper isn't installed
   ```

4. **Check for errors:**
   Run with error details:
   ```bash
   python main.py --serial 2>&1 | tee debug.log
   ```

---

## 🎤 Alternative: Test Without Hardware

Test Whisper + NLU without ESP32:
```bash
python main.py
```

Type commands directly:
```
> open chrome
> what's my battery level
> take a screenshot
```

If this works but serial mode doesn't → ESP32 audio issue
If this doesn't work → NLU/command handler issue
