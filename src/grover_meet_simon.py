"""
Grover-meet-Simon hybrid attack on the FX construction.

The FX construction (Kilian & Rogaway, 1996):
    E_{k_in, k_out}(x) = P_{k_in}(x XOR k_out) XOR k_out

where P_{k_in} is a block cipher keyed by an inner key k_in, and k_out
is an outer "whitening" key.  Security goal: 2n-bit total key (n each).

Classical: birthday bound O(2^{n/2}) queries + brute-force inner key.
Quantum (Simon only): If you fix k_out and treat the whole cipher as
Even-Mansour with key = k_out, Simon's recovers k_out, but only if
you can query the internal cipher P_{k_in} in superposition — which
you can't without knowing k_in.

Grover-meet-Simon hybrid (Leander & May, 2017):
    Grover-search over k_in candidates.  For each candidate, use Simon's
    on the outer key.  Total cost: O(sqrt(2^n) * n) = O(n * 2^{n/2}).
    This beats exhaustive key search on the 2n-bit keyspace (O(2^n)),
    proving FX is NOT secure against quantum adversaries with only
    n/2 + log(n) bits of security.

For simulation purposes we implement this on small n (3-4 bits)
where the Grover component is replaced by a classical loop, since
the asymptotic speedup is the point, not the Grover circuit itself.
"""

from __future__ import annotations

import secrets

import numpy as np
from qiskit import QuantumCircuit

from .even_mansour import _truth_table_to_oracle
from .simons_algorithm import run_simons_algorithm


class FXCipher:
    """FX construction: E(x) = P_{k_in}(x XOR k_out) XOR k_out.

    P_{k_in} is a keyed permutation (indexed by k_in).
    k_out is the outer whitening key.
    """

    def __init__(
        self,
        n_bits: int,
        k_inner: int | None = None,
        k_outer: int | None = None,
        perm_seed: int = 42,
    ):
        self.n_bits = n_bits
        self.mask = (1 << n_bits) - 1
        N = 1 << n_bits

        self.k_inner = (k_inner if k_inner is not None
                        else secrets.randbelow(N)) & self.mask
        self.k_outer = (k_outer if k_outer is not None
                        else secrets.randbelow(N)) & self.mask

        # Generate a family of independent permutations indexed by k_inner.
        # Each k_in value gets its own random permutation (models a PRP).
        rng = np.random.default_rng(perm_seed)
        self._perm_family: list[list[int]] = []
        for k in range(N):
            perm = list(range(N))
            # Use a distinct seed per key for independence
            key_rng = np.random.default_rng(perm_seed * (N + 1) + k)
            key_rng.shuffle(perm)
            self._perm_family.append(perm)

    def _keyed_perm(self, x: int, k_in: int) -> int:
        """P_{k_in}(x): independent permutation for each k_in."""
        return self._perm_family[k_in][x & self.mask]

    def encrypt(self, plaintext: int) -> int:
        """E(x) = P_{k_in}(x XOR k_out) XOR k_out."""
        inner_input = (plaintext ^ self.k_outer) & self.mask
        inner_output = self._keyed_perm(inner_input, self.k_inner)
        return (inner_output ^ self.k_outer) & self.mask

    def get_keyed_perm_table(self, k_in_guess: int) -> list[int]:
        """Get the truth table of P_{k_in_guess} (attacker can compute
        this for any candidate k_in)."""
        N = 1 << self.n_bits
        return [self._keyed_perm(x, k_in_guess) for x in range(N)]


def _build_simon_oracle_for_fx(
    cipher: FXCipher, k_in_guess: int
) -> QuantumCircuit:
    """Build Simon oracle f(x) = E(x) XOR P_{k_in_guess}(x).

    If k_in_guess == k_inner (correct guess), then:
        f(x) = P_{k_in}(x XOR k_out) XOR k_out XOR P_{k_in}(x)
    which has Simon period s = k_out (same as Even-Mansour argument).

    If k_in_guess is wrong, f won't have a clean period, and Simon's
    will return s = 0 or a random result that fails verification.
    """
    n = cipher.n_bits
    N = 1 << n

    truth_table = {}
    for x in range(N):
        e_x = cipher.encrypt(x)
        p_x = cipher._keyed_perm(x, k_in_guess)
        truth_table[x] = (e_x ^ p_x) & cipher.mask

    return _truth_table_to_oracle(truth_table, n)


def grover_meet_simon_attack(cipher: FXCipher) -> dict:
    """Execute the Grover-meet-Simon attack on the FX construction.

    For simulation, we iterate over all k_in candidates classically
    (simulating what Grover would do quantumly in O(sqrt(N)) steps).
    For each candidate, we run Simon's to attempt recovery of k_out.

    This demonstrates the algorithm structure; in a real quantum computer,
    the outer loop would be a Grover search achieving sqrt speedup.

    Returns:
        Dictionary with attack results.
    """
    n = cipher.n_bits
    N = 1 << n

    queries_total = 0

    for k_in_guess in range(N):
        # Simon's phase: O(n) quantum queries per guess
        oracle = _build_simon_oracle_for_fx(cipher, k_in_guess)
        recovered_k_out_bits = run_simons_algorithm(oracle, n)
        recovered_k_out = int(recovered_k_out_bits, 2)
        queries_total += n  # Approximate cost per Simon run

        # Verify: does this (k_in_guess, recovered_k_out) pair explain E?
        test_pt, test_ct = 0, cipher.encrypt(0)
        inner_input = (test_pt ^ recovered_k_out) & cipher.mask
        predicted_ct = (cipher._keyed_perm(inner_input, k_in_guess)
                        ^ recovered_k_out) & cipher.mask

        if predicted_ct == test_ct:
            # Double-check with a second plaintext
            test_pt2 = 1
            test_ct2 = cipher.encrypt(test_pt2)
            inner_input2 = (test_pt2 ^ recovered_k_out) & cipher.mask
            predicted_ct2 = (cipher._keyed_perm(inner_input2, k_in_guess)
                             ^ recovered_k_out) & cipher.mask

            if predicted_ct2 == test_ct2:
                return {
                    "recovered_k_inner": k_in_guess,
                    "recovered_k_outer": recovered_k_out,
                    "actual_k_inner": cipher.k_inner,
                    "actual_k_outer": cipher.k_outer,
                    "k_inner_match": k_in_guess == cipher.k_inner,
                    "k_outer_match": recovered_k_out == cipher.k_outer,
                    "success": True,
                    "queries": queries_total,
                    "n_bits": n,
                    "classical_cost": f"O(2^{2*n}) brute force",
                    "quantum_cost": f"O(n * 2^{n//2}) Grover-meet-Simon",
                }

    return {
        "success": False,
        "queries": queries_total,
        "n_bits": n,
        "actual_k_inner": cipher.k_inner,
        "actual_k_outer": cipher.k_outer,
    }
