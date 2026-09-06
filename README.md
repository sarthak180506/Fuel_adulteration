# FuelGuard — Multimodal Fuel Adulteration Detection System

> Edge-deployed, multimodal sensor fusion for real-time detection and quantification of fuel adulteration at the point of sale.

## System Overview

```
Capacitive (FDC1004) + Optical (IR/BPW34) + Temperature (DS18B20)
                          ↓
              ESP32 — TFLite-Micro Inference
                          ↓
         Classification + Concentration Regression
                          ↓
              MQTT → Supabase → Web Dashboard
```

## Repository Structure

```
fuelguard/
├── ml/              # Python ML pipeline (training, evaluation, TFLite export)
├── firmware/        # ESP32 C++ firmware (PlatformIO)
├── dashboard/       # Next.js web dashboard + Supabase schema
├── research/        # IEEE paper (LaTeX) + patent draft
├── scripts/         # Data collection, calibration, CI helpers
└── docs/            # Architecture diagrams, wiring schematics
```

## Quick Start

### ML Pipeline
```bash
cd ml
uv venv && uv pip install -r requirements.txt
python src/data/generate_dataset.py     # synthetic data
python src/models/train.py              # train all models
python src/conversion/to_tflite.py      # export INT8 .tflite
```

### Firmware
```bash
cd firmware
pio run --target upload                 # build & flash ESP32
pio device monitor                      # serial monitor
```

### Dashboard
```bash
cd dashboard
npm install
npm run dev                             # localhost:3000
```

## Key Targets
| Metric | Minimum | Stretch |
|---|---|---|
| Classification accuracy | ≥90% | ≥97% |
| Concentration RMSE | ≤±3% | ≤±1.5% |
| Inference latency | <500 ms | <100 ms |
| Model RAM footprint | <200 KB | <100 KB |

## Tech Stack
See [docs/tech_stack.md](docs/tech_stack.md) for full rationale.
