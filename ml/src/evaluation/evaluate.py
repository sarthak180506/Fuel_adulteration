"""
Evaluation utilities: confusion matrix, RMSE curve, per-concentration breakdown.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix

PLOTS_DIR = Path(__file__).parents[2] / "artifacts" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

CLASS_NAMES = [
    "Pure Fuel",
    "KER-Pet",
    "DSL-Pet",
    "KER-Dsl",
    "H2O-Dsl",
]


def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray,
                           model_name: str = "model") -> Path:
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(7, 6))
    disp = ConfusionMatrixDisplay(cm, display_labels=CLASS_NAMES)
    disp.plot(ax=ax, colorbar=False, cmap="Blues")
    ax.set_title(f"Confusion Matrix — {model_name}")
    plt.tight_layout()
    out = PLOTS_DIR / f"cm_{model_name}.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"[eval] Confusion matrix → {out}")
    return out


def plot_rmse_by_concentration(y_true: np.ndarray, y_pred: np.ndarray,
                                conc_levels: list[float],
                                model_name: str = "model") -> Path:
    """RMSE broken down by ground-truth concentration bucket."""
    rmse_by_conc: dict[float, float] = {}
    for c in conc_levels:
        mask = y_true == c
        if mask.sum() == 0:
            continue
        rmse_by_conc[c] = float(np.sqrt(np.mean((y_pred[mask] - y_true[mask]) ** 2)))

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(list(rmse_by_conc.keys()), list(rmse_by_conc.values()), width=1.2)
    ax.axhline(3.0, color="red", ls="--", label="Target ±3% RMSE")
    ax.set_xlabel("True concentration (%)")
    ax.set_ylabel("RMSE (%)")
    ax.set_title(f"Concentration RMSE by level — {model_name}")
    ax.legend()
    plt.tight_layout()
    out = PLOTS_DIR / f"rmse_{model_name}.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"[eval] RMSE curve → {out}")
    return out


def print_metric_table(cls_results: dict, reg_results: dict) -> None:
    """Pretty-print comparison table to stdout."""
    print("\n" + "=" * 60)
    print(f"{'Model':<16} {'Acc':>6} {'F1':>6} {'RMSE':>8} {'MAE':>8} {'R²':>6}")
    print("-" * 60)
    for name in cls_results:
        c = cls_results[name]
        r = reg_results[name]
        print(f"{name:<16} {c['accuracy']:>6.4f} {c['macro_f1']:>6.4f} "
              f"{r['rmse']:>8.3f} {r['mae']:>8.3f} {r['r2']:>6.4f}")
    print("=" * 60)
