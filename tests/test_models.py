"""Sanity tests for src/models."""

import numpy as np
import pytest
from src.hyperparams import PARAM_GRID_STAGES
from src.models import (
    evaluate_model,
    get_baseline_models,
    get_paper_models,
    invalidate_checkpoint,
    load_eval_checkpoint,
    model_validation,
    run_checkpointed_eval,
    tune_paper_model,
)


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
    assert set(models.keys()) == {"RF", "SVM", "XGBoost", "LightGBM", "Lasso", "BayesianRidge"}


def test_get_paper_models_bayesianridge_is_deterministic_estimator():
    from sklearn.linear_model import BayesianRidge
    model = get_paper_models()["BayesianRidge"]
    assert isinstance(model, BayesianRidge)
    assert "random_state" not in model.get_params()   # deterministic, no seed


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

# --- run_checkpointed_eval -------------------------------------------------

def _counting_compute():
    """Return (compute_one, calls) where compute_one records each key it actually computes."""
    calls = []

    def compute_one(key):
        calls.append(key)
        ep, fs, model, arm = key
        row = {"endpoint": ep, "featureset": fs, "model": model, "arm": arm, "MAE": len(calls) * 1.0}
        pred = {"y_pred_test": np.array([len(calls)])}
        return row, pred

    return compute_one, calls


def test_run_checkpointed_eval_computes_all_on_empty(tmp_path):
    rp, pp = tmp_path / "res.csv", tmp_path / "pred.pkl"
    keys = [("HLM", "fcfp4", "RF", "base"), ("HLM", "fcfp4", "SVM", "base")]
    compute_one, calls = _counting_compute()
    results_df, predictions = run_checkpointed_eval(keys, compute_one, rp, pp, verbose=False)
    assert calls == keys                       # both computed
    assert len(results_df) == 2 and len(predictions) == 2
    assert rp.exists() and pp.exists()         # both files persisted


def test_run_checkpointed_eval_skips_existing(tmp_path):
    rp, pp = tmp_path / "res.csv", tmp_path / "pred.pkl"
    keys = [("HLM", "fcfp4", "RF", "base"), ("HLM", "fcfp4", "SVM", "base")]
    # First pass computes both.
    run_checkpointed_eval(keys, _counting_compute()[0], rp, pp, verbose=False)
    # Second pass with a fresh counter must recompute nothing.
    compute_one, calls = _counting_compute()
    results_df, predictions = run_checkpointed_eval(keys, compute_one, rp, pp, verbose=False)
    assert calls == []                         # nothing recomputed
    assert len(results_df) == 2 and len(predictions) == 2


def test_run_checkpointed_eval_computes_only_new_keys(tmp_path):
    rp, pp = tmp_path / "res.csv", tmp_path / "pred.pkl"
    first = [("HLM", "fcfp4", "RF", "base")]
    run_checkpointed_eval(first, _counting_compute()[0], rp, pp, verbose=False)
    # Add a new key alongside the already-done one.
    both = first + [("HLM", "fcfp4", "SVM", "base")]
    compute_one, calls = _counting_compute()
    results_df, predictions = run_checkpointed_eval(both, compute_one, rp, pp, verbose=False)
    assert calls == [("HLM", "fcfp4", "SVM", "base")]   # only the new one
    assert len(results_df) == 2 and len(predictions) == 2


def test_run_checkpointed_eval_dedupes_stale_csv_row(tmp_path):
    # Simulate a crash-between-writes: a results row exists on disk but its key is absent
    # from the predictions checkpoint. The next run must recompute it and leave exactly one row.
    import joblib
    import pandas as pd
    rp, pp = tmp_path / "res.csv", tmp_path / "pred.pkl"
    key = ("HLM", "fcfp4", "RF", "base")
    pd.DataFrame([{"endpoint": "HLM", "featureset": "fcfp4", "model": "RF", "arm": "base", "MAE": 99.0}]).to_csv(rp, index=False)
    joblib.dump({}, pp)                        # predictions empty -> key looks 'not done'
    compute_one, calls = _counting_compute()
    results_df, _ = run_checkpointed_eval([key], compute_one, rp, pp, verbose=False)
    assert calls == [key]                      # recomputed
    assert len(results_df) == 1                # stale duplicate dropped, not two rows
    assert results_df.iloc[0]["MAE"] == 1.0    # fresh value kept, not the stale 99.0


def test_load_eval_checkpoint_absent_returns_empty(tmp_path):
    results_df, predictions = load_eval_checkpoint(tmp_path / "nope.csv", tmp_path / "nope.pkl")
    assert results_df.empty and predictions == {}


# --- invalidate_checkpoint -------------------------------------------------

def _seed_checkpoint(tmp_path, keys):
    """Compute a fresh checkpoint over `keys` and return (results_path, predictions_path)."""
    rp, pp = tmp_path / "res.csv", tmp_path / "pred.pkl"
    run_checkpointed_eval(keys, _counting_compute()[0], rp, pp, verbose=False)
    return rp, pp


_KEYS = [
    ("HLM", "fcfp4", "RF", "base"),
    ("HLM", "fcfp4", "SVM", "base"),
    ("MDR1", "hybrid", "RF", "base"),
]


def test_invalidate_checkpoint_by_model_removes_from_both_files(tmp_path):
    rp, pp = _seed_checkpoint(tmp_path, _KEYS)
    removed = invalidate_checkpoint(rp, pp, model="RF")
    assert removed == 2                                    # both RF keys
    results_df, predictions = load_eval_checkpoint(rp, pp)
    assert set(predictions.keys()) == {("HLM", "fcfp4", "SVM", "base")}
    assert results_df["model"].tolist() == ["SVM"]        # CSV pruned too


def test_invalidate_checkpoint_multiple_filters_are_anded(tmp_path):
    rp, pp = _seed_checkpoint(tmp_path, _KEYS)
    removed = invalidate_checkpoint(rp, pp, model="RF", endpoint="HLM")
    assert removed == 1                                    # only HLM+RF, not MDR1+RF
    _, predictions = load_eval_checkpoint(rp, pp)
    assert ("MDR1", "hybrid", "RF", "base") in predictions


def test_invalidate_checkpoint_collection_value(tmp_path):
    rp, pp = _seed_checkpoint(tmp_path, _KEYS)
    removed = invalidate_checkpoint(rp, pp, featureset={"hybrid", "fcfp4"})
    assert removed == 3                                    # all three keys matched


def test_invalidate_checkpoint_no_filters_clears_all(tmp_path):
    rp, pp = _seed_checkpoint(tmp_path, _KEYS)
    removed = invalidate_checkpoint(rp, pp)
    assert removed == 3
    results_df, predictions = load_eval_checkpoint(rp, pp)
    assert predictions == {} and results_df.empty


def test_invalidate_checkpoint_unknown_field_raises(tmp_path):
    rp, pp = _seed_checkpoint(tmp_path, _KEYS)
    with pytest.raises(ValueError, match="unknown filter field"):
        invalidate_checkpoint(rp, pp, mdoel="RF")         # typo'd field name


def test_invalidate_then_recompute_only_touches_removed_keys(tmp_path):
    rp, pp = _seed_checkpoint(tmp_path, _KEYS)
    invalidate_checkpoint(rp, pp, model="RF")
    compute_one, calls = _counting_compute()
    run_checkpointed_eval(_KEYS, compute_one, rp, pp, verbose=False)
    assert set(calls) == {("HLM", "fcfp4", "RF", "base"), ("MDR1", "hybrid", "RF", "base")}
    _, predictions = load_eval_checkpoint(rp, pp)
    assert len(predictions) == 3                           # back to full set
