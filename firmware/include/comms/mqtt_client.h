/**
 * mqtt_client.h — MQTT publish wrapper for Supabase / HiveMQ broker.
 *
 * Payload format (JSON):
 * {
 *   "device_id":       "FG-001",
 *   "timestamp_ms":    1234567890,
 *   "label_cls":       2,
 *   "label_name":      "Diesel-Adulterated Petrol",
 *   "concentration":   14.3,
 *   "temperature_c":   38.5,
 *   "cap_raw":         2.14,
 *   "opt_raw":         0.71
 * }
 */

#pragma once
#include <PubSubClient.h>

class MqttPublisher {
public:
    explicit MqttPublisher(PubSubClient& client) : _client(client) {}

    /**
     * Connect to MQTT broker.
     * @return true on success, false if connection fails.
     */
    bool Connect(const char* broker, uint16_t port, const char* topic);

    /**
     * Publish a reading. Reconnects automatically if connection dropped.
     */
    bool Publish(int classLabel, float concentration, float temp_c,
                  float cap_raw, float opt_raw);

    void Loop() { _client.loop(); }  // Call in main loop to keep connection alive

private:
    PubSubClient& _client;
    const char*   _topic   = nullptr;
    const char*   _broker  = nullptr;
    uint16_t      _port    = 1883;

    static const char* ClassLabelToName(int cls);
    bool Reconnect();
};
