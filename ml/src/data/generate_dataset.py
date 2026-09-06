"""
Synthetic sensor dataset generator for FuelGuard.

Generates (capacitance, optical, temperature) readings for the full
sample matrix defined in the PRD §8.1.  Replace/augment with real
measurements as they are collected.

Output CSV schema:
  sample_id, fuel_base, adulterant, concentration_pct, temperature_c,
  capacitance_raw, optical_raw, tof_raw,
  label_cls (int), label_conc (float)
"""

from __future__ import annotations

import hashlib
import itertools
from pathlib import Path

import numpy as np
import pandas as pd

# ── Physical prior ranges (tweak after real calibration) ────────────────────
# These are plausible relative dielectric / transmittance ranges.
# Petrol ε ≈ 2.0, Kerosene ε ≈ 1.8, Diesel ε ≈ 2.1, Water ε ≈ 80
DIELECTRIC = {
    "petrol":   2.00,
    "diesel":   2.10,
    "kerosene": 1.80,
    "water":   80.00,
}

# BPW34 optical transmittance (0–1 normalised, 850 nm IR)
OPTICAL = {
    "petrol":   0.92,
    "diesel":   0.65,
    "kerosene": 0.88,
    "water":    0.30,
}

# Temperature coefficient of capacitance (per °C, approximate)
TEMP_COEFF_CAP = 0.002   # 0.2% per °C
TEMP_COEFF_OPT = 0.001   # 0.1% per °C
NOISE_STD      = 0.005   # sensor noise std

SAMPLE_MATRIX = [
    # (fuel_base, adulterant, concentrations_pct)
    ("petrol", "kerosene", [0, 2, 5, 10, 15, 20, 25, 30]),
    ("petrol", "diesel",   [0, 2, 5, 10, 15, 20, 25, 30]),
    ("diesel", "kerosene", [0, 2, 5, 10, 15, 20, 25, 30]),
    ("diesel", "water",    [0, 1, 2, 5, 10]),
]

TEMPERATURES  = [30, 35, 40, 45]   # °C
REPLICATES    = 3
REF_TEMP      = 30.0               # calibration reference temperature

# Class map  ──────────────────────────────────────────────────────────────────
CLASS_MAP = {
    ("petrol",  "kerosene"): 1,   # Kerosene-adulterated petrol
    ("petrol",  "diesel"):   2,   # Diesel-adulterated petrol
    ("diesel",  "kerosene"): 3,   # Kerosene-adulterated diesel
    ("diesel",  "water"):    4,   # Water-adulterated diesel
    # concentration == 0 → pure fuel
    ("petrol",  "none"):     0,   # Pure petrol
    ("diesel",  "none"):     0,   # Pure diesel (same class; adjust if needed)
}


def _mix(base: str, adulterant: str, pct: float) -> tuple[float, float]:
    """Return (capacitance_raw, optical_raw) for a mixture at ref temperature."""
    r = pct / 100.0
    cap = (1 - r) * DIELECTRIC[base] + r * DIELECTRIC[adulterant]
    opt = (1 - r) * OPTICAL[base]   + r * OPTICAL[adulterant]
    return cap, opt


def generate(seed: int = 42, out_dir: Path | None = None) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows: list[dict] = []
    sid = 0

    for (fuel, adul, concs), temp, rep in itertools.product(
        SAMPLE_MATRIX, TEMPERATURES, range(REPLICATES)
    ):
        for pct in concs:
            effective_adul = adul if pct > 0 else "none"
            cls = CLASS_MAP.get((fuel, effective_adul), 0)

            cap_ref, opt_ref = _mix(fuel, adul if pct > 0 else fuel, pct)

            # Joint temperature compensation (linear model)
            dt = temp - REF_TEMP
            cap = cap_ref * (1 + TEMP_COEFF_CAP * dt)
            opt = opt_ref * (1 - TEMP_COEFF_OPT * dt)

            # Additive Gaussian noise
            cap += rng.normal(0, NOISE_STD)
            opt += rng.normal(0, NOISE_STD * 0.5)

            # Optional: ultrasonic ToF proxy (density surrogate)
            # density ~ 0.72 (petrol) to 0.84 (diesel) to 1.0 (water) g/mL
            tof = 200 + pct * 0.5 + rng.normal(0, 1.0)  # µs, placeholder

            rows.append({
                "sample_id":        sid,
                "fuel_base":        fuel,
                "adulterant":       effective_adul,
                "concentration_pct": float(pct),
                "temperature_c":    float(temp),
                "replicate":        rep,
                "capacitance_raw":  round(cap, 6),
                "optical_raw":      round(np.clip(opt, 0, 1), 6),
                "tof_raw":          round(tof, 3),
                "label_cls":        cls,
                "label_conc":       float(pct),
            })
            sid += 1

    df = pd.DataFrame(rows)

    if out_dir is not None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "synthetic_dataset.csv"
        df.to_csv(path, index=False)
        print(f"[generate_dataset] Saved {len(df)} rows → {path}")

    return df


if __name__ == "__main__":
    DATA_DIR = Path(__file__).parents[2] / "data" / "raw"
    df = generate(out_dir=DATA_DIR)
    print(df.groupby(["fuel_base", "adulterant"])["concentration_pct"].describe())
