"""Tests for hardware noise simulation."""

import pytest
from src.hardware_noise import (
    HardwareProfile,
    IBM_HERON,
    NISQ_GENERIC,
    FUTURE_DEVICE,
    build_noise_model,
    run_simon_noisy_hardware,
    hardware_comparison,
)


class TestHardwareProfiles:
    def test_profiles_have_valid_parameters(self):
        """All profiles should have positive error rates."""
        for profile in [IBM_HERON, NISQ_GENERIC, FUTURE_DEVICE]:
            assert profile.single_qubit_error > 0
            assert profile.two_qubit_error > 0
            assert profile.readout_error > 0
            assert profile.t1_us > 0
            assert profile.t2_us > 0

    def test_future_better_than_current(self):
        """Future device should have lower error rates."""
        assert FUTURE_DEVICE.single_qubit_error < IBM_HERON.single_qubit_error
        assert FUTURE_DEVICE.two_qubit_error < IBM_HERON.two_qubit_error


class TestNoiseModel:
    def test_builds_without_error(self):
        """Noise model should build successfully from any profile."""
        for profile in [IBM_HERON, NISQ_GENERIC, FUTURE_DEVICE]:
            model = build_noise_model(profile)
            assert model is not None


class TestNoisySimon:
    def test_ideal_device_succeeds(self):
        """With very low noise (future device), should mostly succeed."""
        result = run_simon_noisy_hardware(
            "110", profile=FUTURE_DEVICE,
            n_shots=2048, n_rounds=12,
        )
        assert result["secret"] == "110"
        assert result["circuit_stats"]["n_qubits"] == 6

    def test_reports_circuit_stats(self):
        """Should report circuit statistics."""
        result = run_simon_noisy_hardware(
            "101", profile=IBM_HERON,
            n_shots=512, n_rounds=9,
        )
        assert "cx_count" in result["circuit_stats"]
        assert "depth" in result["circuit_stats"]
        assert result["n_rounds"] == 9

    def test_fraction_valid_reasonable(self):
        """Fraction of valid equations should be between 0 and 1."""
        result = run_simon_noisy_hardware(
            "110", profile=NISQ_GENERIC,
            n_shots=1024, n_rounds=9,
        )
        assert 0.0 <= result["fraction_valid"] <= 1.0


class TestHardwareComparison:
    def test_comparison_runs(self):
        """Hardware comparison should complete."""
        result = hardware_comparison(secret="10", n_shots=256)
        assert "ideal" in result["results"]
        assert result["results"]["ideal"]["success"]
        assert result["n_bits"] == 2
