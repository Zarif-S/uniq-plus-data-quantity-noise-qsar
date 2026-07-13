"""Baseline model factory and evaluation utilities for UNIQ+ QSAR experiments."""

import numpy as np
from lightgbm import LGBMRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import BayesianRidge, LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from xgboost import XGBRegressor


def get_baseline_models():
    """Return a fresh dict of five unfitted sklearn-compatible baseline regressors.

    All five models train with squared-error (MSE) loss — each library's default,
    not explicitly overridden, so comparisons are on equal footing:
      - LinearRegression : OLS (minimises sum of squared residuals)
      - BayesianRidge    : Gaussian likelihood (equivalent to MSE)
      - RandomForest     : criterion="squared_error" (sklearn default)
      - XGBoost          : objective="reg:squarederror" (XGBoost default)
      - LightGBM         : objective="regression_l2" (LightGBM default)
    """
    return {
        "LinearRegression": LinearRegression(),
        "BayesianRidge": BayesianRidge(),
        "RandomForest": RandomForestRegressor(n_estimators=100, random_state=42),
        "XGBoost": XGBRegressor(n_estimators=100, random_state=42, verbosity=0),
        "LightGBM": LGBMRegressor(n_estimators=100, random_state=42, verbose=-1),
    }


def evaluate_model(model, X_test, y_test):
    """Return {R2, RMSE, MSE} for a fitted model evaluated on test data."""
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred) # mse calculated but not returned/printed in the notebook as of yet
    return {
        "R2": r2_score(y_test, y_pred),
        "RMSE": float(np.sqrt(mse)),
        "MSE": float(mse),
    }
