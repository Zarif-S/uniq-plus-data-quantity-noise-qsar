"""Sanity tests for src/noise."""

import numpy as np
import pytest
from src.noise import add_gaussian_noise, add_systematic_bias, add_gross_errors


@pytest.fixture
def y():
    return np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])


class TestGaussianNoise:
    def test_zero_sigma_returns_original(self, y):
        result = add_gaussian_noise(y, sigma_frac=0.0, random_state=42)
        np.testing.assert_array_equal(result, y)

    def test_nonzero_sigma_changes_values(self, y):
        result = add_gaussian_noise(y, sigma_frac=0.5, random_state=42)
        assert not np.allclose(result, y)

    def test_shape_preserved(self, y):
        result = add_gaussian_noise(y, sigma_frac=0.5, random_state=42)
        assert result.shape == y.shape

    def test_reproducible(self, y):
        r1 = add_gaussian_noise(y, sigma_frac=0.5, random_state=42)
        r2 = add_gaussian_noise(y, sigma_frac=0.5, random_state=42)
        np.testing.assert_array_equal(r1, r2)


class TestSystematicBias:
    def test_zero_bias_returns_original(self, y):
        result = add_systematic_bias(y, bias_frac=0.0, random_state=42)
        np.testing.assert_array_equal(result, y)

    def test_nonzero_bias_changes_some_values(self, y):
        result = add_systematic_bias(y, bias_frac=0.5, random_state=42)
        assert not np.allclose(result, y)

    def test_only_shifts_up(self, y):
        """Bias is always positive — affected values should increase or stay same."""
        result = add_systematic_bias(y, bias_frac=0.5, random_state=42)
        assert np.all(result >= y)

    def test_shape_preserved(self, y):
        result = add_systematic_bias(y, bias_frac=0.5, random_state=42)
        assert result.shape == y.shape


class TestGrossErrors:
    def test_zero_frac_changes_one_value(self, y):
        """error_frac=0 still replaces max(1, 0) = 1 label."""
        result = add_gross_errors(y, error_frac=0.0, random_state=42)
        n_changed = np.sum(result != y)
        assert n_changed >= 1

    def test_replaces_correct_count(self, y):
        result = add_gross_errors(y, error_frac=0.2, random_state=42)
        n_changed = np.sum(result != y)
        assert n_changed == 2  # 20% of 10

    def test_replacements_within_range(self, y):
        result = add_gross_errors(y, error_frac=0.5, random_state=42)
        assert np.all(result >= y.min())
        assert np.all(result <= y.max())

    def test_shape_preserved(self, y):
        result = add_gross_errors(y, error_frac=0.2, random_state=42)
        assert result.shape == y.shape
