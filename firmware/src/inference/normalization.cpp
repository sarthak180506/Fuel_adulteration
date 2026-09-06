#include "inference/normalization.h"
#include "config.h"
#include <math.h>

// Default calibration constants (overwritten by LoadCalibration from SPIFFS)
float FEAT_MIN[N_FEATURES]   = {1.75f, 0.28f, 30.0f, 198.0f};
float FEAT_MAX[N_FEATURES]   = {2.20f, 0.93f, 45.0f, 230.0f};
float REF_TEMP               = REF_TEMP_C;
float TEMP_COEFF_CAP         = 0.002f;
float TEMP_COEFF_OPT         = 0.001f;

bool LoadCalibration() {
    // TODO: open /calibration.json from SPIFFS and parse with ArduinoJson
    // Falls back to compile-time defaults above if file not found
    return true;
}

void NormalizeFeatures(float cap_raw, float opt_raw, float temp_c,
                        float tof_raw, float out[N_FEATURES]) {
    // 1. Joint temperature compensation
    float dt      = temp_c - REF_TEMP;
    float cap_comp = cap_raw / (1.0f + TEMP_COEFF_CAP * dt);
    float opt_comp = opt_raw / fmaxf(1.0f - TEMP_COEFF_OPT * dt, 0.01f);

    float raw[N_FEATURES] = {cap_comp, opt_comp, temp_c, tof_raw};

    // 2. Min-max normalisation → [0, 1]
    for (int i = 0; i < N_FEATURES; i++) {
        float range = FEAT_MAX[i] - FEAT_MIN[i];
        if (range < 1e-6f) { out[i] = 0.0f; continue; }
        out[i] = (raw[i] - FEAT_MIN[i]) / range;
        // Clamp to [0, 1]
        if (out[i] < 0.0f) out[i] = 0.0f;
        if (out[i] > 1.0f) out[i] = 1.0f;
    }
}
