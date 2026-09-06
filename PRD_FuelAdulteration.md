# Product Requirements Document
# FuelGuard — Multimodal Fuel Adulteration Detection System

**Version:** 1.0  
**Date:** September 2026  
**Status:** Draft  
**Author:** Research Team  

---

## 1. Executive Summary

FuelGuard is an edge-deployed, multimodal sensor fusion system for real-time detection and quantification of fuel adulteration at the point of sale. It combines capacitive/dielectric sensing, optical transmittance sensing, and temperature measurement into a single fused feature vector, processed by a quantized on-device ML model running on an ESP32 microcontroller. The system outputs both an adulteration classification label (fuel type) and a precise adulterant concentration estimate (%), without requiring cloud connectivity for inference.

---

## 2. Problem Statement

### 2.1 Background
Fuel adulteration — the mixing of cheaper substances (kerosene, diesel, water) into petrol or diesel — is a widespread and economically damaging problem in India and other developing markets. Current detection methods are either:
- **Laboratory-based** (GC-MS, NIR spectroscopy): accurate but slow, expensive, and inaccessible at point-of-sale.
- **Single-sensor embedded devices**: limited to pure/adulterated binary classification; fail at low adulteration levels (<10%) or under temperature variation.
- **Regulatory inspection**: infrequent, not real-time, easily gamed.

### 2.2 Gap Being Addressed
No existing commercial or research device provides:
1. Multi-sensor fusion (≥3 modalities) in a single embedded pipeline.
2. On-device **concentration regression** (not just binary classification).
3. **Joint temperature compensation** across all channels.
4. Edge deployment on a sub-₹800 microcontroller.

---

## 3. Goals & Non-Goals

### Goals
- Detect adulteration of petrol/diesel with kerosene and diesel/petrol (cross-contamination).
- Classify adulterant type (kerosene, diesel, water).
- Estimate adulterant concentration with ±3% accuracy in the 2–30% range.
- Compensate all sensor readings for ambient/fuel temperature (30–45°C range).
- Run inference entirely on-device (ESP32, no cloud round-trip).
- Transmit timestamped results to a Supabase dashboard via MQTT over Wi-Fi.
- Produce a publishable IEEE-style paper and a provisional patent filing.

### Non-Goals (Out of Scope for v1.0)
- Fiber-optic, SPR, or metamaterial sensing (requires fabrication infrastructure).
- GC-MS or spectroscopic reference validation (outsource to external lab for a few samples).
- Regulatory certification (GATC/Legal Metrology Act pathway — future work).
- Detection of adulteration below 2% concentration.
- Multi-fuel simultaneous sampling.
- Battery-powered portable form factor (v2.0 target).

---

## 4. Target Users

| User | Context | Core Need |
|---|---|---|
| **Fuel station inspector** | On-site at a pump, checking a single dispenser | Quick pass/fail result + concentration reading in <30 sec |
| **Regulatory officer** | Spot-check audits under Legal Metrology Act | Timestamped, logged, exportable evidence |
| **Research/academic user** | Lab calibration and dataset collection | Raw sensor readings + ML confidence scores |
| **Fleet manager** | Checking bulk fuel before accepting delivery | API-accessible result for integration with ERP |

---

## 5. System Architecture

```
                    FUEL SAMPLE CHAMBER
               (sealed, vented, PTFE-lined)
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
  Capacitive Cell   Optical Cell     DS18B20
  (FDC1004/AD7746)  (IR LED+BPW34)  (Temperature)
        │                │                │
        └────────────────┼────────────────┘
                         ↓
              ESP32 — ADC / I²C Acquisition
                         ↓
              On-device Normalization +
              Joint Temperature Compensation
                         ↓
              TFLite-Micro Fusion Model
              (Quantized MLP / 1D-CNN)
                         ↓
        ┌────────────────┴────────────────┐
        ↓                                 ↓
  Classification Label            Concentration Estimate
  (pure / kerosene / diesel /      (regression output, %)
   water adulteration)
        └────────────────┬────────────────┘
                         ↓
           MQTT → Supabase → Web Dashboard
                  (timestamped audit log)
```

---

## 6. Functional Requirements

### 6.1 Sensing Layer

| ID | Requirement | Priority |
|---|---|---|
| FR-S1 | System SHALL measure capacitance of fuel sample using FDC1004 or AD7746 at I²C | P0 |
| FR-S2 | System SHALL measure optical transmittance using IR LED + BPW34 photodiode pair | P0 |
| FR-S3 | System SHALL measure in-fluid temperature using DS18B20 (1-Wire) | P0 |
| FR-S4 | System MAY measure ultrasonic time-of-flight as density proxy (optional, deprioritize if noisy) | P2 |
| FR-S5 | Sample chamber SHALL be constructed of PTFE-lined, fuel-inert, spark-safe materials | P0 |
| FR-S6 | All sensors SHALL be isolated from RF interference via proper grounding | P1 |

### 6.2 Signal Processing Layer

| ID | Requirement | Priority |
|---|---|---|
| FR-P1 | ESP32 SHALL acquire all sensor readings at ≥10 Hz sampling rate | P0 |
| FR-P2 | System SHALL apply joint temperature compensation across ALL sensor channels before feature extraction | P0 |
| FR-P3 | System SHALL normalize all features to [0,1] range using pre-calibrated min/max values stored in flash | P0 |
| FR-P4 | System SHALL aggregate N=50 samples into a stable feature vector (rolling average) | P1 |

### 6.3 Inference Layer

| ID | Requirement | Priority |
|---|---|---|
| FR-M1 | On-device model SHALL classify fuel into: {Pure Petrol, Kerosene-Adulterated Petrol, Diesel-Adulterated Petrol, Pure Diesel, Water-Adulterated Diesel} | P0 |
| FR-M2 | On-device model SHALL output adulterant concentration as a regression value (0–100%) | P0 |
| FR-M3 | Model SHALL run inference in <500 ms on ESP32 (TFLite-Micro INT8 quantized) | P0 |
| FR-M4 | Model SHALL be trained offline on scikit-learn; winning model converted to TFLite | P0 |
| FR-M5 | System SHALL compare SVM, Random Forest, XGBoost, MLP baselines in offline evaluation | P1 |
| FR-M6 | Classification accuracy SHALL be ≥90% across all adulterant types at ≥5% concentration | P0 |
| FR-M7 | Concentration regression error SHALL be ≤±3% (RMSE) in the 5–30% range | P0 |

### 6.4 Connectivity & Dashboard Layer

| ID | Requirement | Priority |
|---|---|---|
| FR-C1 | ESP32 SHALL publish results to MQTT broker over Wi-Fi within 2 seconds of inference | P1 |
| FR-C2 | Supabase backend SHALL store timestamped records: {timestamp, fuel_type, adulterant_type, concentration_pct, temperature_C, raw_capacitance, raw_optical, device_id} | P1 |
| FR-C3 | Web dashboard SHALL display live adulteration status, concentration gauge, and historical chart | P1 |
| FR-C4 | Dashboard SHALL allow CSV export of audit log | P2 |
| FR-C5 | System SHALL operate in offline mode (local inference, no MQTT) if Wi-Fi unavailable | P1 |

---

## 7. Non-Functional Requirements

| ID | Requirement | Target |
|---|---|---|
| NFR-1 | **Inference latency** | <500 ms on ESP32 (no cloud round-trip) |
| NFR-2 | **Classification accuracy** | ≥90% across all classes at ≥5% adulteration |
| NFR-3 | **Concentration RMSE** | ≤±3% in 5–30% range |
| NFR-4 | **Temperature range** | Accurate operation 30–45°C (Indian ambient conditions) |
| NFR-5 | **Startup time** | <5 seconds from power-on to ready state |
| NFR-6 | **Bill of materials cost** | <₹3,500 total (sensor BOM only, excluding enclosure) |
| NFR-7 | **Model RAM footprint** | <200 KB (ESP32 has 520 KB SRAM) |
| NFR-8 | **Sample test time** | <30 seconds from sample insertion to result display |
| NFR-9 | **Safety** | All electrical components isolated from fuel vapor; no ignition sources near sample |
| NFR-10 | **Reproducibility** | Results repeatable across 3 independent runs of same sample with <2% variation |

---

## 8. Dataset & Experiment Design

### 8.1 Sample Matrix

| Fuel Base | Adulterant | Concentrations (%) |
|---|---|---|
| Commercial Petrol | Kerosene | 0, 2, 5, 10, 15, 20, 25, 30 |
| Commercial Petrol | Diesel | 0, 2, 5, 10, 15, 20, 25, 30 |
| Commercial Diesel | Kerosene | 0, 2, 5, 10, 15, 20, 25, 30 |
| Commercial Diesel | Water | 0, 1, 2, 5, 10 |

- **Temperature range:** 30°C, 35°C, 40°C, 45°C (controlled water bath or ambient)
- **Replicates:** 3 per (fuel, adulterant, concentration, temperature) combination
- **Total samples:** ~300–400 labeled readings

### 8.2 Experiment Structure

| Experiment | Description | Goal |
|---|---|---|
| **A — Single sensor baselines** | Capacitive only, optical only, temperature only | Establish individual modality limits |
| **B — Pairwise fusion** | Capacitive+optical, capacitive+temp, optical+temp | Quantify fusion gain over single sensor |
| **C — Full fusion** | All 3 (or 4) modalities | Primary result: classification + regression |
| **D — Edge deployment** | TFLite-Micro inference on ESP32 | Latency, RAM, accuracy post-quantization |

### 8.3 Validation Split
- 70% train / 15% validation / 15% test
- Stratified by adulterant type and concentration
- External validation: 5 samples sent to external lab for GC-MS cross-check

---

## 9. Bill of Materials (Sensor BOM)

| Component | Purpose | Estimated Cost (INR) |
|---|---|---|
| FDC1004 module (or AD7746) | Capacitance-to-digital converter | ₹400–600 |
| PTFE parallel-plate capacitor cell | Fuel-inert dielectric sensing chamber | ₹200–400 (custom) |
| IR LED (850 nm) + BPW34 photodiode | Optical transmittance sensing pair | ₹80–120 |
| DS18B20 (stainless steel waterproof) | In-fluid temperature measurement | ₹60–100 |
| HC-SR04 / JSN-SR04T *(optional)* | Ultrasonic ToF density proxy | ₹100–150 |
| ESP32 DevKit v1 | Acquisition, inference, connectivity | ₹400–500 |
| PTFE-lined sample chamber + fittings | Fuel-safe enclosure | ₹500–800 |
| Misc (resistors, wiring, PCB) | Signal conditioning | ₹200–300 |
| **Total** | | **~₹1,940–2,970** |

> [!NOTE]
> Well within the <₹3,500 BOM target. Budget the remainder for 3D-printed enclosure parts and lab safety consumables.

---

## 10. ML Pipeline

### 10.1 Offline Training (Python / scikit-learn)

```
Raw CSV (sensor readings + labels)
        ↓
Preprocessing: outlier removal, per-temperature normalization
        ↓
Feature vector: [C_norm, I_norm, T_norm, (ToF_norm?)]
        ↓
Model comparison:
  ├── SVM (RBF kernel)
  ├── Random Forest (100 trees)
  ├── XGBoost
  ├── MLP (2–3 hidden layers)
  └── 1D-CNN (only if tabular models plateau)
        ↓
Evaluation: accuracy, F1, confusion matrix (classification)
             RMSE, R² (concentration regression)
        ↓
Winner → TFLite conversion → INT8 post-training quantization
        ↓
Deploy to ESP32 flash
```

### 10.2 On-Device Inference (C++ / TFLite-Micro)

```cpp
// Pseudocode
float features[4] = {cap_norm, opt_norm, temp_norm, (tof_norm)};
tflite_model.SetInput(features);
tflite_model.Invoke();
int   class_label  = argmax(tflite_model.GetOutput(0));
float concentration = tflite_model.GetOutput(1)[0];
```

---

## 11. Development Phases & Timeline

| Phase | Duration | Deliverable |
|---|---|---|
| **Phase 0** — Literature & IP freeze | 2–3 weeks | Formal patent search (IP India, WIPO, Espacenet); locked claim scope |
| **Phase 1** — Single-sensor baselines | 4–5 weeks | Capacitive + optical cells built, calibrated; Experiment A dataset collected; baseline paper section |
| **Phase 2** — Fusion pipeline | 4–6 weeks | Full feature-fusion model trained; Experiments B & C results; confusion matrices; RMSE curves |
| **Phase 3** — Edge deployment | 3–4 weeks | TFLite-Micro model on ESP32; latency + RAM benchmarks; MQTT → Supabase → dashboard live |
| **Phase 4** — Writing + IP filing | 3–4 weeks (parallel) | Provisional patent filed; IEEE paper submitted |

> [!IMPORTANT]
> File the provisional patent application **before** submitting or presenting the paper publicly. Filing date = priority date.

---

## 12. IP & Patent Scope

### What Will Be Claimed

| Claim | Description |
|---|---|
| **Claim 1 (System)** | Combination of ≥3 named, non-redundant sensing modalities (capacitive + optical + temperature) fused into a single feature vector |
| **Claim 2 (Method)** | Joint temperature compensation applied across all fused channels simultaneously before feature extraction |
| **Claim 3 (Edge AI)** | Quantized on-device model outputting both classification label AND concentration regression on microcontroller-class hardware |
| **Claim 4 (Dependent)** | MQTT-based IoT reporting pipeline with timestamped audit log |

### Filing Path
1. Institution IP/TT cell → Provisional Application (Form 1 + Form 2)
2. 12-month window to convert to complete specification
3. Optional: PCT filing for international priority

---

## 13. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Density/ToF sensor adds noise, not signal | Medium | Medium | Drop to 2-modality system; 2 clean modalities > 3 noisy ones |
| Capacitive cell design infringes existing patent | Low-Medium | High | Formal novelty search before building; differentiate via fusion (not standalone capacitive sensor) |
| Sample safety incident (petrol vapors) | Low | Critical | Vent sample chamber; no ignition sources; loop in lab safety officer before Phase 1 |
| Timeline slip at Phase 2 (fusion tuning) | High | Medium | Keep Phase 1 baselines demo-ready as fallback deliverable at any point |
| Overclaiming novelty in paper | Medium | Medium | Explicitly cite and position against every prior-art sensor type in §1 of the roadmap |
| Temperature compensation insufficient | Low | High | Calibrate at 4 temperature points minimum; validate on held-out temperature samples |

---

## 14. Success Criteria

| Metric | Threshold (Minimum) | Target (Stretch) |
|---|---|---|
| Classification accuracy | ≥90% (all classes, ≥5% adulteration) | ≥97% |
| Concentration RMSE | ≤±3% (5–30% range) | ≤±1.5% |
| On-device inference latency | <500 ms | <100 ms |
| Model RAM footprint | <200 KB | <100 KB |
| Lowest detectable concentration | ≤5% | ≤2% |
| Paper submission | 1 IEEE/Scopus conference or journal | 1 Q1 journal |
| IP filing | Provisional filed before paper submission | Complete specification filed within 12 months |

---

## 15. Appendix — Glossary

| Term | Definition |
|---|---|
| **Adulteration** | Mixing of a cheaper/inferior substance into a fuel to fraudulently increase volume |
| **FDC1004** | Texas Instruments 4-channel capacitance-to-digital converter IC |
| **TFLite-Micro** | TensorFlow Lite for Microcontrollers — runs quantized ML models on MCU-class hardware |
| **PTFE** | Polytetrafluoroethylene (Teflon) — chemically inert, fuel-safe insulating material |
| **GATC** | Government Approved Test Centre under India's Legal Metrology Act |
| **Provisional Patent** | A 12-month placeholder filing that establishes priority date without full specification |
| **RMSE** | Root Mean Squared Error — primary regression accuracy metric |
| **INT8 quantization** | Converting float32 model weights to 8-bit integers for 4× compression and faster MCU inference |
