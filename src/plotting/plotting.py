"""Reusable plotting utilities for UNIQ+ EDA and results."""

import math

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde


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
