# FuelGuard — Tech Stack Reference

## ML Pipeline

| Layer | Tool | Rationale |
|---|---|---|
| **Package manager** | [`uv`](https://github.com/astral-sh/uv) | 10–100× faster than pip; lockfile support |
| **Data manipulation** | `pandas` + `numpy` | Standard; well-supported on all platforms |
| **ML baselines** | `scikit-learn` | SVM, RF, MLP in one API; easy cross-validation |
| **Gradient boosting** | `XGBoost` | Typically best tabular model; fast, GPU optional |
| **Deep learning / TFLite** | `TensorFlow 2.x` (CPU only for CI) | Only needed for TFLite INT8 conversion step |
| **Experiment tracking** | `MLflow` (local) | Zero infra; full metrics/artifact logging; runs locally |
| **Visualisation** | `matplotlib` + `seaborn` + `plotly` | Static paper figures + interactive notebook plots |
| **Testing** | `pytest` + `pytest-cov` | Standard; integrates with GitHub Actions CI |
| **Linting** | `ruff` | Replaces flake8/isort/black in one tool; extremely fast |

> **Why MLflow over W&B/Neptune?**  
> No account or internet required. All run data stays local. For a research project you can export to CSV/HTML at any time.

---

## Firmware

| Layer | Tool | Rationale |
|---|---|---|
| **Build system** | [PlatformIO](https://platformio.org/) | Cross-platform; dependency management; better than Arduino IDE for multi-file projects |
| **Framework** | Arduino (ESP32 Arduino Core) | Largest ecosystem of ESP32 libraries |
| **ML inference** | [TFLite-Micro](https://github.com/espressif/esp-tflite-micro) (Espressif fork) | Optimised for ESP32 Xtensa; INT8 quantisation; <200 KB RAM |
| **MQTT client** | `PubSubClient` | Most widely used ESP MQTT library; battle-tested |
| **Serialisation** | `ArduinoJson 7` | Zero-allocation JSON; fits in tight MCU RAM |
| **1-Wire / DS18B20** | `OneWire` + `DallasTemperature` | Standard, well-maintained |
| **Calibration storage** | SPIFFS / LittleFS + JSON | Calibration constants updatable via OTA without reflashing model |

> **Why PlatformIO over Arduino IDE?**  
> - Library versioning (lockfile)  
> - Multi-file C++ project support  
> - Unit testing framework (`pio test`)  
> - CI/CD integration  

---

## Dashboard

| Layer | Tool | Rationale |
|---|---|---|
| **Framework** | [Next.js 15](https://nextjs.org/) (App Router) | SSR + client components in one; file-based routing |
| **Language** | TypeScript | End-to-end type safety with Supabase generated types |
| **Database / Auth** | [Supabase](https://supabase.com/) | Open-source Postgres + realtime subscriptions + row-level security |
| **Charts** | [Recharts](https://recharts.org/) | React-native; no D3 expertise required; responsive |
| **Styling** | Tailwind CSS | Utility-first; no CSS files to maintain |
| **Icons** | `lucide-react` | Tree-shakeable; consistent set |
| **MQTT bridge** | Supabase Edge Function or Node.js bridge | ESP32 publishes to MQTT → bridge inserts into Supabase `readings` table |

> **Why Supabase over Firebase?**  
> - Open-source (self-hostable)  
> - Postgres (real SQL, better for analytics/export)  
> - Built-in realtime via websockets  
> - Free tier sufficient for a research project  

---

## DevOps / Research

| Layer | Tool | Rationale |
|---|---|---|
| **Version control** | Git + GitHub | Standard |
| **CI** | GitHub Actions | Free for public repos; three parallel jobs (ML / firmware / dashboard) |
| **Notebooks** | Jupyter | EDA, calibration curves, paper-quality figures |
| **Paper** | LaTeX (IEEE style) | `IEEEtran.cls`; Overleaf compatible |
| **Reference management** | Zotero / BibTeX | Integrates with LaTeX |

---

## Architecture Decision: Dual-head model vs. two separate models

The system uses **a single MLP backbone with two output heads**:
- Head 1: Softmax classification (5 classes)
- Head 2: Linear regression (concentration %)

**Advantages over two separate models:**
- Shared representations → better generalisation
- Single model file → smaller flash footprint
- Single inference call → lower latency

**Downside:** joint loss balancing requires tuning `α·L_cls + (1-α)·L_reg`.  
Start with `α = 0.5`; tune on validation set.
