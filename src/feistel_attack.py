"""
Quantum attack on 3-round Feistel networks using Simon's algorithm.

A 3-round Feistel network with round function F and input (L, R):

    Round 1: L1 = R,    R1 = L XOR F(R)
    Round 2: L2 = R1,   R2 = L1 XOR F(R1)
    Round 3: L3 = R2,   R3 = L2 XOR F(R2)

    Ciphertext = (L3, R3)

Attack (Kuwakado & Morii, 2010):
    For a 3-round Feistel with keyed round function F(x) = S[x XOR k]:

    Define f(x) = E_L(x, 0) XOR E_L(x, 1) where E_L is the left half
    of the ciphertext and the second argument is the initial right half.

    Working through the rounds:
        E_L(x, c) = c XOR S[(x XOR S[c XOR k]) XOR k]

    Let a = S[k] XOR k and b = S[1 XOR k] XOR k. Then:
        f(x) = S[x XOR a] XOR S[x XOR b] XOR 1

    The XOR 1 is a constant that doesn't affect the period.
    f satisfies Simon's promise with period s = a XOR b = S[k] XOR S[1 XOR k].

    After recovering s, brute-force k from the candidates satisfying
    S[k] XOR S[1 XOR k] = s (much smaller set than 2^n).
"""

from __future__ import annotations

import secrets

import numpy as np
from qiskit import QuantumCircuit

from .even_mansour import _truth_table_to_oracle
from .simons_algorithm import run_simons_algorithm


class Feistel3RoundNonlinear:
    """3-round Feistel with nonlinear keyed round functions for Simon attack.

    Round function: F(x) = S[x XOR k] where S is a public S-box (permutation).
    """

    def __init__(self, half_bits: int, key: int | None = None, seed: int = 42):
        self.half_bits = half_bits
        self.mask = (1 << half_bits) - 1
        N = 1 << half_bits

        if key is None:
            self.key = secrets.randbelow(N)
        else:
            self.key = key & self.mask

        # Public S-box (nonlinear permutation)
        rng = np.random.default_rng(seed)
        self.sbox = list(range(N))
        rng.shuffle(self.sbox)

    def round_func(self, x: int) -> int:
        return self.sbox[(x ^ self.key) & self.mask]

    def encrypt(self, left: int, right: int) -> tuple[int, int]:
        l, r = left & self.mask, right & self.mask
        for _ in range(3):
            new_r = l ^ self.round_func(r)
            l = r
            r = new_r & self.mask
        return l, r


def build_feistel_attack_oracle(cipher: Feistel3RoundNonlinear) -> QuantumCircuit:
    """Build the Simon oracle for attacking a 3-round nonlinear Feistel.

    Constructs f(x) = E_L(x, 0) XOR E_L(x, 1), which has Simon period
    s = S[k] XOR S[1 XOR k].
    """
    n = cipher.half_bits
    N = 1 << n

    truth_table = {}
    for x in range(N):
        cl0, _ = cipher.encrypt(x, 0)
        cl1, _ = cipher.encrypt(x, 1)
        truth_table[x] = cl0 ^ cl1

    return _truth_table_to_oracle(truth_table, n)


def attack_feistel_3round(cipher: Feistel3RoundNonlinear) -> dict:
    """Execute Simon's attack on a 3-round nonlinear Feistel network.

    Steps:
        1. Recover Simon period s = S[k] XOR S[1 XOR k].
        2. Find all key candidates k' satisfying S[k'] XOR S[1 XOR k'] = s.
        3. Verify each candidate against a known plaintext-ciphertext pair.

    Returns:
        Dictionary with attack results.
    """
    n = cipher.half_bits
    N = 1 << n

    # Step 1: Build oracle and run Simon's algorithm
    oracle = build_feistel_attack_oracle(cipher)
    recovered_period = run_simons_algorithm(oracle, n)
    s = int(recovered_period, 2)

    # Step 2: Find key candidates where S[k'] XOR S[1 XOR k'] = s
    candidates = []
    for k_guess in range(N):
        expected_s = cipher.sbox[k_guess] ^ cipher.sbox[(1 ^ k_guess) & cipher.mask]
        if (expected_s & cipher.mask) == s:
            candidates.append(k_guess)

    # Step 3: Verify candidates with a known plaintext-ciphertext pair
    recovered_key = None
    test_l, test_r = 0, 0
    expected_cl, expected_cr = cipher.encrypt(test_l, test_r)

    for k_cand in candidates:
        test_cipher = Feistel3RoundNonlinear(n, key=k_cand, seed=42)
        cl, cr = test_cipher.encrypt(test_l, test_r)
        if cl == expected_cl and cr == expected_cr:
            recovered_key = k_cand
            break

    return {
        "simon_period": s,
        "n_candidates": len(candidates),
        "recovered_key": recovered_key,
        "actual_key": cipher.key,
        "success": recovered_key == cipher.key,
        "n_bits": n,
    }
