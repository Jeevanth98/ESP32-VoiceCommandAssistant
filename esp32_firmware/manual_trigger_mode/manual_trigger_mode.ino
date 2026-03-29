/*
 * ESP32 Voice Assistant - INMP441 I2S Microphone Audio Capture
 * MANUAL TRIGGER MODE - Press ENTER in Python app to start recording
 * ============================================================
 * Captures audio from INMP441 I2S MEMS microphone and sends it
 * to PC via serial for Whisper speech-to-text processing.
 * 
 * Hardware:
 *   - ESP32 DevKit
 *   - INMP441 I2S MEMS Microphone
 * 
 * Wiring (INMP441 -> ESP32):
 *   SCK  (Serial Clock)     -> GPIO 14
 *   WS   (Word Select/LRCK) -> GPIO 15  
 *   SD   (Serial Data)      -> GPIO 32
 *   L/R  (Channel Select)   -> GND (left channel)
 *   VDD  (Power)            -> 3.3V
 *   GND  (Ground)           -> GND
 * 
 * Serial Protocol (ESP32 -> PC):
 *   Header:  0xAA (1 byte)
 *   Length:  4 bytes (little-endian uint32) - payload size
 *   Payload: raw 16-bit PCM audio samples
 *   End:     0x55 (1 byte) - end of utterance marker
 * 
 * Serial Protocol (PC -> ESP32):
 *   'A' - Acknowledged
 *   'R' - Result/response follows
 *   'B' - Buzzer trigger
 *   'W' - Wake word detected, listening
 *   'S' - Start recording (manual trigger mode)
 */

#include <driver/i2s.h>

// ─── I2S Configuration ──────────────────────────────────────────────
#define I2S_WS            15    // Word Select (LRCK)
#define I2S_SD            32    // Serial Data (DOUT)
#define I2S_SCK           14    // Serial Clock (BCLK)
#define I2S_PORT          I2S_NUM_0

// Audio parameters (must match config.py)
#define SAMPLE_RATE       16000  // 16 kHz
#define BITS_PER_SAMPLE   16     // 16-bit
#define CHANNELS          1      // Mono

// ─── Serial Protocol ────────────────────────────────────────────────
#define SERIAL_BAUD       921600  // High-speed for audio streaming (was 115200)
#define HEADER_BYTE       0xAA
#define END_BYTE          0x55

// ─── Audio Buffer Settings ──────────────────────────────────────────
#define BUFFER_SIZE       512    // samples per read (32ms at 16kHz)
#define DMA_BUF_COUNT     8      // number of DMA buffers
#define DMA_BUF_LEN       1024   // length of each DMA buffer

// ─── Voice Activity Detection ───────────────────────────────────────
#define SILENCE_THRESHOLD 500    // amplitude threshold for silence
#define SILENCE_DURATION  1000   // ms of silence before ending utterance
#define MIN_UTTERANCE_MS  500    // minimum utterance length
#define MAX_RECORDING_MS  3000   // Maximum recording time (3 seconds)

// ─── LED Indicator (optional) ───────────────────────────────────────
#define LED_PIN           2      // Built-in LED on most ESP32 boards

// Global variables
int16_t audioBuffer[BUFFER_SIZE];
bool isRecording = false;
unsigned long lastSoundTime = 0;
unsigned long recordingStartTime = 0;
bool manualTriggerMode = true;  // Wait for 'S' command from PC to start recording

void setup() {
  Serial.begin(SERIAL_BAUD);
  while (!Serial) delay(10);
  
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  Serial.println("\n╔══════════════════════════════════════════╗");
  Serial.println("║  ESP32 Voice Assistant - INMP441 I2S     ║");
  Serial.println("╚══════════════════════════════════════════╝");
  Serial.print("  Sample Rate: "); Serial.print(SAMPLE_RATE); Serial.println(" Hz");
  Serial.print("  Bit Depth:   "); Serial.print(BITS_PER_SAMPLE); Serial.println("-bit");
  Serial.print("  Channels:    "); Serial.println(CHANNELS == 1 ? "Mono" : "Stereo");
  Serial.println();
  
  // Initialize I2S
  if (!initI2S()) {
    Serial.println("[ERROR] I2S initialization failed!");
    while (1) {
      digitalWrite(LED_PIN, !digitalRead(LED_PIN));
      delay(200);
    }
  }
  
  Serial.println("[READY] Waiting for manual trigger...");
  Serial.println("[INFO]  Press ENTER in the app to start recording\n");
}

void loop() {
  // Read audio samples from I2S
  size_t bytesRead = 0;
  esp_err_t result = i2s_read(I2S_PORT, audioBuffer, BUFFER_SIZE * sizeof(int16_t), 
                               &bytesRead, portMAX_DELAY);
  
  if (result != ESP_OK || bytesRead == 0) {
    return;
  }
  
  int samplesRead = bytesRead / sizeof(int16_t);
  
  // Check for voice activity
  bool hasSound = detectVoiceActivity(audioBuffer, samplesRead);
  
  // State machine for recording
  if (!isRecording && hasSound && !manualTriggerMode) {
    // Auto mode: Start recording on voice activity
    startRecording();
  }
  
  if (isRecording) {
    // Send audio chunk to PC
    sendAudioChunk(audioBuffer, samplesRead);
    
    if (hasSound) {
      lastSoundTime = millis();
    }
    
    // Check if utterance has ended (silence detected OR max time reached)
    unsigned long silenceDuration = millis() - lastSoundTime;
    unsigned long utteranceDuration = millis() - recordingStartTime;
    
    // Stop if: silence detected OR max recording time reached
    if ((silenceDuration > SILENCE_DURATION && utteranceDuration > MIN_UTTERANCE_MS) ||
        utteranceDuration >= MAX_RECORDING_MS) {
      // End of utterance
      if (utteranceDuration >= MAX_RECORDING_MS) {
        Serial.println("⏱  [TIMEOUT] Max recording time (3s) reached");
      }
      endRecording();
    }
  }
  
  // Check for responses from PC
  checkSerialResponse();
}

bool initI2S() {
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S_MSB,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = DMA_BUF_COUNT,
    .dma_buf_len = DMA_BUF_LEN,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
  };
  
  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD
  };
  
  esp_err_t err = i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
  if (err != ESP_OK) {
    Serial.printf("[ERROR] I2S driver install failed: %d\n", err);
    return false;
  }
  
  err = i2s_set_pin(I2S_PORT, &pin_config);
  if (err != ESP_OK) {
    Serial.printf("[ERROR] I2S set pin failed: %d\n", err);
    return false;
  }
  
  // Clear DMA buffers
  i2s_zero_dma_buffer(I2S_PORT);
  
  return true;
}

bool detectVoiceActivity(int16_t* samples, int count) {
  // Simple energy-based VAD
  int32_t energy = 0;
  for (int i = 0; i < count; i++) {
    int16_t sample = samples[i];
    energy += abs(sample);
  }
  
  int16_t avgEnergy = energy / count;
  return avgEnergy > SILENCE_THRESHOLD;
}

void startRecording() {
  isRecording = true;
  recordingStartTime = millis();
  lastSoundTime = millis();
  digitalWrite(LED_PIN, HIGH);
  Serial.println("🎤 [RECORDING] Started...");
}

void sendAudioChunk(int16_t* samples, int count) {
  uint32_t payloadSize = count * sizeof(int16_t);
  
  // Send header
  Serial.write(HEADER_BYTE);
  
  // Send payload size (4 bytes, little-endian)
  Serial.write((uint8_t)(payloadSize & 0xFF));
  Serial.write((uint8_t)((payloadSize >> 8) & 0xFF));
  Serial.write((uint8_t)((payloadSize >> 16) & 0xFF));
  Serial.write((uint8_t)((payloadSize >> 24) & 0xFF));
  
  // Send payload (audio samples)
  Serial.write((uint8_t*)samples, payloadSize);
  Serial.flush();
}

void endRecording() {
  // Send end-of-utterance marker
  Serial.write(END_BYTE);
  Serial.flush();
  
  isRecording = false;
  manualTriggerMode = true;  // Re-enable manual trigger mode
  digitalWrite(LED_PIN, LOW);
  Serial.println("⏹  [RECORDING] Stopped. Waiting for transcription...");
}

void checkSerialResponse() {
  while (Serial.available() > 0) {
    char cmd = Serial.read();
    
    switch (cmd) {
      case 'A':  // Acknowledged
        // PC is ready for more data
        break;
        
      case 'R':  // Result follows
        {
          delay(10);  // Wait for message length
          if (Serial.available() >= 2) {
            uint16_t msgLen = Serial.read() | (Serial.read() << 8);
            String response = "";
            
            unsigned long timeout = millis() + 1000;
            while (response.length() < msgLen && millis() < timeout) {
              if (Serial.available()) {
                response += (char)Serial.read();
              }
            }
            
            Serial.print("💬 [RESPONSE] ");
            Serial.println(response);
          }
        }
        break;
        
      case 'B':  // Buzzer trigger
        // Could add buzzer code here
        Serial.println("🔔 [BEEP] Notification!");
        break;
        
      case 'W':  // Wake word detected
        digitalWrite(LED_PIN, HIGH);
        delay(100);
        digitalWrite(LED_PIN, LOW);
        Serial.println("👂 [LISTENING] Wake word detected!");
        break;
        
      case 'S':  // Start recording (manual trigger)
        if (!isRecording) {
          Serial.println("🎤 [TRIGGER] Manual recording started - speak now!");
          startRecording();
          manualTriggerMode = false;  // Allow auto-stop on silence
        }
        break;
        
      default:
        // Unknown command
        break;
    }
  }
}
