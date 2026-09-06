#include "sensors/optical.h"
#include "config.h"
#include <Arduino.h>

bool Optical_Init() {
    pinMode(PIN_IR_LED, OUTPUT);
    digitalWrite(PIN_IR_LED, LOW);
    return true;
}

float Optical_ReadTransmittance() {
    // Turn IR LED on, read ADC, turn off
    digitalWrite(PIN_IR_LED, HIGH);
    delayMicroseconds(100);
    int raw = analogRead(PIN_OPTICAL_ADC);   // 0–4095 (12-bit ESP32 ADC)
    digitalWrite(PIN_IR_LED, LOW);
    // Normalise to [0.0, 1.0]
    return static_cast<float>(raw) / 4095.0f;
}
