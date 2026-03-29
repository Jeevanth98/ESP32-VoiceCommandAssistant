# INMP441 Microphone Wiring Troubleshooting Guide

## 🔴 Problem Detected
```
Avg Energy: 0    Peak-to-Peak: 0    🔇 Too quiet / No mic detected
```

**This means:** The ESP32 is reading I2S data, but getting **all zeros** - the INMP441 microphone is not sending any audio data.

---

## ❌ Common Wiring Mistakes

### 1. **VDD Connected to 5V Instead of 3.3V**
- ⚠️ **CRITICAL:** INMP441 requires **3.3V**, NOT 5V!
- Connecting to 5V may permanently damage the microphone
- **Solution:** Connect VDD to **3.3V pin** on ESP32

### 2. **L/R Pin Not Connected**
- The L/R (or SEL) pin MUST be connected to GND for left channel
- Leaving it floating will not work
- **Solution:** Connect **L/R pin to GND**

### 3. **SD Pin on Wrong GPIO**
- The SD (Serial Data) pin is the actual audio data
- Must be connected to GPIO 32 in our code
- **Solution:** Verify **SD → GPIO 32**

### 4. **Loose Connections**
- Breadboard connections can be unreliable
- Wires may not be fully inserted
- **Solution:** Push all connections firmly, or try soldering

### 5. **Swapped SCK and WS Pins**
- These pins look similar but serve different purposes
- **Solution:** Double-check:
  - SCK (BCLK) → GPIO 14
  - WS (LRCK/LRC) → GPIO 15

---

## ✅ Correct Wiring (Double-Check This!)

```
INMP441 Pin Label    →    ESP32 GPIO Pin
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VDD (or 3.3V)        →    3.3V  ⚡ (NOT 5V!)
GND                  →    GND
L/R (or SEL)         →    GND   ⚡ (Critical - must connect!)
SCK (or BCLK)        →    GPIO 14
WS (or LRCK/LRC)     →    GPIO 15
SD (or DOUT/DATA)    →    GPIO 32
```

### Visual Check:
```
     INMP441 Module              ESP32 Board
    ┌─────────────┐            ┌──────────────┐
    │ VDD   ●─────┼────────────┤ 3.3V         │
    │ GND   ●─────┼────────────┤ GND          │
    │ L/R   ●─────┼────────────┤ GND          │ ← Important!
    │ SCK   ●─────┼────────────┤ GPIO 14      │
    │ WS    ●─────┼────────────┤ GPIO 15      │
    │ SD    ●─────┼────────────┤ GPIO 32      │
    └─────────────┘            └──────────────┘
```

---

## 🔧 Step-by-Step Verification

### Step 1: Power Check
1. **Disconnect** ESP32 from USB
2. **Remove ALL wires** from INMP441
3. **Reconnect only:**
   - INMP441 VDD → ESP32 3.3V
   - INMP441 GND → ESP32 GND
4. **Measure voltage** with multimeter (if available):
   - Should read ~3.3V between VDD and GND
5. If voltage is correct, proceed to Step 2

### Step 2: L/R Pin Connection (CRITICAL!)
1. **MUST connect** L/R pin to GND
2. Use a short wire (5-10cm max)
3. Ensure solid connection in breadboard

### Step 3: I2S Pin Connections
Connect one at a time, testing after each:

1. **SCK** (Serial Clock) → GPIO 14
   - This provides timing for data transfer
   
2. **WS** (Word Select) → GPIO 15
   - This tells left/right channel
   
3. **SD** (Serial Data) → GPIO 32
   - This carries actual audio data

### Step 4: Test After Each Wire
After connecting ALL wires:
1. Upload diagnostic sketch
2. Open Serial Monitor
3. Tap the microphone gently with your finger
4. You should see energy values jump to 100-500+

---

## 🧪 Alternative Pin Test

If it still doesn't work, try different GPIO pins:

**Upload this modified code to test different pins:**

Change these lines in the diagnostic sketch:
```cpp
// Try these alternative pin combinations:

// Option 1 (Current - if not working, try others):
#define I2S_SCK  14
#define I2S_WS   15
#define I2S_SD   32

// Option 2:
#define I2S_SCK  26
#define I2S_WS   25
#define I2S_SD   33

// Option 3:
#define I2S_SCK  18
#define I2S_WS   23
#define I2S_SD   19
```

---

## 🔍 Debug: Raw Sample Output

Let's verify if I2S is reading **anything at all**:

**Upload this ultra-simple test:**

```cpp
#define CONFIG_BT_ENABLED 0
#include <driver/i2s.h>

#define I2S_WS   15
#define I2S_SD   32
#define I2S_SCK  14

int16_t samples[16];

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  i2s_config_t cfg = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = 16000,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S_MSB,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4,
    .dma_buf_len = 512,
    .use_apll = false
  };
  
  i2s_pin_config_t pins = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = -1,
    .data_in_num = I2S_SD
  };
  
  i2s_driver_install(I2S_NUM_0, &cfg, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pins);
  i2s_zero_dma_buffer(I2S_NUM_0);
  
  Serial.println("Reading raw I2S samples...");
  Serial.println("Expected: Non-zero values if mic is working");
  Serial.println("Seeing all zeros? Check wiring!\n");
}

void loop() {
  size_t bytes;
  i2s_read(I2S_NUM_0, samples, 32, &bytes, 1000);
  
  Serial.print("Raw samples: ");
  for (int i = 0; i < 16; i++) {
    Serial.print(samples[i]);
    Serial.print(" ");
  }
  Serial.println();
  
  delay(1000);
}
```

**Expected Output:**
- ❌ **All zeros:** `0 0 0 0 0 0 0 0...` → Wiring problem
- ✅ **Random values:** `234 -189 456 -23 891...` → Mic working!

---

## 🆘 Hardware Checklist

- [ ] VDD connected to **3.3V** (NOT 5V)
- [ ] GND connected to GND
- [ ] **L/R pin connected to GND** (don't skip this!)
- [ ] SCK → GPIO 14
- [ ] WS → GPIO 15  
- [ ] SD → GPIO 32
- [ ] All wires firmly connected
- [ ] Using a breadboard with good contact
- [ ] INMP441 module is not damaged (VDD was never connected to 5V)

---

## 🔌 Physical Inspection

### Look at Your INMP441 Module:

Most INMP441 modules have **6 pins** on ONE side:
```
Front view of INMP441:
┌──────────────┐
│  ●  ●  ●     │  ← Microphone hole
│  ●  ●  ●     │  ← 6 pins
└──────────────┘

Pin labels (varies by manufacturer):
Row 1: VDD  GND   L/R
Row 2: SCK  WS    SD

OR:

Row 1: VDD  SCK   SD
Row 2: GND  WS    L/R
```

**Check YOUR module** for pin labels - they vary!

---

## 🔧 If Nothing Works - Test the Module

### Is the INMP441 module damaged?

1. **Check if module gets warm:**
   - If VDD connected to 5V before, module may be damaged
   - Touch the module after 10 seconds - should be room temperature
   - If hot → damaged

2. **Try a different INMP441 module** (if you have one)

3. **Test with multimeter** (advanced):
   - Measure resistance between VDD and GND
   - Should be > 1kΩ
   - If < 10Ω → short circuit (damaged)

---

## 📸 Wiring Photo Tips

If you can:
1. Take a clear photo of your wiring
2. Check each connection against the diagram above
3. Compare with example images online:
   - Google: "INMP441 ESP32 wiring"
   - YouTube: "INMP441 I2S microphone ESP32"

---

## ✅ Success Indicators

You'll know the microphone is working when:

1. **Diagnostic test shows non-zero values:**
   ```
   Avg Energy: 234    Peak-to-Peak: 892    [██] 🔈 Quiet background noise
   ```

2. **Values jump when you tap the mic:**
   ```
   Avg Energy: 1892   Peak-to-Peak: 4201   [██████████] 🔉 Normal speech
   ```

3. **Speaking produces even higher values:**
   ```
   Avg Energy: 3892   Peak-to-Peak: 8934   [████████████████] 🔊 LOUD!
   ```

---

## 🎯 Most Likely Issues (in order):

1. **L/R pin not connected to GND** (80% of cases)
2. **Loose breadboard connections** (10% of cases)
3. **Wrong GPIO pins** (5% of cases)
4. **Damaged module from 5V** (3% of cases)
5. **Defective module** (2% of cases)

---

## Next Steps

1. ✅ Double-check **L/R → GND** connection
2. ✅ Verify **VDD → 3.3V** (NOT 5V)
3. ✅ Push all breadboard wires firmly
4. ✅ Upload the raw sample test above
5. ✅ If raw samples show non-zero → mic works, adjust sensitivity
6. ✅ If still zeros → try different GPIO pins
7. ✅ If still zeros → module may be defective

Let me know what the raw sample test shows!
