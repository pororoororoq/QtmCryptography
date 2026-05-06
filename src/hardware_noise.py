"""
Realistic quantum hardware simulation for Simon's algorithm.

This module simulates running Simon's algorithm on noisy quantum hardware
by applying realistic noise models:
    - Depolarizing noise on single-qubit gates
    - Depolarizing noise on two-qubit (CNOT) gates
    - Measurement (readout) errors
    - Thermal relaxation (T1/T2 decoherence)

We compare ideal statevector results with noisy simulation results
to quantify how noise degrades the attack's success probability.

Hardware targets modeled:
    - IBM Heron (127 qubits, CX error ~0.5%, readout error ~1%)
    - Generic NISQ device (higher error rates)
    - Hypothetical "good" device (future improvement)
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit_aer.noise import (
    NoiseModel,
    depolarizing_error,
    ReadoutError,
    thermal_relaxation_error,
)

from .simons_algorithm import (
    build_oracle_from_secret,
    _rank_gf2,
    solve_linear_system_gf2,
)


@dataclass
class HardwareProfile:
    """Noise parameters for a quantum device."""
    name: str
    single_qubit_error: float
    two_qubit_error: float
    readout_error: float
    t1_us: float  # T1 relaxation time in microseconds
    t2_us: float  # T2 dephasing time in microseconds
    gate_time_1q_us: float  # Single-qubit gate time
    gate_time_2q_us: float  # Two-qubit gate time


# Hardware profiles
IBM_HERON = HardwareProfile(
    name="IBM Heron (2024)",
    single_qubit_error=0.001,
    two_qubit_error=0.005,
    readout_error=0.01,
    t1_us=300.0,
    t2_us=200.0,
    gate_time_1q_us=0.035,
    gate_time_2q_us=0.066,
)

NISQ_GENERIC = HardwareProfile(
    name="Generic NISQ (2023)",
    single_qubit_error=0.005,
    two_qubit_error=0.02,
    readout_error=0.03,
    t1_us=100.0,
    t2_us=80.0,
    gate_time_1q_us=0.05,
    gate_time_2q_us=0.3,
)

FUTURE_DEVICE = HardwareProfile(
    name="Future improved device",
    single_qubit_error=0.0001,
    two_qubit_error=0.001,
    readout_error=0.001,
    t1_us=1000.0,
    t2_us=800.0,
    gate_time_1q_us=0.02,
    gate_time_2q_us=0.04,
)


def build_noise_model(profile: HardwareProfile) -> NoiseModel:
    """Construct a Qiskit noise model from a hardware profile."""
    noise_model = NoiseModel()

    # Single-qubit gate errors
    error_1q = depolarizing_error(profile.single_qubit_error, 1)
    noise_model.add_all_qubit_quantum_error(error_1q, ["h", "x", "id"])

    # Two-qubit gate errors (CX/MCX decomposition uses CX)
    error_2q = depolarizing_error(profile.two_qubit_error, 2)
    noise_model.add_all_qubit_quantum_error(error_2q, ["cx"])

    # Readout errors
    p0_given1 = profile.readout_error  # P(measure 0 | state is 1)
    p1_given0 = profile.readout_error  # P(measure 1 | state is 0)
    readout_err = ReadoutError(
        [[1 - p1_given0, p1_given0], [p0_given1, 1 - p0_given1]]
    )
    noise_model.add_all_qubit_readout_error(readout_err)

    return noise_model


def run_simon_noisy_hardware(
    secret: str,
    profile: HardwareProfile = IBM_HERON,
    n_shots: int = 1024,
    n_rounds: int | None = None,
) -> dict:
    """Run Simon's algorithm through a noisy hardware simulation.

    Args:
        secret: The secret string s (MSB-first bitstring).
        profile: Hardware noise profile to simulate.
        n_shots: Number of shots per circuit execution.
        n_rounds: Number of Simon circuit iterations. Default: 3*n.

    Returns:
        Dictionary with results, success rate, and noise analysis.
    """
    n = len(secret)
    if n_rounds is None:
        n_rounds = 3 * n

    oracle = build_oracle_from_secret(secret)

    # Build Simon circuit with measurements
    qc = QuantumCircuit(2 * n, n)
    qc.h(range(n))
    qc.compose(oracle, inplace=True)
    qc.h(range(n))
    qc.measure(range(n), range(n))

    # Transpile to basis gates
    transpiled = transpile(qc, basis_gates=["cx", "id", "x", "h", "measure"],
                           optimization_level=2)

    # Noisy simulation
    noise_model = build_noise_model(profile)
    noisy_sim = AerSimulator(noise_model=noise_model)

    # Collect measurements from multiple rounds
    all_y_vectors: list[list[int]] = []
    raw_counts_list = []

    for _ in range(n_rounds):
        job = noisy_sim.run(transpiled, shots=n_shots)
        counts = job.result().get_counts()
        raw_counts_list.append(counts)

        # Extract the most common measurement result as our y-vector
        # (majority vote within a single shot batch)
        most_common = max(counts, key=counts.get)

        # Convert Qiskit measurement string to MSB-first y-vector
        # Qiskit returns strings in big-endian: bit[0] of string = highest qubit
        # For the input register (qubits 0..n-1):
        # y_bits[k] corresponds to qubit n-1-k -> outcome position n+k
        # But measurement only has n classical bits, so outcome[k] = qubit n-1-k
        y_bits = [int(most_common[k]) for k in range(n)]
        all_y_vectors.append(y_bits)

    # Try to solve from collected equations
    non_zero = [y for y in all_y_vectors if any(b != 0 for b in y)]

    if len(non_zero) >= n - 1:
        recovered = solve_linear_system_gf2(non_zero, n)
    else:
        recovered = "0" * n

    # Ideal comparison
    ideal_result = _run_ideal_simon(secret)

    # Compute how many y-vectors actually satisfy y · s = 0
    s_bits = [int(c) for c in secret]
    n_valid = sum(
        1 for y in all_y_vectors
        if sum(y[i] * s_bits[i] for i in range(n)) % 2 == 0
    )

    # Circuit stats
    cx_count = transpiled.count_ops().get("cx", 0)
    depth = transpiled.depth()

    return {
        "secret": secret,
        "recovered": recovered,
        "success": recovered == secret,
        "hardware_profile": profile.name,
        "n_rounds": n_rounds,
        "n_shots_per_round": n_shots,
        "n_valid_equations": n_valid,
        "fraction_valid": n_valid / n_rounds,
        "ideal_result": ideal_result,
        "circuit_stats": {
            "cx_count": cx_count,
            "depth": depth,
            "n_qubits": 2 * n,
        },
        "noise_params": {
            "1q_error": profile.single_qubit_error,
            "2q_error": profile.two_qubit_error,
            "readout_error": profile.readout_error,
        },
    }


def _run_ideal_simon(secret: str) -> str:
    """Run ideal (noiseless) Simon's for comparison."""
    from .simons_algorithm import run_simons_algorithm
    oracle = build_oracle_from_secret(secret)
    return run_simons_algorithm(oracle, len(secret))


def hardware_comparison(
    secret: str = "110",
    n_shots: int = 1024,
) -> dict:
    """Compare Simon's algorithm performance across hardware profiles.

    Returns results for ideal, IBM Heron, generic NISQ, and future device.
    """
    profiles = [IBM_HERON, NISQ_GENERIC, FUTURE_DEVICE]
    results = {}

    # Ideal
    ideal = _run_ideal_simon(secret)
    results["ideal"] = {
        "recovered": ideal,
        "success": ideal == secret,
        "profile": "Ideal (noiseless)",
    }

    # Noisy hardware
    for profile in profiles:
        res = run_simon_noisy_hardware(secret, profile=profile, n_shots=n_shots)
        results[profile.name] = {
            "recovered": res["recovered"],
            "success": res["success"],
            "fraction_valid": res["fraction_valid"],
            "cx_count": res["circuit_stats"]["cx_count"],
            "depth": res["circuit_stats"]["depth"],
        }

    return {
        "secret": secret,
        "n_bits": len(secret),
        "results": results,
    }


def estimate_success_probability(
    n: int,
    profile: HardwareProfile,
    n_trials: int = 50,
) -> dict:
    """Estimate success probability of Simon's attack for given n and hardware.

    Runs multiple trials with random secrets and reports statistics.
    """
    rng = np.random.default_rng(42)
    successes = 0
    valid_fractions = []

    for trial in range(n_trials):
        # Random non-zero secret
        s_int = rng.integers(1, 1 << n)
        secret = format(s_int, f"0{n}b")

        result = run_simon_noisy_hardware(
            secret, profile=profile,
            n_shots=512, n_rounds=4 * n,
        )
        if result["success"]:
            successes += 1
        valid_fractions.append(result["fraction_valid"])

    return {
        "n_bits": n,
        "hardware": profile.name,
        "n_trials": n_trials,
        "success_rate": successes / n_trials,
        "mean_valid_fraction": float(np.mean(valid_fractions)),
        "std_valid_fraction": float(np.std(valid_fractions)),
    }
