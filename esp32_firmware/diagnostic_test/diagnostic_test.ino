#define CONFIG_BT_ENABLED 0  // Disable Bluetooth to save memory

#include <driver/i2s.h>

// ─── I2S Configuration ──────────────────────────────────────────────
#define I2S_WS            15    // Word Select (LRCK)
#define I2S_SD            32    // Serial Data (DOUT)
#define I2S_SCK           14    // Serial Clock (BCLK)
#define I2S_PORT          I2S_NUM_0

// Audio parameters
#define SAMPLE_RATE       16000
#define BUFFER_SIZE       512

// Diagnostic settings
#define PRINT_INTERVAL    500   // Print audio levels every 500ms

int16_t audioBuffer[BUFFER_SIZE];
unsigned long lastPrintTime = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);  // Give serial time to initialize
  
  Serial.println("\n╔════════════════════════════════════════════════╗");
  Serial.println("║  ESP32 INMP441 Microphone Diagnostic Test     ║");
  Serial.println("╚════════════════════════════════════════════════╝");
  Serial.println();
  Serial.println("This will show you the actual audio levels");
  Serial.println("being read from the INMP441 microphone.");
  Serial.println();
  Serial.println("Expected behavior:");
  Serial.println("  - Silence: Levels near 0-100");
  Serial.println("  - Normal speech: Levels 500-5000+");
  Serial.println("  - Loud sounds: Levels 10000+");
  Serial.println();
  
  // Initialize I2S
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S_MSB,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = 1024,
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
    Serial.printf("❌ [ERROR] I2S driver install failed: %d\n", err);
    Serial.println("\nPossible causes:");
    Serial.println("  - GPIO pins already in use");
    Serial.println("  - Insufficient memory");
    Serial.println("\nESP32 will restart in 5 seconds...");
    delay(5000);
    ESP.restart();
  }
  
  err = i2s_set_pin(I2S_PORT, &pin_config);
  if (err != ESP_OK) {
    Serial.printf("❌ [ERROR] I2S set pin failed: %d\n", err);
    delay(5000);
    ESP.restart();
  }
  
  i2s_zero_dma_buffer(I2S_PORT);
  
  Serial.println("✅ I2S Initialized Successfully!");
  Serial.println();
  Serial.println("Wiring Check:");
  Serial.println("  INMP441 SCK  -> ESP32 GPIO 14");
  Serial.println("  INMP441 WS   -> ESP32 GPIO 15");
  Serial.println("  INMP441 SD   -> ESP32 GPIO 32");
  Serial.println("  INMP441 L/R  -> GND");
  Serial.println("  INMP441 VDD  -> 3.3V");
  Serial.println("  INMP441 GND  -> GND");
  Serial.println();
  Serial.println("🎤 Listening... Speak into the microphone!");
  Serial.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
  
  delay(1000);  // Let I2S settle
}

void loop() {
  // Read audio samples
  size_t bytesRead = 0;
  esp_err_t result = i2s_read(I2S_PORT, audioBuffer, BUFFER_SIZE * sizeof(int16_t), 
                               &bytesRead, portMAX_DELAY);
  
  if (result != ESP_OK || bytesRead == 0) {
    Serial.println("❌ I2S read error!");
    delay(1000);
    return;
  }
  
  int samplesRead = bytesRead / sizeof(int16_t);
  
  // Calculate audio statistics
  int32_t totalEnergy = 0;
  int16_t minSample = 32767;
  int16_t maxSample = -32768;
  
  for (int i = 0; i < samplesRead; i++) {
    int16_t sample = audioBuffer[i];
    totalEnergy += abs(sample);
    if (sample < minSample) minSample = sample;
    if (sample > maxSample) maxSample = sample;
  }
  
  int16_t avgEnergy = totalEnergy / samplesRead;
  int16_t peakToPeak = maxSample - minSample;
  
  // Print statistics every PRINT_INTERVAL ms
  if (millis() - lastPrintTime >= PRINT_INTERVAL) {
    lastPrintTime = millis();
    
    // Create visual bar graph
    int barLength = avgEnergy / 100;  // Scale for display
    if (barLength > 50) barLength = 50;
    
    Serial.print("Avg Energy: ");
    Serial.print(avgEnergy);
    Serial.print("\t");
    
    Serial.print("Peak-to-Peak: ");
    Serial.print(peakToPeak);
    Serial.print("\t");
    
    // Visual indicator
    Serial.print("[");
    for (int i = 0; i < barLength; i++) {
      Serial.print("█");
    }
    for (int i = barLength; i < 50; i++) {
      Serial.print(" ");
    }
    Serial.print("]");
    
    // Status indicator
    if (avgEnergy < 100) {
      Serial.print(" 🔇 Too quiet / No mic detected");
    } else if (avgEnergy < 500) {
      Serial.print(" 🔈 Quiet background noise");
    } else if (avgEnergy < 2000) {
      Serial.print(" 🔉 Normal speech detected");
    } else {
      Serial.print(" 🔊 LOUD - Good signal!");
    }
    
    Serial.println();
  }
}
