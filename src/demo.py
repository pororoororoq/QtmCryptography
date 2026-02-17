#!/usr/bin/env python3
"""
Demonstration: Quantum attacks on symmetric ciphers using Simon's algorithm.

This script demonstrates:
1. Simon's algorithm recovering a secret string
2. Key recovery attack on the Even-Mansour cipher
3. Key recovery attack on a 3-round Feistel network

All simulations use Qiskit's statevector simulator (no hardware needed).
Block sizes are kept small (4-8 bits) for simulation feasibility.
"""

from __future__ import annotations

import time


def demo_simons_basic():
    """Demonstrate basic Simon's algorithm on a known secret."""
    from src.simons_algorithm import build_oracle_from_secret, run_simons_algorithm

    print("=" * 60)
    print("DEMO 1: Simon's Algorithm -- Basic Secret Recovery")
    print("=" * 60)

    secrets = ["110", "1010", "0101", "1001"]

    for secret in secrets:
        n = len(secret)
        oracle = build_oracle_from_secret(secret)
        recovered = run_simons_algorithm(oracle, n)

        status = "OK" if recovered == secret else "FAIL"
        print(f"  Secret: {secret}  |  Recovered: {recovered}  |  [{status}]")

    # Test s = 0 (1-to-1 function)
    oracle_1to1 = build_oracle_from_secret("0000")
    recovered_1to1 = run_simons_algorithm(oracle_1to1, 4)
    status = "OK" if recovered_1to1 == "0000" else "FAIL"
    print(f"  Secret: 0000  |  Recovered: {recovered_1to1}  |  [{status}]  (1-to-1 case)")
    print()


def demo_even_mansour_attack():
    """Demonstrate quantum key recovery on Even-Mansour cipher."""
    from src.even_mansour import EvenMansourCipher, attack_even_mansour

    print("=" * 60)
    print("DEMO 2: Quantum Attack on Even-Mansour Cipher")
    print("=" * 60)
    print()
    print("  Cipher: E(x) = P(x XOR k1) XOR k2")
    print("  Attack: f(x) = E(x) XOR P(x) has Simon period s = k1")
    print()

    for trial in range(3):
        cipher = EvenMansourCipher(n_bits=4)

        print(f"  Trial {trial + 1}: k1={cipher.k1:04b}, k2={cipher.k2:04b}")

        t0 = time.time()
        result = attack_even_mansour(cipher)
        elapsed = time.time() - t0

        rk1 = result["recovered_k1"]
        rk2 = result["recovered_k2"]
        ok = result["functionally_equivalent"]

        print(f"    Recovered k1={rk1:04b}, k2={rk2:04b}")
        print(f"    Functionally equivalent: {ok}  ({elapsed:.2f}s)")
        print()


def demo_feistel_attack():
    """Demonstrate quantum key recovery on a 3-round Feistel network."""
    from src.feistel_attack import Feistel3RoundNonlinear, attack_feistel_3round

    print("=" * 60)
    print("DEMO 3: Quantum Attack on 3-Round Feistel Network")
    print("=" * 60)
    print()
    print("  Cipher: 3-round Feistel with F(x) = S[x XOR k]")
    print("  Attack: f(x) = E_L(x,0) XOR E_L(x,1) has Simon period")
    print("          s = S[k] XOR S[1 XOR k]")
    print("          Then brute-force k from reduced candidates.")
    print()

    for trial in range(3):
        cipher = Feistel3RoundNonlinear(half_bits=4)
        print(f"  Trial {trial + 1}: key={cipher.key:04b} ({cipher.key})")

        t0 = time.time()
        result = attack_feistel_3round(cipher)
        elapsed = time.time() - t0

        print(f"    Simon's period: {result['simon_period']:04b}")
        print(f"    Key candidates: {result['n_candidates']}")
        print(f"    Recovered key:  {result['recovered_key']}")
        print(f"    Success: {result['success']}  ({elapsed:.2f}s)")
        print()


def main():
    print()
    print("Quantum Attacks on Symmetric Cryptography via Simon's Algorithm")
    print("=" * 60)
    print()
    print("Simon's algorithm finds a hidden period s of a function")
    print("f: {0,1}^n -> {0,1}^n where f(x) = f(x XOR s), using O(n)")
    print("quantum queries vs. O(2^{n/2}) classical queries.")
    print()
    print("This exponential speedup breaks certain symmetric ciphers")
    print("when the attacker has quantum superposition access (Q2 model).")
    print()

    demo_simons_basic()
    demo_even_mansour_attack()
    demo_feistel_attack()

    print("=" * 60)
    print("All demonstrations complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
