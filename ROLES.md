# FuelGuard — Team Roles & Responsibilities

> **Project:** FuelGuard — Multimodal Fuel Adulteration Detection System  
> **Team Size:** 4 people  
> **Version:** 1.0 | September 2026

---

## Branch Strategy

```
main                              ← stable, paper-ready snapshots only
 └── dev                          ← integration (all PRs merge here first)
      ├── feature/ml-pipeline          → Person A — ML Engineer
      ├── feature/firmware-esp32       → Person B — Embedded Engineer
      ├── feature/dashboard-supabase   → Person C — Full-Stack Developer
      └── feature/research-paper       → Person D — Research Lead
```

> **Rule:** Never push directly to `main` or `dev`. Always open a PR from your feature branch → `dev`.

---

## Person A — ML Engineer

**Branch:** `feature/ml-pipeline`

### Responsibilities
- Build and maintain the entire Python ML pipeline
- Generate synthetic sensor dataset; ingest real lab CSV from Person D
- Train and compare SVM, Random Forest, XGBoost, and MLP models
- Evaluate classification accuracy (≥90%) and concentration RMSE (≤±3%)
- Export winning model to INT8 TFLite format for Person B
- Export calibration constants (`calibration.json`) for firmware
- Generate paper-quality confusion matrices and RMSE plots for Person D

### Files Owned
| File | Purpose |
|---|---|
| `ml/src/data/generate_dataset.py` | Synthetic data generator — replace with real CSV post-lab |
| `ml/src/features/feature_engineering.py` | Temperature compensation + MinMax normalisation |
| `ml/src/models/train.py` | Multi-model training + MLflow experiment tracking |
| `ml/src/evaluation/evaluate.py` | Confusion matrix, RMSE-by-concentration plots |
| `ml/src/conversion/to_tflite.py` | INT8 TFLite export + C-array header for firmware |
| `ml/notebooks/` | EDA, calibration curves, paper figures |
| `ml/tests/test_pipeline.py` | Unit tests — must stay green before every PR |
| `ml/requirements.txt` | Python dependencies |
| `ml/artifacts/` | Model outputs, plots (do NOT commit large binaries) |

### Phase Deliverables
| Phase | Deliverable | Deadline |
|---|---|---|
| Phase 1 | Synthetic dataset working; SVM + RF baseline numbers in `summary.json` | Week 7 |
| Phase 2 | Full 4-model comparison; confusion matrices; RMSE ≤ ±3% | Week 13 |
| Phase 3 | `fuelguard_model.tflite` (<200 KB INT8) + `fuelguard_model.cc` for Person B | Week 16 |
| Phase 4 | Final accuracy table for IEEE paper §IV | Week 20 |

### Interfaces with Other Team Members
- **→ Person B:** Deliver `firmware/src/fuelguard_model.cc` and updated `firmware/data/calibration.json`
- **→ Person D:** Deliver confusion matrix PNGs and RMSE plots for paper figures
- **← Person D:** Receive `ml/data/raw/real_measurements.csv` from lab sessions

### Tools to Learn
| Tool | Install |
|---|---|
| `uv` (package manager) | `pip install uv` |
| `scikit-learn` | `uv pip install scikit-learn` |
| `XGBoost` | `uv pip install xgboost` |
| `MLflow` | `uv pip install mlflow` → `mlflow ui` to view results |
| `pytest` | Run `pytest ml/tests/ -v` before every PR |

```bash
# Quick start
cd ml
uv venv && uv pip install -r requirements.txt
python src/data/generate_dataset.py   # generates data/raw/synthetic_dataset.csv
python src/models/train.py            # trains all models, logs to MLflow
mlflow ui                             # view at localhost:5000
pytest tests/ -v
```

---

## Person B — Embedded / Firmware Engineer

**Branch:** `feature/firmware-esp32`

### Responsibilities
- Write and maintain all ESP32 C++ firmware
- Implement sensor drivers for FDC1004 (I²C), BPW34 optical (ADC), DS18B20 (1-Wire)
- Implement joint temperature compensation and rolling-average feature aggregation
- Integrate TFLite-Micro inference engine with Person A's quantized model
- Implement MQTT publishing with JSON payload matching Person C's Supabase schema
- Benchmark inference latency (<500 ms) and RAM footprint (<200 KB)

### Files Owned
| File | Purpose |
|---|---|
| `firmware/src/main.cpp` | Top-level loop: acquire → compensate → infer → publish |
| `firmware/src/sensors/fdc1004.cpp` | FDC1004 I²C capacitance driver |
| `firmware/src/sensors/optical.cpp` | IR LED + BPW34 ADC optical driver |
| `firmware/src/sensors/temperature.cpp` | DS18B20 1-Wire temperature driver |
| `firmware/src/inference/inference_engine.cpp` | TFLite-Micro runner |
| `firmware/src/inference/normalization.cpp` | Load `calibration.json`, apply transform |
| `firmware/src/comms/mqtt_client.cpp` | MQTT connect / publish / auto-reconnect |
| `firmware/include/` | All `.h` headers |
| `firmware/platformio.ini` | Build config, library versions |
| `firmware/data/calibration.json` | Updated by Person A after lab calibration |

### Phase Deliverables
| Phase | Deliverable | Deadline |
|---|---|---|
| Phase 1 | FDC1004 + DS18B20 + optical drivers reading real values over Serial | Week 7 |
| Phase 2 | Temperature compensation + rolling average (N=50) working; raw CSV log | Week 13 |
| Phase 3 | TFLite-Micro inference running with Person A's model; <500 ms latency confirmed | Week 16 |
| Phase 3 | MQTT publishing to broker; JSON payload verified with Person C | Week 16 |
| Phase 4 | Full system demo: sample insert → result in <30 s end-to-end | Week 20 |

### Interfaces with Other Team Members
- **← Person A:** Receive `fuelguard_model.cc` and `calibration.json`
- **→ Person C:** Confirm MQTT payload field names match Supabase `readings` table columns
- **→ Person D:** Provide raw serial readings during lab sessions for calibration

### Tools to Learn
| Tool | Install |
|---|---|
| PlatformIO (VS Code extension) | [platformio.org](https://platformio.org) |
| Arduino framework for ESP32 | Auto-installed by PlatformIO |
| TFLite-Micro (Espressif fork) | [github.com/espressif/esp-tflite-micro](https://github.com/espressif/esp-tflite-micro) |
| ArduinoJson 7 | [arduinojson.org](https://arduinojson.org/v7/doc/) |
| FDC1004 datasheet | [TI FDC1004](https://www.ti.com/lit/ds/symlink/fdc1004.pdf) |

```bash
# Quick start
pip install platformio
cd firmware
pio run                          # build only
pio run --target upload          # flash to ESP32
pio device monitor -b 115200     # serial output
pio run --target uploadfs        # upload calibration.json to SPIFFS
```

---

## Person C — Full-Stack Developer

**Branch:** `feature/dashboard-supabase`

### Responsibilities
- Build the Next.js web dashboard with live sensor data display
- Set up Supabase database schema and row-level security policies
- Implement realtime data feed from Supabase to the dashboard
- Write the MQTT-to-Supabase bridge (Node.js) that receives ESP32 payloads
- Implement CSV export for audit logs (FR-C4)
- Ensure the dashboard works in offline mode (shows last known data)

### Files Owned
| File | Purpose |
|---|---|
| `dashboard/src/app/page.tsx` | Main dashboard: live status + gauge + chart |
| `dashboard/src/app/layout.tsx` | Root layout |
| `dashboard/src/app/history/page.tsx` | Historical readings table + CSV export |
| `dashboard/src/components/charts/ConcentrationGauge.tsx` | Recharts gauge |
| `dashboard/src/components/charts/TimeSeriesChart.tsx` | Rolling concentration chart |
| `dashboard/src/components/ui/StatusBadge.tsx` | Pass/Fail/Adulterated badge |
| `dashboard/src/lib/supabase.ts` | Supabase client singleton |
| `dashboard/src/types/supabase.ts` | TypeScript types for `readings` table |
| `dashboard/supabase/migrations/` | SQL schema — add new migrations here |
| `dashboard/src/app/api/export/route.ts` | CSV export API route |
| `scripts/mqtt_bridge.js` | Node.js MQTT subscriber → Supabase insert |
| `dashboard/package.json` | Dependencies |

### Phase Deliverables
| Phase | Deliverable | Deadline |
|---|---|---|
| Phase 1 | Supabase project created; migration applied; manual insert tested | Week 7 |
| Phase 2 | Dashboard scaffolded with mock data; Recharts charts visible at localhost:3000 | Week 13 |
| Phase 3 | MQTT bridge running; real ESP32 readings appearing in dashboard live | Week 16 |
| Phase 3 | CSV export endpoint working | Week 16 |
| Phase 4 | Screenshot + screen recording of live dashboard for paper figure | Week 20 |

### Interfaces with Other Team Members
- **← Person B:** Agree on MQTT payload JSON field names before Phase 3
- **→ Person D:** Provide CSV export and dashboard screenshot for paper

### Tools to Learn
| Tool | Docs |
|---|---|
| Next.js 15 App Router | [nextjs.org/docs](https://nextjs.org/docs) |
| Supabase (Postgres + Realtime) | [supabase.com/docs](https://supabase.com/docs/guides/getting-started/quickstarts/nextjs) |
| Recharts | [recharts.org](https://recharts.org/en-US/) |
| Tailwind CSS | [tailwindcss.com/docs](https://tailwindcss.com/docs) |
| MQTT.js (bridge) | [github.com/mqttjs/MQTT.js](https://github.com/mqttjs/MQTT.js) |

```bash
# Quick start
cd dashboard
npm install
cp .env.example .env.local      # fill in Supabase URL + anon key
npm run dev                     # localhost:3000
npm run lint                    # check before PR
npx tsc --noEmit                # type check before PR
```

---

## Person D — Research Lead & Hardware Engineer

**Branch:** `feature/research-paper`

### Responsibilities
- Design and assemble the physical sensor hardware (PTFE chamber, FDC1004, BPW34, DS18B20)
- Conduct all lab experiments and collect the real sensor dataset
- Maintain the lab safety checklist and experiment log
- Hand off `real_measurements.csv` to Person A in the correct format
- Write the IEEE-style paper (LaTeX) using results from Persons A and C
- Conduct prior art search and draft provisional patent claims
- Coordinate external GC-MS validation (5 samples to external lab)
- Act as project **safety officer** for all fuel handling sessions

### Files Owned
| File | Purpose |
|---|---|
| `research/paper/main.tex` | IEEE paper — primary LaTeX document |
| `research/paper/sections/` | Individual section `.tex` files |
| `research/paper/figures/` | Plots from Person A + dashboard screenshots from Person C |
| `research/patent/provisional_claims.md` | Patent claim drafts |
| `research/patent/prior_art_search.md` | IP India / WIPO / Espacenet search log |
| `research/literature/references.bib` | BibTeX references |
| `ml/data/raw/real_measurements.csv` | **Key file:** real sensor readings from lab |
| `docs/safety_checklist.md` | Lab safety protocol — read before every session |
| `docs/experiment_log.md` | Date-stamped record of every lab session |
| `scripts/serial_logger.py` | Captures ESP32 serial output → CSV during experiments |

### Real Measurement CSV Schema
Person D must collect data in this exact column format for Person A to ingest:
```
sample_id, fuel_base, adulterant, concentration_pct, temperature_c, replicate,
capacitance_raw, optical_raw, tof_raw, timestamp, notes
```

### Phase Deliverables
| Phase | Deliverable | Deadline |
|---|---|---|
| Phase 0 | Prior art search complete; patent claims scoped in `prior_art_search.md` | Week 3 |
| Phase 1 | Hardware assembled; Experiment A data collected; `real_measurements.csv` to Person A | Week 7 |
| Phase 2 | Full sample matrix collected (all concentrations × 4 temps × 3 replicates) | Week 13 |
| Phase 3 | 5 samples sent to external lab for GC-MS cross-validation | Week 16 |
| Phase 4 | IEEE paper draft complete; provisional patent filed **before** paper submission | Week 20 |

### Interfaces with Other Team Members
- **→ Person A:** Hand off `ml/data/raw/real_measurements.csv` with correct column schema
- **← Person A:** Receive confusion matrix PNGs + RMSE plots for paper §IV–V
- **← Person C:** Receive dashboard screenshot for paper figure
- **← Person B:** Confirm sensor wiring matches `firmware/include/config.h` pin assignments

### Tools to Learn
| Tool | Resource |
|---|---|
| LaTeX (IEEEtran class) | [Overleaf IEEEtran Template](https://www.overleaf.com/latex/templates/ieee-conference-template/grfzhhncsfqn) |
| Zotero + BibTeX | [zotero.org/support/quick_start_guide](https://www.zotero.org/support/quick_start_guide) |
| `scripts/serial_logger.py` | `python scripts/serial_logger.py --port COM3 --out ml/data/raw/real_measurements.csv` |
| IP India Patent Portal | [ipindia.gov.in](https://ipindia.gov.in) — Form 1 + Form 2 provisional filing |
| Espacenet / WIPO PatentScope | Prior art search — query "fuel adulteration capacitive optical sensor" |

```bash
# Capture lab data from ESP32 serial
python scripts/serial_logger.py --port COM3 --baud 115200 --samples 50 \
  --out ml/data/raw/real_measurements.csv
```

---

## Cross-Team Data Flow

```
Person D (Lab)
  real_measurements.csv
         │
         ▼
Person A (ML) ──── fuelguard_model.cc ────► Person B (Firmware)
         │          calibration.json                │
         │                                          │ MQTT JSON
         │                                          ▼
         │                               Person C (Dashboard)
         │                                 Supabase DB
         │                                 CSV export
         │                                    │
         └──── confusion_matrix.png ──────────┘
               RMSE plots                     │
               accuracy table                 │
                                              ▼
                               Person D (Paper + Patent)
```

---

## Milestone Schedule

| Week | Milestone | Merge to `dev` |
|---|---|---|
| Week 3 | Phase 0 — prior art done | Person D |
| Week 7 | Phase 1 — single sensor baselines | A + B + D |
| Week 13 | Phase 2 — fusion model ≥90% accuracy | A |
| Week 16 | Phase 3 — ESP32 live demo + dashboard live | B + C |
| Week 20 | Phase 4 — paper submitted + patent filed | D |
| Week 20 | **Final `dev → main` merge** | All 4 approve |

---

## Shared Responsibilities (Everyone)

| Responsibility | Details |
|---|---|
| Weekly sync | 30-minute standup — share blockers, review PR status |
| PR reviews | Every PR needs ≥1 reviewer from another team member |
| CI checks | All 3 CI checks (ML tests, dashboard lint, firmware build) must be green before merge |
| No secrets | Never commit Wi-Fi passwords, API keys, or `.env.local` files |
| Commit format | `type(scope): description` — see [CONTRIBUTING.md](CONTRIBUTING.md) |

---

*Last updated: September 2026*
