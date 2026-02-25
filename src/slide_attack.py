"""
Quantum slide attack on iterated block ciphers using Simon's algorithm.

The slide attack exploits ciphers that repeat the SAME keyed round function
r times:

    E_k(x) = F_k^r(x) = F_k(F_k(...F_k(x)...))

where F_k(x) = P(x XOR k) for a public permutation P and secret key k.

Classical slide attack (Biryukov & Wagner, 1999):
    Find a "slide pair" — two inputs (x, x') where x' = F_k(x), implying
    E_k(x') = F_k(E_k(x)).  Finding such a pair requires O(2^{n/2}) queries
    via the birthday bound, regardless of the number of rounds r.

Quantum slide attack (Kaplan et al., 2016):
    Construct f(x) = F_k(x) XOR P(x) = P(x XOR k) XOR P(x).

    f satisfies Simon's promise with secret s = k because:
        f(x XOR k) = P(x XOR k XOR k) XOR P(x XOR k)
                    = P(x) XOR P(x XOR k)
                    = f(x)          [XOR is commutative]

    Simon's algorithm recovers k in O(n) quantum queries.

Key insight:
    The attack complexity is O(n) regardless of the number of rounds r.
    Classical security of iterated ciphers grows with r (birthday bound
    for slide pairs), but the quantum slide attack bypasses all additional
    rounds entirely.  "Just add more rounds" is NOT a defense against
    a quantum adversary with access to the round function.

Threat model:
    The attacker needs quantum superposition access to the round function
    F_k (Q2 model).  This arises when:
      - The cipher is only 1 round (F_k = E_k, as in Even-Mansour).
      - The round function is exposed separately (e.g., in a MAC or KDF).
      - Fault injection causes the cipher to execute fewer rounds.
"""

from __future__ import annotations

import secrets

import numpy as np
from qiskit import QuantumCircuit

from .even_mansour import _truth_table_to_oracle
from .simons_algorithm import run_simons_algorithm


class SlideBlockCipher:
    """An iterated block cipher vulnerable to the quantum slide attack.

    One round:  F_k(x) = P(x XOR k)
    Full cipher: E_k(x) = F_k^r(x)  (r applications of the same round)

    P is a publicly known permutation.
    """

    def __init__(
        self,
        n_bits: int,
        n_rounds: int = 4,
        key: int | None = None,
        perm_seed: int = 42,
    ):
        self.n_bits = n_bits
        self.n_rounds = n_rounds
        self.mask = (1 << n_bits) - 1
        N = 1 << n_bits

        self.key = (key if key is not None else secrets.randbelow(N)) & self.mask

        # Public permutation P and its inverse
        self._perm = list(range(N))
        rng = np.random.default_rng(perm_seed)
        rng.shuffle(self._perm)

        self._inv_perm = [0] * N
        for i, v in enumerate(self._perm):
            self._inv_perm[v] = i

    def permutation(self, x: int) -> int:
        """Public permutation P(x)."""
        return self._perm[x]

    def inv_permutation(self, y: int) -> int:
        """Inverse permutation P^{-1}(y)."""
        return self._inv_perm[y]

    def one_round(self, x: int) -> int:
        """Single round: F_k(x) = P(x XOR k)."""
        return self.permutation((x ^ self.key) & self.mask)

    def one_round_inv(self, y: int) -> int:
        """Inverse of one round: F_k^{-1}(y) = P^{-1}(y) XOR k."""
        return self.inv_permutation(y) ^ self.key

    def encrypt(self, plaintext: int) -> int:
        """Encrypt by applying r rounds: E_k(x) = F_k^r(x)."""
        x = plaintext & self.mask
        for _ in range(self.n_rounds):
            x = self.one_round(x)
        return x

    def decrypt(self, ciphertext: int) -> int:
        """Decrypt by applying r inverse rounds."""
        x = ciphertext & self.mask
        for _ in range(self.n_rounds):
            x = self.one_round_inv(x)
        return x


def build_slide_attack_oracle(cipher: SlideBlockCipher) -> QuantumCircuit:
    """Build the Simon oracle for the quantum slide attack.

    Constructs f(x) = F_k(x) XOR P(x) = P(x XOR k) XOR P(x).

    This function has Simon period s = k because:
        f(x XOR k) = P(x) XOR P(x XOR k) = f(x).

    Note: This oracle uses the ONE-ROUND function F_k, not the full
    r-round cipher.  The slide attack's power is that it needs only
    one round, regardless of how many rounds the cipher has.
    """
    n = cipher.n_bits
    N = 1 << n

    truth_table = {}
    for x in range(N):
        truth_table[x] = cipher.one_round(x) ^ cipher.permutation(x)

    return _truth_table_to_oracle(truth_table, n)


def attack_slide_cipher(cipher: SlideBlockCipher) -> dict:
    """Execute the quantum slide attack to recover the key.

    Steps:
        1. Build the Simon oracle f(x) = F_k(x) XOR P(x) with period k.
        2. Run Simon's algorithm to recover k.
        3. Verify: check that the recovered key correctly encrypts all inputs.

    The attack makes O(n) quantum queries to the round function,
    independent of the number of rounds r.
    """
    n = cipher.n_bits
    N = 1 << n

    # Step 1: Build oracle from the one-round function
    oracle = build_slide_attack_oracle(cipher)

    # Step 2: Run Simon's algorithm to find s = k
    recovered_key_bits = run_simons_algorithm(oracle, n)
    recovered_key = int(recovered_key_bits, 2)

    # Step 3: Verify by rebuilding the cipher with the recovered key
    test_cipher = SlideBlockCipher(
        n_bits=n,
        n_rounds=cipher.n_rounds,
        key=recovered_key,
        perm_seed=42,
    )
    success = all(
        cipher.encrypt(x) == test_cipher.encrypt(x)
        for x in range(N)
    )

    return {
        "recovered_key": recovered_key,
        "actual_key": cipher.key,
        "success": success,
        "n_bits": n,
        "n_rounds": cipher.n_rounds,
    }
