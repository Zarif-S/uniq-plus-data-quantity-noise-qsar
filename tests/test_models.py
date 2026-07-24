"""Sanity tests for src/models."""

import numpy as np
import pytest
from src.hyperparams import PARAM_GRID_STAGES
from src.models import evaluate_model, get_baseline_models, get_paper_models, model_validation, tune_paper_model


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


def test_get_paper_models_has_expected_keys():
    models = get_paper_models()
    assert set(models.keys()) == {"RF", "SVM", "XGBoost", "LightGBM", "Lasso"}


def test_get_paper_models_are_unfitted_and_fresh():
    m1 = get_paper_models()
    m2 = get_paper_models()
    for name in m1:
        assert hasattr(m1[name], "fit")
        assert hasattr(m1[name], "predict")
        assert m1[name] is not m2[name]


def _synthetic_regression_data(n=60, seed=0):
    rng = np.random.default_rng(seed)
    X = rng.random((n, 4))
    y = X @ np.array([1.0, -2.0, 0.5, 3.0]) + rng.normal(scale=0.01, size=n)
    return X, y


def test_tune_paper_model_changes_params_across_stages():
    X, y = _synthetic_regression_data()
    from sklearn.linear_model import Lasso
    model = Lasso(alpha=0.1, random_state=42)
    tuned = tune_paper_model(model, X, y, PARAM_GRID_STAGES["Lasso"], n_jobs_cv=1)
    assert tuned is model
    assert tuned.get_params()["alpha"] in PARAM_GRID_STAGES["Lasso"][0]["alpha"]


def test_model_validation_returns_expected_keys():
    X, y = _synthetic_regression_data()
    X_train, X_test = X[:40], X[40:]
    y_train, y_test = y[:40], y[40:]
    from sklearn.linear_model import Lasso
    model = Lasso(alpha=0.1, random_state=42)
    result = model_validation(model, X_train, y_train, X_test, y_test, n_repeats=1)
    assert set(result.keys()) == {"Pearson_r_CV", "Pearson_r_test", "cv_scores", "y_pred_test"}
    assert -1.0 <= result["Pearson_r_CV"] <= 1.0
    assert -1.0 <= result["Pearson_r_test"] <= 1.0
    assert result["y_pred_test"].shape == y_test.shape
    assert len(result["cv_scores"]) == 5 * 1


def test_model_validation_n_jobs_matches_serial():
    # Parallelizing independent CV folds must not change results -- each fold is fit on a
    # fixed, pre-determined split, so serial vs parallel execution should be numerically
    # identical for a deterministic model like Lasso.
    X, y = _synthetic_regression_data()
    X_train, X_test = X[:40], X[40:]
    y_train, y_test = y[:40], y[40:]
    from sklearn.linear_model import Lasso
    result_serial = model_validation(Lasso(alpha=0.1, random_state=42), X_train, y_train, X_test, y_test, n_repeats=1, n_jobs=1)
    result_parallel = model_validation(Lasso(alpha=0.1, random_state=42), X_train, y_train, X_test, y_test, n_repeats=1, n_jobs=-1)
    assert np.allclose(result_serial["cv_scores"], result_parallel["cv_scores"], equal_nan=True)
    assert result_serial["Pearson_r_test"] == result_parallel["Pearson_r_test"]


def test_model_validation_nan_cv_folds_do_not_poison_mean():
    # DummyRegressor(strategy="mean") predicts a constant on every fold, so the CV Pearson
    # scorer sees zero-variance predictions and returns NaN for every fold. Pearson_r_CV
    # should come out NaN too (nanmean over all-NaN input), not silently error, and
    # Pearson_r_test (single held-out value) must still be computed cleanly.
    from sklearn.dummy import DummyRegressor
    X, y = _synthetic_regression_data()
    X_train, X_test = X[:40], X[40:]
    y_train, y_test = y[:40], y[40:]
    model = DummyRegressor(strategy="mean")
    with pytest.warns(UserWarning, match="NaN Pearson r"):
        result = model_validation(model, X_train, y_train, X_test, y_test, n_repeats=1)
    assert np.isnan(result["Pearson_r_CV"])
    assert np.isnan(result["cv_scores"]).all()