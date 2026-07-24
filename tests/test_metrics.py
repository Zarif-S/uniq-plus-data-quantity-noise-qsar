"""Sanity tests for src/metrics."""

import warnings

import numpy as np
from sklearn.metrics import mean_absolute_error
from src.metrics import mae, pearson_r


def test_pearson_r_perfect_correlation():
    y = np.array([1.0, 2.0, 3.0, 4.0])
    assert abs(pearson_r(y, y) - 1.0) < 1e-9


def test_pearson_r_perfect_anticorrelation():
    y_true = np.array([1.0, 2.0, 3.0, 4.0])
    y_pred = np.array([4.0, 3.0, 2.0, 1.0])
    assert abs(pearson_r(y_true, y_pred) - (-1.0)) < 1e-9


def test_mae_matches_sklearn():
    y_true = np.array([1.0, 2.0, 3.0, 4.0])
    y_pred = np.array([1.1, 1.9, 3.2, 3.7])
    assert abs(mae(y_true, y_pred) - mean_absolute_error(y_true, y_pred)) < 1e-9


def test_mae_non_negative():
    y_true = np.array([1.0, 2.0, 3.0])
    y_pred = np.array([1.5, 1.5, 3.5])
    assert mae(y_true, y_pred) >= 0


def test_pearson_r_constant_input_returns_nan_without_warning_leaking():
    y_true = np.array([1.0, 2.0, 3.0, 4.0])
    y_pred = np.array([5.0, 5.0, 5.0, 5.0])  # zero variance -> ConstantInputWarning internally
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # any leaked warning fails the test
        result = pearson_r(y_true, y_pred)
    assert np.isnan(result)
