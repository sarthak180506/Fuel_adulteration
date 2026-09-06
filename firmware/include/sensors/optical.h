/**
 * optical.h — BPW34 photodiode + IR LED optical transmittance driver.
 * Reads ADC, drives IR LED, returns normalised transmittance [0.0, 1.0].
 */
#pragma once
#include <stdint.h>

bool  Optical_Init();
float Optical_ReadTransmittance();  // Returns [0.0, 1.0]; NAN on error
