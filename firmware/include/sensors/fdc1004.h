/**
 * fdc1004.h — FDC1004 capacitance-to-digital driver (I²C).
 * Datasheet: https://www.ti.com/lit/ds/symlink/fdc1004.pdf
 */
#pragma once
#include <stdint.h>
#include <stdbool.h>

bool  FDC1004_Init();
float FDC1004_ReadCapacitance();   // Returns capacitance in pF; NAN on error
