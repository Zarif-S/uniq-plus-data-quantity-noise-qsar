"""Sanity tests for src/hyperparams."""

from src.hyperparams import PARAM_GRID_STAGES, n_jobs_model


def test_n_jobs_defined():
    assert n_jobs_model == -1


def test_param_grid_stages_has_all_model_keys():
    assert set(PARAM_GRID_STAGES.keys()) == {"RF", "SVM", "XGBoost", "LightGBM", "Lasso"}


def test_param_grid_stages_xgb_lgb_are_staged():
    assert len(PARAM_GRID_STAGES["XGBoost"]) == 5
    assert len(PARAM_GRID_STAGES["LightGBM"]) == 4


def test_param_grid_stages_single_stage_models():
    assert len(PARAM_GRID_STAGES["RF"]) == 1
    assert len(PARAM_GRID_STAGES["SVM"]) == 1
    assert len(PARAM_GRID_STAGES["Lasso"]) == 1
