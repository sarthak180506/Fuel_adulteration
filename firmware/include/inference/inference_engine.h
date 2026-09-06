/**
 * inference_engine.h — TFLite-Micro inference wrapper.
 *
 * Loads the quantized INT8 model (either from a C array or SPIFFS),
 * runs the dual-head inference (classification + regression),
 * and returns results in physical units.
 */

#pragma once
#include <stdint.h>
#include <stdbool.h>

class InferenceEngine {
public:
    /**
     * Load model and allocate tensor arena.
     * @return true on success, false on allocation/model error.
     */
    bool Init();

    /**
     * Run inference on a normalised feature vector.
     * @param features  Pointer to float[4]: {cap_norm, opt_norm, temp_norm, tof_norm}
     * @param classLabel  Output: predicted class (0–4)
     * @param concentration  Output: predicted adulterant concentration (%)
     * @return true on success
     */
    bool RunInference(const float* features, int* classLabel, float* concentration);

    /** Return last inference latency in milliseconds. */
    uint32_t LastLatencyMs() const { return _lastLatencyMs; }

private:
    static constexpr size_t TENSOR_ARENA_SIZE = 50 * 1024;  // 50 KB
    uint8_t _tensorArena[TENSOR_ARENA_SIZE];
    uint32_t _lastLatencyMs = 0;
    bool _initialized = false;
};
