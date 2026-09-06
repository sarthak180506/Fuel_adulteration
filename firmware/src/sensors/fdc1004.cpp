#include "sensors/fdc1004.h"
#include <Wire.h>

// FDC1004 I2C address
static constexpr uint8_t FDC1004_ADDR = 0x50;

bool FDC1004_Init() {
    Wire.begin();
    // TODO: verify device ID register (0xFF should return 0x1004)
    return true;
}

float FDC1004_ReadCapacitance() {
    // TODO: implement full FDC1004 register read sequence
    // 1. Write MEAS1 config register (0x08)
    // 2. Write FDC config register (0x0C) — trigger single measurement
    // 3. Poll done bit
    // 4. Read MSB (0x00) + LSB (0x01), combine and convert to pF
    return 0.0f;  // placeholder
}
