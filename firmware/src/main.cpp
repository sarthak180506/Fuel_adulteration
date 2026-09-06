/**
 * FuelGuard — Main Firmware Entry Point
 * Target: ESP32 DevKit v1 / Arduino Framework
 *
 * Pipeline:
 *   1. Sensor acquisition (FDC1004 I²C, BPW34 ADC, DS18B20 1-Wire)
 *   2. Temperature compensation + normalisation
 *   3. TFLite-Micro inference (classification + regression)
 *   4. MQTT publish to Supabase broker
 *   5. OLED/Serial display of result
 */

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#include "config.h"
#include "sensors/fdc1004.h"
#include "sensors/optical.h"
#include "sensors/temperature.h"
#include "inference/inference_engine.h"
#include "inference/normalization.h"
#include "comms/mqtt_client.h"

// ── Globals ──────────────────────────────────────────────────────────────────
WiFiClient   wifiClient;
PubSubClient mqttClient(wifiClient);

InferenceEngine inferenceEngine;
MqttPublisher   mqttPublisher(mqttClient);

static uint8_t consecutiveFails = 0;

// ── Setup ────────────────────────────────────────────────────────────────────
void setup() {
    Serial.begin(115200);
    Serial.println(F("\n=== FuelGuard v1.0 ==="));

    // Sensor init
    FDC1004_Init();
    Optical_Init();
    Temperature_Init();

    // TFLite-Micro model init
    if (!inferenceEngine.Init()) {
        Serial.println(F("[ERROR] TFLite model init failed — halting"));
        while (true) delay(1000);
    }

    // Wi-Fi + MQTT (non-blocking: skip if offline)
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    uint8_t wifiAttempts = 0;
    while (WiFi.status() != WL_CONNECTED && wifiAttempts++ < 20) {
        delay(500);
        Serial.print('.');
    }
    if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("\n[WiFi] Connected: %s\n", WiFi.localIP().toString().c_str());
        mqttPublisher.Connect(MQTT_BROKER, MQTT_PORT, MQTT_TOPIC);
    } else {
        Serial.println(F("\n[WiFi] Offline mode — MQTT disabled"));
    }

    Serial.println(F("[Setup] Ready. Insert fuel sample."));
}

// ── Main loop ────────────────────────────────────────────────────────────────
void loop() {
    static uint32_t lastInference = 0;
    const  uint32_t INTERVAL_MS   = 2000;  // 2 s between inferences

    if (millis() - lastInference < INTERVAL_MS) return;
    lastInference = millis();

    // 1. Read raw sensors
    float cap_raw = FDC1004_ReadCapacitance();   // pF
    float opt_raw = Optical_ReadTransmittance();  // 0.0–1.0
    float temp_c  = Temperature_ReadCelsius();    // °C

    if (isnan(cap_raw) || isnan(opt_raw) || isnan(temp_c)) {
        Serial.println(F("[WARN] Sensor read failed — skipping"));
        consecutiveFails++;
        if (consecutiveFails > 5) {
            Serial.println(F("[ERROR] Persistent sensor failure"));
            // TODO: alert user via LED / buzzer
        }
        return;
    }
    consecutiveFails = 0;

    // 2. Temperature compensation + normalisation
    float features[4];
    NormalizeFeatures(cap_raw, opt_raw, temp_c, /*tof_raw=*/0.0f, features);

    // 3. Inference
    int   classLabel    = -1;
    float concentration = -1.0f;
    if (!inferenceEngine.RunInference(features, &classLabel, &concentration)) {
        Serial.println(F("[ERROR] Inference failed"));
        return;
    }

    // 4. Print result
    Serial.printf("[Result] Class=%d  Conc=%.1f%%  Temp=%.1f°C\n",
                  classLabel, concentration, temp_c);

    // 5. MQTT publish (skip if offline)
    if (WiFi.status() == WL_CONNECTED) {
        mqttPublisher.Publish(classLabel, concentration, temp_c,
                               cap_raw, opt_raw);
    }
}
