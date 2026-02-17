"""
Quantum key-recovery attack on the Even-Mansour cipher using Simon's algorithm.

The Even-Mansour cipher:
    E_{k1,k2}(x) = P(x XOR k1) XOR k2

where P is a publicly known permutation and k1, k2 are secret keys.

Attack (Kuwakado & Morii, 2010):
    Define f(x) = E_{k1,k2}(x) XOR P(x)
                = P(x XOR k1) XOR k2 XOR P(x)

    Then f(x) = f(x XOR k1) because:
        f(x XOR k1) = P(x XOR k1 XOR k1) XOR k2 XOR P(x XOR k1)
                     = P(x) XOR k2 XOR P(x XOR k1)
                     = P(x XOR k1) XOR k2 XOR P(x)  [XOR is commutative]
                     = f(x)

    So f satisfies Simon's promise with secret s = k1.
    After recovering k1, compute k2 = E(0) XOR P(k1) trivially.

Threat model:
    The attacker needs quantum superposition access to the cipher (Q2 model),
    i.e., the ability to query |x>|0> -> |x>|E(x)> in superposition.
"""

from __future__ import annotations

import secrets

import numpy as np
from qiskit import QuantumCircuit

from .simons_algorithm import run_simons_algorithm


class EvenMansourCipher:
    """A simple Even-Mansour cipher: E(x) = P(x XOR k1) XOR k2."""

    def __init__(
        self,
        n_bits: int,
        k1: int | None = None,
        k2: int | None = None,
        perm_seed: int = 42,
    ):
        """Initialize the cipher.

        Args:
            n_bits: Block size in bits (kept small for quantum simulation).
            k1: First key as an integer. Random if not provided.
            k2: Second key as an integer. Random if not provided.
            perm_seed: RNG seed for generating the public permutation.
        """
        self.n_bits = n_bits
        self.mask = (1 << n_bits) - 1
        N = 1 << n_bits

        self.k1 = (k1 if k1 is not None else secrets.randbelow(N)) & self.mask
        self.k2 = (k2 if k2 is not None else secrets.randbelow(N)) & self.mask

        # Generate a random permutation table for P.
        self._perm = list(range(N))
        rng = np.random.default_rng(perm_seed)
        rng.shuffle(self._perm)

        # Inverse permutation
        self._inv_perm = [0] * N
        for i, v in enumerate(self._perm):
            self._inv_perm[v] = i

    def permutation(self, x: int) -> int:
        """Public permutation P(x)."""
        return self._perm[x]

    def inv_permutation(self, y: int) -> int:
        """Inverse permutation P^{-1}(y)."""
        return self._inv_perm[y]

    def encrypt(self, plaintext: int) -> int:
        """Encrypt: E(x) = P(x XOR k1) XOR k2."""
        return self.permutation(plaintext ^ self.k1) ^ self.k2

    def decrypt(self, ciphertext: int) -> int:
        """Decrypt: D(c) = P^{-1}(c XOR k2) XOR k1."""
        return self.inv_permutation(ciphertext ^ self.k2) ^ self.k1


def build_even_mansour_attack_oracle(cipher: EvenMansourCipher) -> QuantumCircuit:
    """Build the quantum oracle for the Simon attack on Even-Mansour.

    The oracle computes f(x) = E(x) XOR P(x) into the output register.

    Args:
        cipher: The Even-Mansour cipher instance to attack.

    Returns:
        A 2n-qubit oracle circuit.
    """
    n = cipher.n_bits
    N = 1 << n

    truth_table = {}
    for x in range(N):
        truth_table[x] = cipher.encrypt(x) ^ cipher.permutation(x)

    return _truth_table_to_oracle(truth_table, n)


def _truth_table_to_oracle(truth_table: dict[int, int], n: int) -> QuantumCircuit:
    """Convert a truth table to a reversible quantum oracle.

    Builds U_f: |x>|y> -> |x>|y XOR f(x)> using multi-controlled X gates.

    In the circuit, qubit i represents bit i of the integer (LSB = qubit 0).
    """
    N = 1 << n
    qc = QuantumCircuit(2 * n)

    for out_bit in range(n):
        active_inputs = [x for x in range(N) if (truth_table[x] >> out_bit) & 1]
        if not active_inputs:
            continue

        target_qubit = n + out_bit
        for x in active_inputs:
            # Flip controls that need to be 0
            for bit in range(n):
                if not ((x >> bit) & 1):
                    qc.x(bit)

            qc.mcx(list(range(n)), target_qubit)

            # Uncompute flips
            for bit in range(n):
                if not ((x >> bit) & 1):
                    qc.x(bit)

    return qc


def attack_even_mansour(cipher: EvenMansourCipher) -> dict:
    """Execute the full Simon-based key recovery attack on Even-Mansour.

    Returns:
        Dictionary with recovered k1, k2 and whether the attack succeeded.
    """
    n = cipher.n_bits

    # Step 1: Build the attack oracle f(x) = E(x) XOR P(x)
    oracle = build_even_mansour_attack_oracle(cipher)

    # Step 2: Run Simon's algorithm to find s = k1
    recovered_k1_bits = run_simons_algorithm(oracle, n)
    recovered_k1_int = int(recovered_k1_bits, 2)

    # Step 3: Recover k2 = E(0) XOR P(k1)
    e_zero = cipher.encrypt(0)
    p_k1 = cipher.permutation(recovered_k1_int)
    recovered_k2_int = e_zero ^ p_k1

    # Verify: check that the recovered keys produce correct encryption
    success = all(
        cipher.encrypt(x) == cipher.permutation(x ^ recovered_k1_int) ^ recovered_k2_int
        for x in range(1 << n)
    )

    return {
        "recovered_k1": recovered_k1_int,
        "recovered_k2": recovered_k2_int,
        "actual_k1": cipher.k1,
        "actual_k2": cipher.k2,
        "k1_match": recovered_k1_int == cipher.k1,
        "k2_match": recovered_k2_int == cipher.k2,
        "functionally_equivalent": success,
        "n_bits": n,
    }
