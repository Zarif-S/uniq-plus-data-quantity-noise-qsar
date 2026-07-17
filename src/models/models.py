"""Baseline model factory and evaluation utilities for UNIQ+ QSAR experiments."""

import numpy as np
from lightgbm import LGBMRegressor
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import BayesianRidge, Ridge
from sklearn.metrics import mean_squared_error, r2_score
from xgboost import XGBRegressor


def get_baseline_models():
    """Return a fresh dict of six unfitted sklearn-compatible baseline regressors.

    All models train with squared-error (MSE) loss — each library's default,
    not explicitly overridden, so comparisons are on equal footing:
      - MeanPredictor    : always predicts training set mean; trivial lower bound
      - Ridge             : L2-regularised OLS (alpha=1.0); plain OLS is ill-conditioned
                            on 2048-dim binary fingerprints and fails catastrophically
      - BayesianRidge    : Gaussian likelihood (equivalent to MSE)
      - RandomForest     : criterion="squared_error" (sklearn default)
      - XGBoost          : objective="reg:squarederror" (XGBoost default)
      - LightGBM         : objective="regression_l2" (LightGBM default)
    """
    return {
        "MeanPredictor": DummyRegressor(strategy="mean"),
        "Ridge": Ridge(alpha=1.0),
        "BayesianRidge": BayesianRidge(),
        "RandomForest": RandomForestRegressor(n_estimators=100, random_state=42),
        "XGBoost": XGBRegressor(n_estimators=100, random_state=42, verbosity=0),
        "LightGBM": LGBMRegressor(n_estimators=100, random_state=42, verbose=-1),
    }


def evaluate_model(model, X_test, y_test, y_pred=None):
    """Return {R2, RMSE, MSE} for a fitted model evaluated on test data.

    Pass y_pred to reuse already-computed predictions and skip a redundant predict call.
    """
    if y_pred is None:
        y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred) # mse calculated but not returned/printed in the notebook as of yet
    return {
        "R2": r2_score(y_test, y_pred),
        "RMSE": float(np.sqrt(mse)),
        "MSE": float(mse),
    }
