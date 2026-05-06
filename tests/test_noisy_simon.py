"""Tests for Simon's algorithm with noise (error-tolerant variant)."""

import pytest
from src.noisy_simon import (
    run_noisy_simons_algorithm,
    run_noisy_vs_clean_comparison,
    _inject_noise,
    _majority_vote_recovery,
)
from src.simons_algorithm import build_oracle_from_secret
import numpy as np


class TestNoiseInjection:
    def test_no_noise_preserves_vector(self):
        """With epsilon=0, vector should be unchanged."""
        rng = np.random.default_rng(42)
        y = [1, 0, 1]
        s = [1, 1, 0]
        result = _inject_noise(y, s, 0.0, rng)
        assert result == y

    def test_full_noise_always_flips(self):
        """With epsilon=1, vector dot product parity should flip."""
        rng = np.random.default_rng(42)
        # Use a vector that satisfies y·s = 0 (as Simon's would produce)
        y = [1, 1, 1]  # y·s = 1*1 + 1*1 + 1*0 = 0 mod 2
        s = [1, 1, 0]
        result = _inject_noise(y, s, 1.0, rng)
        dot = sum(result[i] * s[i] for i in range(3)) % 2
        assert dot == 1

    def test_noise_with_zero_secret(self):
        """With s=0, noise injection should not modify vector."""
        rng = np.random.default_rng(42)
        y = [1, 0, 1]
        s = [0, 0, 0]
        result = _inject_noise(y, s, 1.0, rng)
        assert result == y


class TestNoisySimon:
    def test_low_noise_recovers_secret(self):
        """With low noise (5%), should still recover the secret."""
        secret = "110"
        oracle = build_oracle_from_secret(secret)
        result = run_noisy_simons_algorithm(
            oracle, n=3, epsilon=0.05,
            secret_for_noise=secret, seed=42,
        )
        assert result["recovered_s"] == secret

    def test_moderate_noise_recovers_secret(self):
        """With moderate noise (15%), should still recover with enough samples."""
        secret = "110"
        oracle = build_oracle_from_secret(secret)
        result = run_noisy_simons_algorithm(
            oracle, n=3, epsilon=0.15,
            n_samples=60,
            secret_for_noise=secret, seed=42,
        )
        assert result["recovered_s"] == secret

    def test_reports_error_statistics(self):
        """Should report correct noise statistics."""
        secret = "110"
        oracle = build_oracle_from_secret(secret)
        result = run_noisy_simons_algorithm(
            oracle, n=3, epsilon=0.2,
            n_samples=100,
            secret_for_noise=secret, seed=42,
        )
        assert result["n_samples"] == 100
        assert result["epsilon"] == 0.2
        assert result["n_correct_samples"] is not None
        # Empirical error should be roughly close to epsilon
        assert result["empirical_error_rate"] < 0.4

    def test_no_noise_injection_mode(self):
        """Without secret_for_noise, should run clean."""
        secret = "101"
        oracle = build_oracle_from_secret(secret)
        result = run_noisy_simons_algorithm(
            oracle, n=3, epsilon=0.1,
            secret_for_noise=None, seed=42,
        )
        # Without noise injection, should recover perfectly
        assert result["recovered_s"] == secret
        assert result["n_correct_samples"] is None


class TestNoisyVsClean:
    def test_comparison_runs(self):
        """Comparison function should complete and return valid results."""
        result = run_noisy_vs_clean_comparison(
            n=3, secret="110", epsilon=0.1, n_trials=5
        )
        assert result["clean_success_rate"] >= 0.0
        assert result["noisy_success_rate"] >= 0.0
        assert result["n_trials"] == 5
        assert result["epsilon"] == 0.1
