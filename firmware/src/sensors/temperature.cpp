#include "sensors/temperature.h"
#include "config.h"
#include <OneWire.h>
#include <DallasTemperature.h>

static OneWire          oneWire(PIN_ONE_WIRE);
static DallasTemperature sensors(&oneWire);

bool Temperature_Init() {
    sensors.begin();
    return sensors.getDeviceCount() > 0;
}

float Temperature_ReadCelsius() {
    sensors.requestTemperatures();
    float t = sensors.getTempCByIndex(0);
    if (t == DEVICE_DISCONNECTED_C) return NAN;
    return t;
}
