/**
 * config.h — User configuration: Wi-Fi, MQTT, pin assignments, calibration.
 *
 * IMPORTANT: Copy this file to config_local.h and add your real credentials.
 * config_local.h is .gitignored. Never commit credentials.
 */

#pragma once

// ── Wi-Fi ────────────────────────────────────────────────────────────────────
#define WIFI_SSID       "YOUR_WIFI_SSID"
#define WIFI_PASSWORD   "YOUR_WIFI_PASSWORD"

// ── MQTT (Supabase Realtime or local broker) ─────────────────────────────────
#define MQTT_BROKER     "broker.example.com"
#define MQTT_PORT       1883
#define MQTT_TOPIC      "fuelguard/readings"
#define DEVICE_ID       "FG-001"

// ── Pin assignments ───────────────────────────────────────────────────────────
// FDC1004 (I²C)
#define PIN_SDA         21
#define PIN_SCL         22

// DS18B20 (1-Wire)
#define PIN_ONE_WIRE    4

// BPW34 optical (ADC input)
#define PIN_OPTICAL_ADC 34   // GPIO34 — ADC1_CH6 (input only)

// IR LED enable (digital output, active HIGH)
#define PIN_IR_LED      25

// ── Sampling parameters ───────────────────────────────────────────────────────
#define SAMPLE_RATE_HZ  10       // Acquisition rate
#define ROLLING_N       50       // Samples averaged per inference
#define REF_TEMP_C      30.0f    // Temperature compensation reference

// ── Model flash storage ───────────────────────────────────────────────────────
// If model is stored in SPIFFS/LittleFS rather than as a C array:
// #define MODEL_FILE_PATH  "/model.tflite"
