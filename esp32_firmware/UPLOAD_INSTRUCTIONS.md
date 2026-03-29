# 📤 Upload ESP32 Firmware - Step by Step

## ⚡ Quick Steps

### 1. Open Arduino IDE

### 2. Load the Firmware
- **Option A:** Open the file directly
  - Go to: `File` → `Open`
  - Navigate to: `E:\Projects\ESP32-VoiceCommandAssistant\esp32_firmware\`
  - Select: `manual_trigger_mode.ino`
  - Click `Open`

- **Option B:** Copy-paste the code
  - Open Arduino IDE
  - Create new sketch: `File` → `New`
  - Delete all default code
  - Copy ALL code from `manual_trigger_mode.ino`
  - Paste into Arduino IDE

### 3. Select Your ESP32 Board
- Go to: `Tools` → `Board` → `ESP32 Arduino`
- Select: **ESP32 Dev Module** (or your specific board)

### 4. Select the COM Port
- Go to: `Tools` → `Port`
- Select: **COM6** (or whatever port your ESP32 is on)
  - If you don't see COM6, check Device Manager (Windows)
  - Your ESP32 should show as "USB-SERIAL CH340" or similar

### 5. Upload the Firmware
- Click the **Upload** button (→ arrow icon)
- OR press `Ctrl+U`

### 6. Wait for Upload to Complete

You'll see:
```
Connecting........_____.....
Writing at 0x00001000... (3 %)
Writing at 0x00002000... (6 %)
...
Writing at 0x00010000... (100 %)
Leaving...
Hard resetting via RTS pin...
```

**✅ Success message:**
```
Done uploading.
```

### 7. Open Serial Monitor (Optional - for testing)
- Click the magnifying glass icon (top-right)
- OR press `Ctrl+Shift+M`
- Set baud rate to: **115200**

You should see:
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

### 8. **IMPORTANT:** Close Serial Monitor!

**Before running Python:**
- Close the Arduino Serial Monitor
- Only one program can use the COM port at a time

### 9. Run Python Script
```bash
python manual_trigger.py
```

---

## 🔧 Troubleshooting Upload Issues

### ❌ Error: "Port COM6 is busy" or "Permission denied"
**Solution:** Close Arduino Serial Monitor and any other programs using the port

### ❌ Error: "A fatal error occurred: Failed to connect"
**Solution:** Hold the **BOOT button** on ESP32 while uploading

**Steps:**
1. Click Upload in Arduino IDE
2. Wait for "Connecting........"
3. **Hold BOOT button** on ESP32
4. Keep holding until you see "Writing at 0x00010000"
5. Release BOOT button

### ❌ Error: "Sketch too big" or "Out of memory"
**Solution:** Add this line at the TOP of your sketch (before `#include`):
```cpp
#define CONFIG_BT_ENABLED 0
```

Then change partition scheme:
- `Tools` → `Partition Scheme` → `Minimal SPIFFS (1.9MB APP / 190KB SPIFFS)`

### ❌ Error: Can't find COM port
**Check:**
1. ESP32 is plugged in via USB
2. USB cable is data-capable (not charge-only)
3. Driver installed:
   - Windows: CH340 driver (Google "CH340 driver Windows")
   - Mac: Already built-in
   - Linux: Already built-in

### ❌ Upload completes but ESP32 doesn't work
**Solution:** Press the **RESET button** (EN) on ESP32

---

## ✅ Verify Upload Success

### Method 1: Check LED
- ESP32 built-in LED should be **OFF** (waiting mode)
- When you press ENTER in Python, LED turns **ON** (recording)
- After silence, LED turns **OFF** again

### Method 2: Check Serial Monitor
1. Open Arduino Serial Monitor (baud: 115200)
2. You should see:
   ```
   [READY] Waiting for manual trigger...
   [INFO]  Press ENTER in the app to start recording
   ```
3. **Close it before running Python!**

### Method 3: Run Python and Test
```bash
python manual_trigger.py
```

Expected output:
```
[SERIAL] Opening COM6 at 115200 baud …
[SERIAL] Listening on COM6 …
[SERIAL] ⚡ MANUAL MODE: Press ENTER to start recording, then speak!

▶ Press ENTER to record...
```

**Press ENTER** and you should see ESP32 respond!

---

## 📋 Quick Checklist

Before running Python, make sure:
- ✅ ESP32 firmware uploaded successfully
- ✅ Arduino Serial Monitor **CLOSED**
- ✅ ESP32 still connected to PC (COM6)
- ✅ ESP32 showing "Waiting for manual trigger..." (check Serial Monitor then close it)
- ✅ Virtual environment activated: `(.venv)` in your prompt

---

## 🎯 Next Steps

After successful upload:

1. **Close Arduino Serial Monitor**
2. **Run:** `python manual_trigger.py`
3. **Press ENTER** when prompted
4. **Speak** your command
5. **Wait** for transcription and execution

---

## 🆘 Still Having Issues?

### Quick Test - Does ESP32 Work?
Run this in Arduino Serial Monitor (baud 115200):
```
// Just watch the output - if you see the ready message, hardware is OK
```

### Python Can't Connect?
```bash
# Check if port is available
python -c "import serial; print(serial.Serial('COM6', 115200))"
```

If you see errors, COM6 is busy or wrong port.

### Need Help?
Check these files:
- `ARDUINO_TROUBLESHOOTING.md` - Compilation and upload errors
- `INMP441_WIRING_TROUBLESHOOTING.md` - Hardware wiring issues
- `MANUAL_TRIGGER_SETUP.md` - Manual trigger mode details
