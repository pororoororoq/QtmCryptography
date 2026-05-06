"""
Simon's algorithm with noise (error-tolerant variant).

In real quantum hardware, gates are imperfect and decoherence occurs.
This means the measurement outcomes y from Simon's circuit may NOT
exactly satisfy y · s = 0 — some fraction will have y · s = 1 instead.

Error model:
    With probability (1 - epsilon), y · s = 0 (correct).
    With probability epsilon, y · s = 1 (error).

Error-tolerant recovery (Kaplan et al., 2016):
    Instead of requiring all equations to hold exactly, use majority
    vote on each candidate solution.  Collect M >> n samples and use
    statistical post-processing to recover s despite noise.

Approach:
    1. Collect many y-vectors (even noisy ones).
    2. For each possible s (in the null space of the "clean" subspace),
       count how many y satisfy y · s = 0.
    3. The true s will have the highest count (close to M * (1-epsilon)).

For our simulation we inject noise directly into the measurement results
to model realistic quantum hardware without requiring an actual noise
model on the gates (which would make simulation exponentially expensive).
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit

from .simons_algorithm import (
    _sample_y_bits,
    _rank_gf2,
    solve_linear_system_gf2,
    build_oracle_from_secret,
)


def _inject_noise(y_bits: list[int], s_bits: list[int], epsilon: float,
                  rng: np.random.Generator) -> list[int]:
    """Simulate noisy measurement: with probability epsilon, flip one bit
    so that y · s != 0.

    Rather than flipping random bits, we flip a single bit at a position
    where s has a 1, which guarantees the dot product changes parity.
    """
    n = len(y_bits)
    if rng.random() >= epsilon:
        return y_bits  # No error

    # Find positions where s has a 1
    s_positions = [i for i in range(n) if s_bits[i] == 1]
    if not s_positions:
        return y_bits  # s = 0, no meaningful noise to inject

    # Flip one bit at an s-position to violate y · s = 0
    y_noisy = y_bits.copy()
    flip_pos = rng.choice(s_positions)
    y_noisy[flip_pos] ^= 1
    return y_noisy


def run_noisy_simons_algorithm(
    oracle: QuantumCircuit,
    n: int,
    epsilon: float = 0.1,
    n_samples: int | None = None,
    secret_for_noise: str | None = None,
    seed: int = 123,
) -> dict:
    """Run Simon's algorithm with injected noise and error-tolerant recovery.

    Args:
        oracle: The 2n-qubit oracle circuit.
        n: Number of input bits.
        epsilon: Error rate (probability that y · s != 0).
        n_samples: Number of measurement samples to collect.
                   Default: 5*n for epsilon <= 0.1, scales up for worse noise.
        secret_for_noise: The actual secret (for noise injection simulation).
                          If None, we run without noise injection (just collecting).
        seed: RNG seed for reproducibility.

    Returns:
        Dictionary with recovered secret, statistics, and success info.
    """
    rng = np.random.default_rng(seed)

    if n_samples is None:
        # Need more samples with higher noise
        n_samples = max(5 * n, int(n / (1 - 2 * epsilon) ** 2)) if epsilon < 0.5 else 20 * n

    s_bits = ([int(c) for c in secret_for_noise]
              if secret_for_noise else None)

    # Phase 1: Collect noisy y-vectors
    all_y_vectors: list[list[int]] = []
    for _ in range(n_samples):
        y_bits = _sample_y_bits(oracle, n)
        if s_bits is not None:
            y_bits = _inject_noise(y_bits, s_bits, epsilon, rng)
        all_y_vectors.append(y_bits)

    # Phase 2: Majority-vote recovery
    # Method: find the best s using the clean GF(2) system from the
    # "mostly correct" equations, then verify with voting.
    recovered_s = _majority_vote_recovery(all_y_vectors, n, epsilon)

    # Statistics
    if s_bits is not None:
        n_correct = sum(
            1 for y in all_y_vectors
            if sum(y[i] * s_bits[i] for i in range(n)) % 2 == 0
        )
    else:
        n_correct = None

    return {
        "recovered_s": recovered_s,
        "n_samples": len(all_y_vectors),
        "epsilon": epsilon,
        "n_correct_samples": n_correct,
        "empirical_error_rate": (1 - n_correct / len(all_y_vectors))
                                 if n_correct else None,
        "n_bits": n,
    }


def _majority_vote_recovery(
    y_vectors: list[list[int]], n: int, epsilon: float
) -> str:
    """Recover s from noisy y-vectors using majority-vote decoding.

    Strategy:
        1. Try multiple random subsets of n-1 equations.
        2. For each subset, solve for a candidate s.
        3. Vote: the candidate with the most y satisfying y · s = 0 wins.
        4. s="0...0" trivially scores M, so we track the best NON-ZERO
           candidate separately and return it if its score is above chance.
    """
    if not y_vectors:
        return "0" * n

    M = len(y_vectors)
    best_nonzero_s = None
    best_nonzero_score = 0

    rng = np.random.default_rng(42)
    n_trials = min(50, M)

    candidates_seen: set[str] = set()

    for trial in range(n_trials):
        subset_size = min(2 * n, M)
        indices = rng.choice(M, size=subset_size, replace=False)
        subset = [y_vectors[i] for i in indices]

        non_zero = [y for y in subset if any(b != 0 for b in y)]
        if len(non_zero) < n - 1:
            continue

        equations = non_zero[:n + 2]
        candidate = solve_linear_system_gf2(equations, n)

        if candidate in candidates_seen:
            continue
        candidates_seen.add(candidate)

        if candidate == "0" * n:
            continue  # Skip trivial — it always scores M

        s_bits = [int(c) for c in candidate]
        score = sum(
            1 for y in y_vectors
            if sum(y[i] * s_bits[i] for i in range(n)) % 2 == 0
        )

        if score > best_nonzero_score:
            best_nonzero_score = score
            best_nonzero_s = candidate

    # Decision: a non-zero candidate is valid if its score is significantly
    # above chance (M/2).  Expected for true s: M*(1-epsilon).
    # Random s would score ~M/2.  Threshold: midpoint.
    chance_score = M / 2
    threshold = (M * (1 - epsilon) + chance_score) / 2  # Midpoint

    if best_nonzero_s is not None and best_nonzero_score > threshold:
        return best_nonzero_s

    return "0" * n


def run_noisy_vs_clean_comparison(
    n: int = 4,
    secret: str | None = None,
    epsilon: float = 0.15,
    n_trials: int = 20,
) -> dict:
    """Compare success rates of clean vs noisy Simon's.

    Runs both clean and noisy versions multiple times and reports
    success rates, demonstrating noise tolerance.
    """
    if secret is None:
        # Generate a random non-zero secret
        rng = np.random.default_rng(99)
        s_int = rng.integers(1, 1 << n)
        secret = format(s_int, f"0{n}b")

    oracle = build_oracle_from_secret(secret)

    clean_successes = 0
    noisy_successes = 0

    for trial in range(n_trials):
        # Clean run
        from .simons_algorithm import run_simons_algorithm
        clean_result = run_simons_algorithm(oracle, n)
        if clean_result == secret:
            clean_successes += 1

        # Noisy run
        noisy_result = run_noisy_simons_algorithm(
            oracle, n,
            epsilon=epsilon,
            secret_for_noise=secret,
            seed=trial * 7,
        )
        if noisy_result["recovered_s"] == secret:
            noisy_successes += 1

    return {
        "secret": secret,
        "n_bits": n,
        "epsilon": epsilon,
        "n_trials": n_trials,
        "clean_success_rate": clean_successes / n_trials,
        "noisy_success_rate": noisy_successes / n_trials,
    }
