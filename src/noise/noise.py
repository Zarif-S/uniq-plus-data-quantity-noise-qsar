"""Label noise injection for QSAR experiments (Landrum & Riniker taxonomy)."""

import numpy as np


def add_gaussian_noise(y, sigma_frac, random_state=None):
    """Add Gaussian noise: y_noisy = y + N(0, sigma_frac * std(y))."""
    rng = np.random.RandomState(random_state)
    sigma = sigma_frac * np.std(y)
    return y + rng.normal(0, sigma, size=len(y))


def add_systematic_bias(y, bias_frac, affected_frac=0.5, random_state=None):
    """Add constant bias to a random fraction of labels."""
    rng = np.random.RandomState(random_state)
    y_noisy = y.copy()
    bias = bias_frac * np.std(y)
    mask = rng.rand(len(y)) < affected_frac
    y_noisy[mask] += bias
    return y_noisy


def add_gross_errors(y, error_frac, random_state=None):
    """Replace error_frac of labels with uniform random from endpoint range."""
    rng = np.random.RandomState(random_state)
    y_noisy = y.copy()
    n_errors = max(1, int(error_frac * len(y)))
    idx = rng.choice(len(y), n_errors, replace=False)
    y_noisy[idx] = rng.uniform(y.min(), y.max(), size=n_errors)
    return y_noisy
