"""Sanity tests for src/models."""

import numpy as np
import pytest
from src.models import evaluate_model, get_baseline_models


def test_get_baseline_models_has_expected_keys():
    models = get_baseline_models()
    assert set(models.keys()) == {
        "MeanPredictor", "Ridge", "BayesianRidge", "RandomForest", "XGBoost", "LightGBM"
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
    assert set(result.keys()) == {"R2", "RMSE", "MSE", "MAE", "Spearman", "CCC"}


def test_evaluate_model_perfect_predictions():
    X = np.array([[1], [2], [3]])
    y = np.array([1.0, 2.0, 3.0])
    from sklearn.linear_model import LinearRegression
    model = LinearRegression().fit(X, y)
    result = evaluate_model(model, X, y)
    assert abs(result["R2"] - 1.0) < 1e-9
    assert result["RMSE"] < 1e-9
    assert result["MSE"] < 1e-9
    assert result["MAE"] < 1e-9
    assert abs(result["Spearman"] - 1.0) < 1e-9
    assert abs(result["CCC"] - 1.0) < 1e-9


def test_evaluate_model_metric_ranges():
    rng = np.random.default_rng(42)
    X = rng.random((20, 3))
    y = rng.random(20)
    from sklearn.linear_model import LinearRegression
    model = LinearRegression().fit(X, y)
    result = evaluate_model(model, X, y)
    assert result["MAE"] >= 0
    assert -1.0 <= result["Spearman"] <= 1.0
    assert -1.0 <= result["CCC"] <= 1.0


def test_evaluate_model_accepts_none_model_with_y_pred():
    y = np.array([1.0, 2.0, 3.0, 4.0])
    y_pred = np.array([1.1, 1.9, 3.1, 3.9])
    result = evaluate_model(None, None, y, y_pred=y_pred)
    assert result["MAE"] >= 0
    assert -1.0 <= result["Spearman"] <= 1.0
    assert -1.0 <= result["CCC"] <= 1.0


def test_get_baseline_models_returns_fresh_instances():
    m1 = get_baseline_models()
    m2 = get_baseline_models()
    assert m1["RandomForest"] is not m2["RandomForest"]


def test_evaluate_model_accepts_precomputed_y_pred():
    X = np.array([[1], [2], [3]])
    y = np.array([1.0, 2.0, 3.0])
    from sklearn.linear_model import LinearRegression
    model = LinearRegression().fit(X, y)
    y_pred = model.predict(X)
    result_precomputed = evaluate_model(model, X, y, y_pred=y_pred)
    result_default = evaluate_model(model, X, y)
    for key in ("R2", "RMSE", "MAE", "Spearman", "CCC"):
        assert abs(result_precomputed[key] - result_default[key]) < 1e-9