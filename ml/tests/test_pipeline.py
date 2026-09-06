"""
Smoke tests for the ML pipeline (no real data required).
"""
import numpy as np
import pytest
from src.data.generate_dataset import generate
from src.features.feature_engineering import build_feature_matrix, split_and_scale


def test_generate_dataset_shape():
    df = generate(seed=0)
    # 4 fuel combos × (varied concentrations) × 4 temps × 3 reps
    assert len(df) > 200
    assert "capacitance_raw" in df.columns
    assert "label_cls" in df.columns


def test_feature_matrix_shape():
    df = generate(seed=0)
    X, y_cls, y_conc = build_feature_matrix(df, include_tof=True)
    assert X.shape[1] == 4
    assert X.shape[0] == len(df)
    assert y_cls.shape[0] == len(df)


def test_split_sizes():
    df = generate(seed=0)
    X, y_cls, y_conc = build_feature_matrix(df)
    splits = split_and_scale(X, y_cls, y_conc)
    n = len(df)
    assert splits["X_train"].shape[0] > splits["X_test"].shape[0]
    assert splits["X_val"].shape[0]   > 0


def test_features_normalised():
    df = generate(seed=0)
    X, y_cls, y_conc = build_feature_matrix(df)
    splits = split_and_scale(X, y_cls, y_conc)
    # After MinMaxScaler, train features should be in [0, 1]
    assert splits["X_train"].min() >= -1e-6
    assert splits["X_train"].max() <= 1.0 + 1e-6


def test_label_cls_range():
    df = generate(seed=0)
    _, y_cls, _ = build_feature_matrix(df)
    assert y_cls.min() >= 0
    assert y_cls.max() <= 4
