"""Hyperparameter tuning utilities for UNIQ+ QSAR experiments.

Used for clean-data reference tuning (Phase 3) and re-tuning under each
experimental condition (Phases 4-6). CV scoring uses MAE to avoid
disproportionate influence of noisy labels under noise injection.

Tuning uses a fixed held-out validation set (PredefinedSplit) rather than
k-fold CV. The caller is responsible for the train/val split.
"""

import json

import numpy as np
from lightgbm import LGBMRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import PredefinedSplit, RandomizedSearchCV

LGBM_PARAM_GRID = {
    "n_estimators": [100, 300, 500, 800],
    "learning_rate": [0.01, 0.05, 0.1, 0.2],
    "num_leaves": [15, 31, 63, 127],
    "min_child_samples": [10, 20, 50],
    "subsample": [0.7, 0.8, 1.0],
    "colsample_bytree": [0.7, 0.8, 1.0],
}

RF_PARAM_GRID = {
    "n_estimators": [100, 300, 500],
    "max_depth": [None, 10, 20, 30],
    "min_samples_leaf": [1, 5, 10],
    "max_features": ["sqrt", "log2", 0.3],
}


def _make_predefined_split(X_train, y_train, X_val, y_val):
    """Combine train and val arrays and return (X_combined, y_combined, PredefinedSplit)."""
    split_idx = np.concatenate([
        -np.ones(len(X_train), dtype=int),  # -1 = always train
         np.zeros(len(X_val),  dtype=int),  #  0 = validation fold
    ])
    X_combined = np.vstack([X_train, X_val])
    y_combined  = np.concatenate([y_train, y_val])
    return X_combined, y_combined, PredefinedSplit(split_idx)


def tune_lightgbm(X_train, y_train, X_val, y_val, param_grid=None, n_iter=50, random_state=42):
    """Tune and train LightGBM on a fixed val set; return (fitted_model, best_params).

    Uses PredefinedSplit so the val set is always the same held-out set.
    After selecting best params, refits on the full train+val data.
    """
    if param_grid is None:
        param_grid = LGBM_PARAM_GRID
    X_combined, y_combined, ps = _make_predefined_split(X_train, y_train, X_val, y_val)
    search = RandomizedSearchCV(
        LGBMRegressor(random_state=random_state, verbose=-1),
        param_distributions=param_grid,
        n_iter=n_iter,
        cv=ps,
        scoring="neg_mean_absolute_error",
        random_state=random_state,
        n_jobs=-1,
    )
    search.fit(X_combined, y_combined)
    return search.best_estimator_, search.best_params_


def tune_rf(X_train, y_train, X_val, y_val, param_grid=None, n_iter=50, random_state=42):
    """Tune and train RandomForest on a fixed val set; return (fitted_model, best_params).

    Uses PredefinedSplit so the val set is always the same held-out set.
    After selecting best params, refits on the full train+val data.
    """
    if param_grid is None:
        param_grid = RF_PARAM_GRID
    X_combined, y_combined, ps = _make_predefined_split(X_train, y_train, X_val, y_val)
    search = RandomizedSearchCV(
        RandomForestRegressor(random_state=random_state),
        param_distributions=param_grid,
        n_iter=n_iter,
        cv=ps,
        scoring="neg_mean_absolute_error",
        random_state=random_state,
        n_jobs=-1,
    )
    search.fit(X_combined, y_combined)
    return search.best_estimator_, search.best_params_


def make_model(model_name, params):
    """Create an unfitted model from a params dict."""
    if model_name == "LightGBM":
        return LGBMRegressor(**params, verbose=-1)
    elif model_name == "RandomForest":
        return RandomForestRegressor(**params)
    else:
        raise ValueError(f"Unknown model: {model_name}")


def save_params(params, path):
    """Serialise a hyperparameter dict to JSON at path."""
    with open(path, "w") as f:
        json.dump(params, f, indent=2)


def load_params(path):
    """Load a hyperparameter dict from a JSON file."""
    with open(path) as f:
        return json.load(f)
