"""Reusable plotting utilities for UNIQ+ EDA and results."""

import math

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde
from sklearn.metrics import r2_score

# All six ADME endpoint values are log10-transformed in the raw data (see DECISIONS.md —
# "y values never scaled, already log-transformed in raw data"); units below describe the
# untransformed assay quantity inside the log.
ENDPOINT_LABELS = {
    "HLM": "HLM CLint (log$_{10}$ mL/min/kg)",
    "RLM": "RLM CLint (log$_{10}$ mL/min/kg)",
    "MDR1": "MDR1 efflux ratio (log$_{10}$ ER)",
    "SOL": "Solubility, pH 6.8 (log$_{10}$ µg/mL)",
    "PPB_H": "PPB, human (log$_{10}$ % unbound)",
    "PPB_R": "PPB, rat (log$_{10}$ % unbound)",
}


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

        _, bins, _ = ax.hist(data, bins=40, density=False, alpha=0.6, color="steelblue", edgecolor="white")

        if len(data) > 1 and np.var(data) > 0:
            bin_width = bins[1] - bins[0]
            kde = gaussian_kde(data)
            x = np.linspace(data.min(), data.max(), 300)
            ax.plot(x, kde(x) * len(data) * bin_width, color="darkblue", linewidth=2)

        ax.set_title(ENDPOINT_LABELS.get(col, col), fontsize=10, pad=6)
        ax.set_xlabel("Value")
        ax.set_ylabel("Count")
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
