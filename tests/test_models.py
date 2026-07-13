"""Sanity tests for src/models."""

import numpy as np
import pytest
from src.models import evaluate_model, get_baseline_models


def test_get_baseline_models_has_expected_keys():
    models = get_baseline_models()
    assert set(models.keys()) == {
        "LinearRegression", "BayesianRidge", "RandomForest", "XGBoost", "LightGBM"
    }


def test_get_baseline_models_are_unfitted():
    models = get_baseline_models()
    for name, model in models.items():
        assert hasattr(model, "fit"), f"{name} missing .fit()"
        assert hasattr(model, "predict"), f"{name} missing .predict()"


def test_evaluate_model_keys():
    X = np.array([[1], [2], [3]])
    y = np.array([1.0, 2.0, 3.0])
    from sklearn.linear_model import LinearRegression
    model = LinearRegression().fit(X, y)
    result = evaluate_model(model, X, y)
    assert set(result.keys()) == {"R2", "RMSE", "MSE"}


def test_evaluate_model_perfect_predictions():
    X = np.array([[1], [2], [3]])
    y = np.array([1.0, 2.0, 3.0])
    from sklearn.linear_model import LinearRegression
    model = LinearRegression().fit(X, y)
    result = evaluate_model(model, X, y)
    assert abs(result["R2"] - 1.0) < 1e-9
    assert result["RMSE"] < 1e-9
    assert result["MSE"] < 1e-9


def test_get_baseline_models_returns_fresh_instances():
    m1 = get_baseline_models()
    m2 = get_baseline_models()
    assert m1["RandomForest"] is not m2["RandomForest"]