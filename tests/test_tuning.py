"""Sanity tests for src/tuning."""

import json

import numpy as np
import pytest
from lightgbm import LGBMRegressor
from sklearn.ensemble import RandomForestRegressor
from src.tuning import (
    load_params,
    make_model,
    save_params,
    tune_lightgbm,
    tune_rf,
)


@pytest.fixture
def small_regression():
    rng = np.random.default_rng(0)
    X = rng.random((60, 10))
    y = X[:, 0] * 2 + rng.normal(0, 0.1, 60)
    # 48 train, 12 val
    return X[:48], y[:48], X[48:], y[48:]


SMALL_LGBM_GRID = {
    "n_estimators": [20, 50],
    "learning_rate": [0.05, 0.1],
    "num_leaves": [15, 31],
}

SMALL_RF_GRID = {
    "n_estimators": [20, 50],
    "max_depth": [None, 10],
    "min_samples_leaf": [1, 5],
}


# ── tune_lightgbm ────────────────────────────────────────────────────────────


def test_tune_lightgbm_returns_estimator_and_params(small_regression):
    X_tr, y_tr, X_val, y_val = small_regression
    model, params = tune_lightgbm(X_tr, y_tr, X_val, y_val, SMALL_LGBM_GRID, n_iter=4)
    assert isinstance(model, LGBMRegressor)
    assert isinstance(params, dict)


def test_tune_lightgbm_params_subset_of_grid(small_regression):
    X_tr, y_tr, X_val, y_val = small_regression
    _, params = tune_lightgbm(X_tr, y_tr, X_val, y_val, SMALL_LGBM_GRID, n_iter=4)
    for key in params:
        assert key in SMALL_LGBM_GRID


def test_tune_lightgbm_estimator_predicts(small_regression):
    X_tr, y_tr, X_val, y_val = small_regression
    model, _ = tune_lightgbm(X_tr, y_tr, X_val, y_val, SMALL_LGBM_GRID, n_iter=4)
    preds = model.predict(X_tr)
    assert preds.shape == (48,)


# ── tune_rf ──────────────────────────────────────────────────────────────────


def test_tune_rf_returns_estimator_and_params(small_regression):
    X_tr, y_tr, X_val, y_val = small_regression
    model, params = tune_rf(X_tr, y_tr, X_val, y_val, SMALL_RF_GRID, n_iter=4)
    assert isinstance(model, RandomForestRegressor)
    assert isinstance(params, dict)


def test_tune_rf_estimator_predicts(small_regression):
    X_tr, y_tr, X_val, y_val = small_regression
    model, _ = tune_rf(X_tr, y_tr, X_val, y_val, SMALL_RF_GRID, n_iter=4)
    preds = model.predict(X_tr)
    assert preds.shape == (48,)


# ── make_model ───────────────────────────────────────────────────────────────


def test_make_model_lightgbm():
    params = {"n_estimators": 100, "learning_rate": 0.1}
    model = make_model("LightGBM", params)
    assert isinstance(model, LGBMRegressor)
    assert model.n_estimators == 100


def test_make_model_rf():
    params = {"n_estimators": 200, "max_depth": 10}
    model = make_model("RandomForest", params)
    assert isinstance(model, RandomForestRegressor)
    assert model.max_depth == 10


def test_make_model_unknown_raises():
    with pytest.raises(ValueError, match="Unknown model"):
        make_model("XGBoost", {})


# ── save / load params ───────────────────────────────────────────────────────


def test_save_and_load_params(tmp_path, small_regression):
    X_tr, y_tr, X_val, y_val = small_regression
    _, params = tune_lightgbm(X_tr, y_tr, X_val, y_val, SMALL_LGBM_GRID, n_iter=4)
    path = tmp_path / "params.json"
    save_params(params, path)
    loaded = load_params(path)
    assert loaded == params


def test_save_params_writes_valid_json(tmp_path, small_regression):
    X_tr, y_tr, X_val, y_val = small_regression
    _, params = tune_lightgbm(X_tr, y_tr, X_val, y_val, SMALL_LGBM_GRID, n_iter=4)
    path = tmp_path / "params.json"
    save_params(params, path)
    with open(path) as f:
        parsed = json.load(f)
    assert isinstance(parsed, dict)
