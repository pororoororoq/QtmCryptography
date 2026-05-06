"""
Quantum attack on PRINCE-like ciphers (real-world FX construction).

PRINCE (Borghoff et al., 2012) is a lightweight block cipher designed for
low-latency applications.  Its structure is:

    PRINCE_{k0, k1}(x) = k0 XOR PRINCE_core_{k1}(x XOR k0)

This is exactly the FX construction!  The outer key k0 whitens the
input and output, while the inner key k1 parameterizes the core cipher.

For our attack, we implement a simplified PRINCE-like cipher that
preserves the FX structure while being small enough to simulate quantumly.

The cipher we implement:
    - Block size: n bits (configurable, 4 for simulation)
    - Core cipher: substitution-permutation network keyed by k1
    - Outer key k0: whitening (XOR before and after)
    - Structure: E(x) = k0 XOR Core_{k1}(x XOR k0)

Simon's attack on this structure:
    Define f(x) = E(x) XOR Core_{k1_guess}(x)
    If k1_guess is correct:
        f(x) = k0 XOR Core_{k1}(x XOR k0) XOR Core_{k1}(x)
    This has Simon period s = k0 (same as Even-Mansour argument).

This demonstrates that PRINCE-class ciphers with their FX structure
are vulnerable to quantum key recovery in O(n * 2^{n/2}) time via
the Grover-meet-Simon approach, compared to O(2^{2n}) classically.
"""

from __future__ import annotations

import secrets

import numpy as np
from qiskit import QuantumCircuit

from .even_mansour import _truth_table_to_oracle
from .simons_algorithm import run_simons_algorithm


class PRINCELikeCipher:
    """A PRINCE-like cipher with FX construction.

    Structure:
        E_{k0, k1}(x) = k0' XOR Core_{k1}(x XOR k0)

    where k0' = k0 XOR (k0 >>> 1) XOR (k0 >> (n-1))
    (the "alpha reflection" of PRINCE — simplified here to k0' = k0 ^ alpha).

    The core cipher is a 3-round SPN:
        Round i: SubBytes -> ShiftBits -> AddRoundKey(k1 XOR rc_i)
    """

    def __init__(
        self,
        n_bits: int = 4,
        k0: int | None = None,
        k1: int | None = None,
        seed: int = 42,
    ):
        self.n_bits = n_bits
        self.mask = (1 << n_bits) - 1
        N = 1 << n_bits

        self.k0 = (k0 if k0 is not None else secrets.randbelow(N)) & self.mask
        self.k1 = (k1 if k1 is not None else secrets.randbelow(N)) & self.mask

        # PRINCE uses k0' = k0 >>> 1 XOR (k0 >> 63) XOR k0
        # Simplified for small n: k0' = k0 XOR alpha
        self.alpha = 0b1010 & self.mask  # Fixed constant (like PRINCE's alpha)
        self.k0_prime = (self.k0 ^ self.alpha) & self.mask

        # S-box (4-bit PRINCE S-box for n=4, random for other sizes)
        rng = np.random.default_rng(seed)
        if n_bits == 4:
            # Actual PRINCE 4-bit S-box
            self.sbox = [0xB, 0xF, 0x3, 0x2, 0xA, 0xC, 0x9, 0x1,
                         0x6, 0x7, 0x8, 0x0, 0xE, 0x5, 0xD, 0x4]
            # Inverse S-box
            self.inv_sbox = [0] * 16
            for i, v in enumerate(self.sbox):
                self.inv_sbox[v] = i
        else:
            self.sbox = list(range(N))
            rng.shuffle(self.sbox)
            self.inv_sbox = [0] * N
            for i, v in enumerate(self.sbox):
                self.inv_sbox[v] = i

        # Round constants (simplified)
        self.round_constants = [
            rng.integers(0, N) & self.mask for _ in range(6)
        ]

    def _sub_bytes(self, x: int) -> int:
        """Apply S-box substitution."""
        return self.sbox[x & self.mask]

    def _inv_sub_bytes(self, x: int) -> int:
        """Apply inverse S-box."""
        return self.inv_sbox[x & self.mask]

    def _shift_bits(self, x: int) -> int:
        """Bit permutation layer (simplified rotation)."""
        n = self.n_bits
        return ((x << 1) | (x >> (n - 1))) & self.mask

    def _inv_shift_bits(self, x: int) -> int:
        """Inverse bit permutation."""
        n = self.n_bits
        return ((x >> 1) | (x << (n - 1))) & self.mask

    def core_encrypt(self, x: int, key: int | None = None) -> int:
        """PRINCE core cipher: 3-round SPN keyed by k1.

        Can be called with an arbitrary key (for the attack).
        """
        k = key if key is not None else self.k1
        state = x & self.mask

        # Forward rounds
        for rnd in range(3):
            state = self._sub_bytes(state)
            state = self._shift_bits(state)
            state = (state ^ k ^ self.round_constants[rnd]) & self.mask

        return state

    def core_decrypt(self, y: int, key: int | None = None) -> int:
        """Inverse of core cipher."""
        k = key if key is not None else self.k1
        state = y & self.mask

        for rnd in range(2, -1, -1):
            state = (state ^ k ^ self.round_constants[rnd]) & self.mask
            state = self._inv_shift_bits(state)
            state = self._inv_sub_bytes(state)

        return state

    def encrypt(self, plaintext: int) -> int:
        """Full PRINCE-like encryption: E(x) = k0' XOR Core_{k1}(x XOR k0)."""
        whitened = (plaintext ^ self.k0) & self.mask
        core_out = self.core_encrypt(whitened)
        return (core_out ^ self.k0_prime) & self.mask

    def decrypt(self, ciphertext: int) -> int:
        """Full decryption."""
        de_whitened = (ciphertext ^ self.k0_prime) & self.mask
        core_out = self.core_decrypt(de_whitened)
        return (core_out ^ self.k0) & self.mask


def build_prince_attack_oracle(
    cipher: PRINCELikeCipher,
    k1_guess: int,
) -> QuantumCircuit:
    """Build Simon oracle for PRINCE attack given a k1 guess.

    f(x) = E(x) XOR Core_{k1_guess}(x)

    If k1_guess == k1 (correct):
        f(x) = k0' XOR Core_{k1}(x XOR k0) XOR Core_{k1}(x)
        f(x XOR k0) = k0' XOR Core_{k1}(x) XOR Core_{k1}(x XOR k0)
                     = k0' XOR Core_{k1}(x XOR k0) XOR Core_{k1}(x)   [oops, not quite]

    Actually for the standard Even-Mansour argument:
        f(x) = E(x) XOR Core_{k1}(x)
             = Core_{k1}(x XOR k0) XOR k0' XOR Core_{k1}(x)

        f(x XOR k0) = Core_{k1}(x) XOR k0' XOR Core_{k1}(x XOR k0)
                    = f(x)   [XOR is commutative!]

    So period s = k0. Simon's recovers k0.
    """
    n = cipher.n_bits
    N = 1 << n

    truth_table = {}
    for x in range(N):
        e_x = cipher.encrypt(x)
        core_x = cipher.core_encrypt(x, key=k1_guess)
        truth_table[x] = (e_x ^ core_x) & cipher.mask

    return _truth_table_to_oracle(truth_table, n)


def attack_prince_cipher(cipher: PRINCELikeCipher) -> dict:
    """Full quantum attack on the PRINCE-like cipher.

    Strategy (Grover-meet-Simon):
        For each k1 candidate:
            1. Build Simon oracle f(x) = E(x) XOR Core_{k1_guess}(x)
            2. Run Simon's to recover k0 candidate
            3. Verify with known plaintext-ciphertext pair

    For simulation we iterate classically over k1 candidates.
    On a real quantum computer, Grover would search over k1 in O(sqrt(N)).
    """
    n = cipher.n_bits
    N = 1 << n
    queries = 0

    for k1_guess in range(N):
        oracle = build_prince_attack_oracle(cipher, k1_guess)
        recovered_k0_bits = run_simons_algorithm(oracle, n)
        recovered_k0 = int(recovered_k0_bits, 2)
        queries += n

        # Verify: does (k0_guess, k1_guess) explain the cipher?
        test_pt = 0
        test_ct = cipher.encrypt(test_pt)
        # Predicted: Core_{k1_guess}(test_pt XOR recovered_k0) XOR k0'
        k0_prime_guess = (recovered_k0 ^ cipher.alpha) & cipher.mask
        predicted = (cipher.core_encrypt(test_pt ^ recovered_k0, key=k1_guess)
                     ^ k0_prime_guess) & cipher.mask

        if predicted == test_ct:
            # Double-check
            test_pt2 = 1
            test_ct2 = cipher.encrypt(test_pt2)
            predicted2 = (cipher.core_encrypt(test_pt2 ^ recovered_k0, key=k1_guess)
                          ^ k0_prime_guess) & cipher.mask

            if predicted2 == test_ct2:
                # Full verification
                success = all(
                    cipher.encrypt(x) == (
                        cipher.core_encrypt(x ^ recovered_k0, key=k1_guess)
                        ^ k0_prime_guess
                    ) & cipher.mask
                    for x in range(N)
                )

                return {
                    "recovered_k0": recovered_k0,
                    "recovered_k1": k1_guess,
                    "actual_k0": cipher.k0,
                    "actual_k1": cipher.k1,
                    "k0_match": recovered_k0 == cipher.k0,
                    "k1_match": k1_guess == cipher.k1,
                    "success": success,
                    "queries": queries,
                    "n_bits": n,
                    "cipher": "PRINCE-like (FX construction)",
                    "classical_cost": f"O(2^{2*n}) exhaustive search",
                    "quantum_cost": f"O(n * 2^{n//2}) Grover-meet-Simon",
                }

    return {
        "success": False,
        "queries": queries,
        "n_bits": n,
        "actual_k0": cipher.k0,
        "actual_k1": cipher.k1,
    }


def prince_security_analysis(n_bits: int = 4) -> dict:
    """Analyze PRINCE security under classical and quantum attacks.

    PRINCE-64 (real cipher): 128-bit key (k0=64, k1=64)
        Classical: 2^127 security (meet-in-the-middle not applicable)
        Quantum (Grover): 2^64 security
        Quantum (Grover-meet-Simon): 2^32 * n security!

    Our simplified version: 2n-bit key (k0=n, k1=n)
    """
    return {
        "cipher": f"PRINCE-like ({n_bits}-bit block, {2*n_bits}-bit key)",
        "structure": "FX construction: E(x) = k0' XOR Core_k1(x XOR k0)",
        "classical_security": {
            "exhaustive_search": f"O(2^{2*n_bits})",
            "meet_in_middle": f"O(2^{n_bits}) with O(2^{n_bits}) memory",
            "best_classical": f"O(2^{n_bits}) time + memory",
        },
        "quantum_security": {
            "grover_only": f"O(2^{n_bits}) (brute-force key space)",
            "grover_meet_simon": f"O({n_bits} * 2^{n_bits//2})",
            "attack_model": "Q2 (superposition queries to E) or Q1 + birthday",
        },
        "real_prince_64": {
            "block_size": 64,
            "key_size": 128,
            "classical_security_bits": 127,
            "quantum_grover_bits": 64,
            "quantum_gms_bits": 37,  # 2^32 * 64 ~ 2^37
            "conclusion": "PRINCE is broken by Grover-meet-Simon with ~2^37 work",
        },
    }
