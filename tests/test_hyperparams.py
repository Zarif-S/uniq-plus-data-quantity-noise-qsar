"""Sanity tests for src/hyperparams."""

from src.hyperparams import (
    PARAM_GRID_STAGES,
    n_jobs_model,
    param_base_LGB,
    param_base_RF,
    param_base_XGB,
)


def test_single_parallelism_layer_to_avoid_oversubscription():
    # Option B (ADR-008 update, 2026-08-02): the ESTIMATOR owns all cores (n_jobs_model=-1) and the
    # outer GridSearchCV/cross_val_score runs one fit at a time (notebook n_jobs_cv=1). This is a
    # single parallelism layer — the invariant that matters is that the two layers are never both
    # parallel (that nesting oversubscribes, ~64 threads on 8 cores). The 2026-08-02 benchmark showed
    # this layout is 2.1x faster than the inverse (outer=-1, estimator=1) on the tree-heavy grid,
    # because forests parallelise within a fit better than across folds. LightGBM defaults to all
    # cores anyway, so -1 here is explicit-and-consistent. If a notebook ever sets n_jobs_cv=-1, these
    # MUST flip to 1 in the same change — that pairing is the oversubscription trap.
    assert n_jobs_model == -1
    assert param_base_RF["n_jobs"] == -1
    assert param_base_XGB["n_jobs"] == -1
    assert param_base_LGB["n_jobs"] == -1


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
