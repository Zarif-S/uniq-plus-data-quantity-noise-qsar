"""Metric functions for UNIQ+ QSAR experiments."""

import warnings

import numpy as np
from scipy.stats import ConstantInputWarning, pearsonr
from sklearn.metrics import mean_absolute_error


def pearson_r(y_true, y_pred):
    """Pearson correlation coefficient.

    Returns NaN (ConstantInputWarning suppressed) if either input has zero variance —
    e.g. a CV fold where predictions collapse to a single value. Callers aggregating
    over folds should use np.nanmean, not np.mean, to avoid one NaN fold silently
    poisoning the whole average.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConstantInputWarning)
        r, _ = pearsonr(np.asarray(y_true), np.asarray(y_pred))
    return float(r)


def mae(y_true, y_pred):
    """Mean absolute error."""
    return float(mean_absolute_error(np.asarray(y_true), np.asarray(y_pred)))
