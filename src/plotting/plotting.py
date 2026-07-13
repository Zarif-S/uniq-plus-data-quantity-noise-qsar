"""Reusable plotting utilities for UNIQ+ EDA and results."""

import math

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde
from sklearn.metrics import r2_score


def endpoint_distributions(df, endpoint_cols, figsize=(14, 8)):
    """Histogram + KDE grid for a list of endpoint columns. Returns matplotlib Figure.

    NaN values are silently dropped per column — run missing_value_report() first
    to check counts. Grid dimensions are computed from len(endpoint_cols).
    """
    n = len(endpoint_cols)
    n_cols = min(3, n)
    n_rows = math.ceil(n / n_cols)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize, squeeze=False)
    axes = axes.flatten()

    for i, col in enumerate(endpoint_cols):
        ax = axes[i]
        data = df[col].dropna()

        ax.hist(data, bins=40, density=True, alpha=0.6, color="steelblue", edgecolor="white")

        if len(data) > 1 and np.var(data) > 0:
            kde = gaussian_kde(data)
            x = np.linspace(data.min(), data.max(), 300)
            ax.plot(x, kde(x), color="darkblue", linewidth=2)

        ax.set_title(col, fontsize=10, pad=6)
        ax.set_xlabel("Value")
        ax.set_ylabel("Density")
        ax.tick_params(labelsize=8)

    for j in range(n, len(axes)):
        axes[j].set_visible(False)

    fig.tight_layout()
    return fig


def pred_vs_actual_grid(preds_dict, title="", figsize=None):
    """Scatter grid of predicted vs actual values for multiple models. Returns matplotlib Figure.

    preds_dict: {model_name: (y_test, y_pred)} — one entry per model.
    title: optional suptitle (e.g. endpoint name).
    """
    n = len(preds_dict)
    if figsize is None:
        figsize = (4 * n, 4)

    fig, axes = plt.subplots(1, n, figsize=figsize, squeeze=False)
    axes = axes.flatten()

    for ax, (name, (y_test, y_pred)) in zip(axes, preds_dict.items()):
        y_test = np.asarray(y_test)
        y_pred = np.asarray(y_pred)

        ax.scatter(y_test, y_pred, alpha=0.4, s=12, color="steelblue")

        lo = min(y_test.min(), y_pred.min())
        hi = max(y_test.max(), y_pred.max())
        ax.plot([lo, hi], [lo, hi], color="crimson", linewidth=1.2, linestyle="--")

        r2 = r2_score(y_test, y_pred)
        ax.annotate(f"R²={r2:.3f}", xy=(0.05, 0.92), xycoords="axes fraction", fontsize=8)

        ax.set_title(name, fontsize=9)
        ax.set_xlabel("Actual")
        ax.set_ylabel("Predicted")
        ax.tick_params(labelsize=7)

    if title:
        fig.suptitle(title, fontsize=11, y=1.02)

    fig.tight_layout()
    return fig
