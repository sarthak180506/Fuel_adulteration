#include "comms/mqtt_client.h"
#include "config.h"
#include <ArduinoJson.h>
#include <Arduino.h>

static const char* CLASS_NAMES[] = {
    "Pure Fuel",
    "Kerosene-Adulterated Petrol",
    "Diesel-Adulterated Petrol",
    "Kerosene-Adulterated Diesel",
    "Water-Adulterated Diesel",
};

const char* MqttPublisher::ClassLabelToName(int cls) {
    if (cls < 0 || cls > 4) return "Unknown";
    return CLASS_NAMES[cls];
}

bool MqttPublisher::Connect(const char* broker, uint16_t port, const char* topic) {
    _broker = broker;
    _port   = port;
    _topic  = topic;
    _client.setServer(broker, port);
    return Reconnect();
}

bool MqttPublisher::Reconnect() {
    if (_client.connected()) return true;
    String clientId = String("FuelGuard-") + String(DEVICE_ID);
    return _client.connect(clientId.c_str());
}

bool MqttPublisher::Publish(int classLabel, float concentration,
                             float temp_c, float cap_raw, float opt_raw) {
    if (!Reconnect()) return false;

    JsonDocument doc;
    doc["device_id"]    = DEVICE_ID;
    doc["timestamp_ms"] = millis();
    doc["label_cls"]    = classLabel;
    doc["label_name"]   = ClassLabelToName(classLabel);
    doc["concentration"] = concentration;
    doc["temperature_c"] = temp_c;
    doc["cap_raw"]      = cap_raw;
    doc["opt_raw"]      = opt_raw;

    char buf[256];
    serializeJson(doc, buf);
    return _client.publish(_topic, buf);
}
