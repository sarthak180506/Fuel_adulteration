"""
Feature engineering pipeline.

Applies:
  1. Joint temperature compensation (inverse of acquisition-time correction)
  2. Per-channel min-max normalisation to [0, 1]
  3. Outputs calibration constants suitable for writing to ESP32 flash (JSON)
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

FEATURE_COLS = ["capacitance_raw", "optical_raw", "tof_raw", "temperature_c"]
TARGET_CLS   = "label_cls"
TARGET_CONC  = "label_conc"

REF_TEMP     = 30.0
TEMP_COEFF_CAP = 0.002
TEMP_COEFF_OPT = 0.001


def temperature_compensate(df: pd.DataFrame) -> pd.DataFrame:
    """Invert the temperature drift so features reflect ref-temp values."""
    df = df.copy()
    dt = df["temperature_c"] - REF_TEMP
    df["cap_comp"] = df["capacitance_raw"] / (1 + TEMP_COEFF_CAP * dt)
    df["opt_comp"] = df["optical_raw"]     / (1 - TEMP_COEFF_OPT * dt).clip(lower=0.01)
    return df


def build_feature_matrix(
    df: pd.DataFrame,
    include_tof: bool = True,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (X, y_cls, y_conc)."""
    df = temperature_compensate(df)
    cols = ["cap_comp", "opt_comp", "temperature_c"]
    if include_tof:
        cols.append("tof_raw")
    X      = df[cols].values.astype(np.float32)
    y_cls  = df[TARGET_CLS].values.astype(np.int32)
    y_conc = df[TARGET_CONC].values.astype(np.float32)
    return X, y_cls, y_conc


def split_and_scale(
    X: np.ndarray,
    y_cls: np.ndarray,
    y_conc: np.ndarray,
    test_size: float = 0.15,
    val_size:  float = 0.15,
    random_state: int = 42,
) -> dict:
    """
    Stratified 70 / 15 / 15 split + MinMaxScaler fit on train set only.
    Returns a dict of {X_train, X_val, X_test, y_cls_*, y_conc_*, scaler}.
    """
    X_tmp, X_test, yc_tmp, yc_test, yr_tmp, yr_test = train_test_split(
        X, y_cls, y_conc,
        test_size=test_size,
        stratify=y_cls,
        random_state=random_state,
    )
    val_frac = val_size / (1 - test_size)
    X_train, X_val, yc_train, yc_val, yr_train, yr_val = train_test_split(
        X_tmp, yc_tmp, yr_tmp,
        test_size=val_frac,
        stratify=yc_tmp,
        random_state=random_state,
    )

    scaler = MinMaxScaler()
    X_train = scaler.fit_transform(X_train)
    X_val   = scaler.transform(X_val)
    X_test  = scaler.transform(X_test)

    return dict(
        X_train=X_train, X_val=X_val, X_test=X_test,
        y_cls_train=yc_train, y_cls_val=yc_val, y_cls_test=yc_test,
        y_conc_train=yr_train, y_conc_val=yr_val, y_conc_test=yr_test,
        scaler=scaler,
    )


def export_calibration_json(scaler: MinMaxScaler, path: Path) -> None:
    """
    Serialize scaler min/max to JSON for embedding in ESP32 flash.
    Format matches firmware/data/calibration.json schema.
    """
    cal = {
        "feature_min": scaler.data_min_.tolist(),
        "feature_max": scaler.data_max_.tolist(),
        "feature_range": scaler.data_range_.tolist(),
        "ref_temp_c": REF_TEMP,
        "temp_coeff_cap": TEMP_COEFF_CAP,
        "temp_coeff_opt": TEMP_COEFF_OPT,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cal, indent=2))
    print(f"[features] Calibration JSON → {path}")
