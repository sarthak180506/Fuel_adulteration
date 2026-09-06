"""
Baseline model comparison: SVM, Random Forest, XGBoost, MLP.

Each model is evaluated on:
  - Classification head: accuracy, macro-F1, per-class F1
  - Regression head:     RMSE, MAE, R²  (concentration %)

Results are logged to MLflow and saved to artifacts/plots/.
"""

from __future__ import annotations

import json
from pathlib import Path

import mlflow
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.svm import SVC, SVR
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from xgboost import XGBClassifier, XGBRegressor

# Local imports
import sys
sys.path.insert(0, str(Path(__file__).parents[2]))
from src.data.generate_dataset import generate
from src.features.feature_engineering import build_feature_matrix, split_and_scale, export_calibration_json

ARTIFACTS  = Path(__file__).parents[2] / "artifacts"
DATA_DIR   = Path(__file__).parents[2] / "data" / "raw"

CLASS_NAMES = [
    "Pure Fuel",
    "Kerosene-Adulterated Petrol",
    "Diesel-Adulterated Petrol",
    "Kerosene-Adulterated Diesel",
    "Water-Adulterated Diesel",
]

# ── Model zoo ────────────────────────────────────────────────────────────────
CLASSIFIERS = {
    "SVM":           SVC(kernel="rbf", C=10, gamma="scale", probability=True, random_state=42),
    "RandomForest":  RandomForestClassifier(n_estimators=200, max_depth=None, random_state=42, n_jobs=-1),
    "XGBoost":       XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1,
                                    use_label_encoder=False, eval_metric="mlogloss",
                                    random_state=42, n_jobs=-1),
    "MLP":           MLPClassifier(hidden_layer_sizes=(128, 64, 32), activation="relu",
                                    max_iter=500, early_stopping=True, random_state=42),
}

REGRESSORS = {
    "SVM":           SVR(kernel="rbf", C=10, epsilon=0.5),
    "RandomForest":  RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1),
    "XGBoost":       XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1,
                                   random_state=42, n_jobs=-1),
    "MLP":           MLPRegressor(hidden_layer_sizes=(128, 64, 32), activation="relu",
                                   max_iter=500, early_stopping=True, random_state=42),
}


def evaluate_classifier(name: str, clf, splits: dict) -> dict:
    clf.fit(splits["X_train"], splits["y_cls_train"])
    preds = clf.predict(splits["X_test"])
    acc   = accuracy_score(splits["y_cls_test"], preds)
    f1    = f1_score(splits["y_cls_test"], preds, average="macro")
    report = classification_report(splits["y_cls_test"], preds,
                                    target_names=CLASS_NAMES, output_dict=True)
    print(f"[CLS] {name:15s}  acc={acc:.4f}  macro-F1={f1:.4f}")
    return {"accuracy": acc, "macro_f1": f1, "report": report, "model": clf}


def evaluate_regressor(name: str, reg, splits: dict) -> dict:
    reg.fit(splits["X_train"], splits["y_conc_train"])
    preds = reg.predict(splits["X_test"])
    rmse  = float(np.sqrt(mean_squared_error(splits["y_conc_test"], preds)))
    mae   = float(mean_absolute_error(splits["y_conc_test"], preds))
    r2    = float(r2_score(splits["y_conc_test"], preds))
    print(f"[REG] {name:15s}  RMSE={rmse:.3f}%  MAE={mae:.3f}%  R²={r2:.4f}")
    return {"rmse": rmse, "mae": mae, "r2": r2, "model": reg}


def train(include_tof: bool = True) -> None:
    mlflow.set_experiment("fuelguard-baselines")

    # ── Load / generate data ────────────────────────────────────────────────
    csv_path = DATA_DIR / "synthetic_dataset.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        df = generate(out_dir=DATA_DIR)

    X, y_cls, y_conc = build_feature_matrix(df, include_tof=include_tof)
    splits = split_and_scale(X, y_cls, y_conc)

    # Export calibration constants for firmware
    cal_path = Path(__file__).parents[3] / "firmware" / "data" / "calibration.json"
    export_calibration_json(splits["scaler"], cal_path)

    cls_results: dict  = {}
    reg_results: dict  = {}

    with mlflow.start_run(run_name="all_baselines"):
        for name, clf in CLASSIFIERS.items():
            with mlflow.start_run(run_name=f"cls_{name}", nested=True):
                res = evaluate_classifier(name, clf, splits)
                mlflow.log_metrics({"accuracy": res["accuracy"], "macro_f1": res["macro_f1"]})
                cls_results[name] = res

        for name, reg in REGRESSORS.items():
            with mlflow.start_run(run_name=f"reg_{name}", nested=True):
                res = evaluate_regressor(name, reg, splits)
                mlflow.log_metrics({"rmse": res["rmse"], "mae": res["mae"], "r2": res["r2"]})
                reg_results[name] = res

    # ── Pick winner ─────────────────────────────────────────────────────────
    best_cls_name = max(cls_results, key=lambda k: cls_results[k]["macro_f1"])
    best_reg_name = min(reg_results, key=lambda k: reg_results[k]["rmse"])
    print(f"\n✓ Best classifier : {best_cls_name} (F1={cls_results[best_cls_name]['macro_f1']:.4f})")
    print(f"✓ Best regressor  : {best_reg_name} (RMSE={reg_results[best_reg_name]['rmse']:.3f}%)")

    # Save summary
    summary = {
        "classifier": {k: {"accuracy": v["accuracy"], "macro_f1": v["macro_f1"]}
                        for k, v in cls_results.items()},
        "regressor":  {k: {"rmse": v["rmse"], "mae": v["mae"], "r2": v["r2"]}
                        for k, v in reg_results.items()},
        "best_classifier": best_cls_name,
        "best_regressor":  best_reg_name,
    }
    out = ARTIFACTS / "models" / "summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2))
    print(f"\nSummary → {out}")

    return cls_results, reg_results, splits


if __name__ == "__main__":
    train()
