/**
 * temperature.h — DS18B20 1-Wire temperature sensor driver.
 */
#pragma once

bool  Temperature_Init();
float Temperature_ReadCelsius();    // Returns temperature in °C; NAN on error
