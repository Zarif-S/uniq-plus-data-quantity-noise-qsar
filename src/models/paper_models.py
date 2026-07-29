"""Paper-recreation model factory, tuning, and validation for the ADME public dataset.

Reproduces the exact procedure in Fang et al. (2023)'s ADME_ML_public.py — separate from
src/models/models.py's fixed 6-model baseline set, which serves a different purpose (the
noise/learning-curve experiments) and must not be changed to accommodate notebook 01.5_adme_recreation.
"""

import os
import warnings

import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import BayesianRidge, Lasso
from sklearn.metrics import make_scorer
from sklearn.model_selection import GridSearchCV, RepeatedKFold, cross_val_score
from sklearn.svm import SVR
from xgboost import XGBRegressor

from src.hyperparams import (
    param_base_BayesianRidge,
    param_base_FCNN,
    param_base_Lasso,
    param_base_LGB,
    param_base_RF,
    param_base_SVM,
    param_base_XGB,
)
from src.metrics import pearson_r
from src.models.fcnn import FCNN

_pearson_scorer = make_scorer(pearson_r, greater_is_better=True)


def load_eval_checkpoint(results_path, predictions_path):
    """Load a persisted (results_df, predictions) checkpoint pair, or empty defaults if absent."""
    predictions = joblib.load(predictions_path) if os.path.exists(predictions_path) else {}
    results_df = pd.read_csv(results_path) if os.path.exists(results_path) else pd.DataFrame()
    return results_df, predictions


def run_checkpointed_eval(keys, compute_one, results_path, predictions_path,
                          key_cols=("endpoint", "featureset", "model", "arm"), verbose=True):
    """Resumably evaluate `keys`, skipping any already present in the on-disk predictions checkpoint.

    keys:        iterable of hashable keys, e.g. (endpoint, featureset, model, arm).
    compute_one: callback (key) -> (row: dict, pred: dict). `row` is one results_df record;
                 `pred` is stored under `key` in the predictions dict.

    The predictions dict (keyed by `key`) is the source of truth for what is 'done'. After each
    newly computed key, results_df is rewritten to CSV *first* then predictions to pkl, so a crash
    between the two writes leaves a recomputable state (the CSV row is de-duplicated on `key_cols`,
    keep='last', on the next run). Returns (results_df, predictions).
    """
    results_df, predictions = load_eval_checkpoint(results_path, predictions_path)
    rows = results_df.to_dict("records")
    done = set(predictions.keys())
    for key in keys:
        if key in done:
            if verbose:
                print(f"skip  {key}")
            continue
        row, pred = compute_one(key)
        rows.append(row)
        predictions[key] = pred
        df = pd.DataFrame(rows)
        if set(key_cols).issubset(df.columns):
            df = df.drop_duplicates(subset=list(key_cols), keep="last")
            rows = df.to_dict("records")
        df.to_csv(results_path, index=False)
        joblib.dump(predictions, predictions_path)
        done.add(key)
        if verbose:
            print(f"done  {key}")
    return pd.DataFrame(rows), predictions


def invalidate_checkpoint(results_path, predictions_path,
                          key_fields=("endpoint", "featureset", "model", "arm"), **filters):
    """Remove every checkpoint entry whose key matches ALL `filters`, from both files, so the
    next `run_checkpointed_eval` recomputes them.

    A 'key' is one unit of work: the tuple (endpoint, featureset, model, arm) identifying one
    results row / one predictions entry. Each filter kwarg names a key field; its value may be a
    scalar or a collection of allowed values. Examples:
        invalidate_checkpoint(rp, pp, model="RF")               # every RF key (all ep/fs/arm)
        invalidate_checkpoint(rp, pp, model="RF", arm="base")   # only RF base keys
        invalidate_checkpoint(rp, pp, featureset={"hybrid", "rdkit"})
    Passing no filters clears everything. Rewrites both files and returns the number of keys removed.
    """
    unknown = set(filters) - set(key_fields)
    if unknown:
        raise ValueError(f"unknown filter field(s) {sorted(unknown)}; valid: {list(key_fields)}")

    def _as_set(v):
        return {v} if isinstance(v, str) or not hasattr(v, "__iter__") else set(v)

    filters = {f: _as_set(v) for f, v in filters.items()}
    results_df, predictions = load_eval_checkpoint(results_path, predictions_path)

    def matches(key):
        row = dict(zip(key_fields, key))
        return all(row[f] in allowed for f, allowed in filters.items())

    doomed = [k for k in predictions if matches(k)]
    for k in doomed:
        del predictions[k]

    if not results_df.empty and set(key_fields).issubset(results_df.columns):
        mask = pd.Series(True, index=results_df.index)
        for f, allowed in filters.items():
            mask &= results_df[f].isin(allowed)
        results_df = results_df[~mask]

    results_df.to_csv(results_path, index=False)
    joblib.dump(predictions, predictions_path)
    return len(doomed)


def get_paper_models(random_state=42):
    """Unfitted RF/SVM/XGBoost/LightGBM/Lasso/BayesianRidge regressors using the paper's base
    hyperparameters. BayesianRidge is deterministic (no random_state) and, like SVM/Lasso, expects
    scaled features — callers must feed it the RobustScaler'd matrices.

    FCNN (DeepChem MultitaskRegressor) also expects scaled features. MPNN1/MPNN2 are graph models
    (SMILES in, no X matrix) and are handled separately in the notebook loop, not here.
    """
    return {
        "RF":            RandomForestRegressor(**param_base_RF, random_state=random_state),
        "SVM":           SVR(**param_base_SVM),
        "XGBoost":       XGBRegressor(**param_base_XGB, random_state=random_state, verbosity=0),
        "LightGBM":      LGBMRegressor(**param_base_LGB, random_state=random_state, verbose=-1),
        "Lasso":         Lasso(**param_base_Lasso, random_state=random_state),
        "BayesianRidge": BayesianRidge(**param_base_BayesianRidge),
        "FCNN":          FCNN(**param_base_FCNN, random_state=random_state),
    }


def tune_paper_model(model, X_train, y_train, stages, n_jobs_cv=-1, cv=5):
    """Sequentially GridSearchCV each stage in `stages` (cv=5, scoring='r2'), locking in
    best_params_ before the next stage — matches the paper's staged tuning exactly. Mutates
    and returns `model`.
    """
    for stage in stages:
        gsearch = GridSearchCV(estimator=model, param_grid=stage, scoring="r2", n_jobs=n_jobs_cv, cv=cv)
        gsearch.fit(X_train, y_train)
        model.set_params(**gsearch.best_params_)
    return model


def model_validation(model, X_train, y_train, X_test, y_test,
                      n_splits=5, n_repeats=3, random_state=128, n_jobs=1):
    """Reproduce the paper's model_validation(): fit model once on the full X_train, compute
    cv_pearson_r via RepeatedKFold(n_splits, n_repeats, random_state) + a Pearson scorer on
    X_train (diagnostic only — does not affect the fitted model), and Pearson_r_test via Pearson
    r on the held-out X_test using the model fit on the full X_train. Also returns y_pred_test —
    the paper's script never computes MAE at all (confirmed: no mean_absolute_error import or
    usage anywhere in ADME_ML_public.py), so whatever domain-of-applicability MAE analysis the
    paper text describes must live in a separate, unpublished script. We add MAE ourselves this
    session (see src.metrics.mae), computed from this same y_pred_test capture.

    n_jobs controls parallelism across the 15 RepeatedKFold folds (not passed to the paper's
    original script, which ran them serially) — safe to set to -1 even when the underlying
    model itself also uses n_jobs=-1 internally (e.g. RF/XGBoost/LightGBM): joblib/loky give
    each fold's fit its own process, so this is nested-but-not-conflicting parallelism, not
    double-counting the same threads.
    """
    rkf = RepeatedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=random_state)
    cv_scores = cross_val_score(model, X_train, y_train, scoring=_pearson_scorer, cv=rkf, n_jobs=n_jobs)
    n_nan = int(np.sum(np.isnan(cv_scores)))
    if n_nan:
        warnings.warn(
            f"{n_nan}/{len(cv_scores)} CV folds returned NaN Pearson r (constant predictions "
            "or targets in that fold) — averaging with nanmean, excluding them."
        )
    model.fit(X_train, y_train)
    y_pred_test = model.predict(X_test)
    r_test = pearson_r(y_test, y_pred_test)
    with warnings.catch_warnings():
        # already warned above about NaN folds; suppress numpy's redundant "Mean of empty
        # slice" RuntimeWarning for the all-NaN case
        warnings.simplefilter("ignore", RuntimeWarning)
        cv_pearson_r = float(np.nanmean(cv_scores))
    return {
        "Pearson_r_CV":   cv_pearson_r,
        "Pearson_r_test": r_test,
        "cv_scores":      cv_scores,
        "y_pred_test":    y_pred_test,
    }
