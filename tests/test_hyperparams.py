"""Sanity tests for src/hyperparams."""

from src.hyperparams import (
    PARAM_GRID_STAGES,
    n_jobs_model,
    param_base_LGB,
    param_base_RF,
    param_base_XGB,
)


def test_estimators_single_threaded_to_avoid_oversubscription():
    # Estimators must stay serial so the outer GridSearchCV/cross_val_score (n_jobs_cv=-1) owns the
    # cores. A parallel estimator nested in a parallel CV loop oversubscribes (~64 threads on 8
    # cores). LightGBM defaults to all cores, so it must set n_jobs explicitly too.
    assert n_jobs_model == 1
    assert param_base_RF["n_jobs"] == 1
    assert param_base_XGB["n_jobs"] == 1
    assert param_base_LGB["n_jobs"] == 1


def test_rf_oob_score_disabled():
    # OOB is never read (tuning selects on CV R2, eval reports Pearson r); computing it only adds a
    # redundant out-of-bag prediction pass per forest fit.
    assert param_base_RF["oob_score"] is False


def test_param_grid_stages_has_all_model_keys():
    assert set(PARAM_GRID_STAGES.keys()) == {"RF", "SVM", "XGBoost", "LightGBM", "Lasso"}


def test_param_grid_stages_xgb_lgb_are_staged():
    assert len(PARAM_GRID_STAGES["XGBoost"]) == 5
    assert len(PARAM_GRID_STAGES["LightGBM"]) == 4


def test_param_grid_stages_single_stage_models():
    assert len(PARAM_GRID_STAGES["RF"]) == 1
    assert len(PARAM_GRID_STAGES["SVM"]) == 1
    assert len(PARAM_GRID_STAGES["Lasso"]) == 1
