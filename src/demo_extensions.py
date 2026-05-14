#!/usr/bin/env python3
"""
Demonstration of advanced extensions to Simon's algorithm attacks.

Run with:  python -m src.demo_extensions

Extensions demonstrated:
1. Grover-meet-Simon hybrid attack on FX construction
2. Noisy Simon's algorithm with error-tolerant recovery
3. Q1 offline Simon (classical queries + local quantum)
4. Hardware noise simulation across device profiles
5. Resource estimation for real-world cipher scales
6. Attack on PRINCE-like cipher (real S-box)
"""

from __future__ import annotations

import time


def demo_grover_meet_simon():
    """Grover-meet-Simon hybrid attack on the FX construction."""
    from src.grover_meet_simon import FXCipher, grover_meet_simon_attack

    print("=" * 64)
    print("EXTENSION 1: Grover-meet-Simon on FX Construction")
    print("=" * 64)
    print()
    print("  FX cipher: E(x) = P_{k_in}(x XOR k_out) XOR k_out")
    print("  Attack: Grover-search k_in, Simon's recovers k_out per guess")
    print("  Cost: O(n * 2^{n/2}) vs O(2^{2n}) classical brute force")
    print()

    for trial in range(3):
        cipher = FXCipher(n_bits=4, perm_seed=42)
        ki, ko = cipher.k_inner, cipher.k_outer

        t0 = time.time()
        result = grover_meet_simon_attack(cipher)
        elapsed = time.time() - t0

        rki = result.get("recovered_k_inner", "?")
        rko = result.get("recovered_k_outer", "?")
        ok = result["success"]

        print(f"  Trial {trial+1}: k_in={ki:04b}, k_out={ko:04b}")
        print(f"    Recovered k_in={rki:04b}, k_out={rko:04b}")
        print(f"    Success: {ok}  ({elapsed:.2f}s, {result.get('queries',0)} queries)")
        print()


def demo_noisy_simon():
    """Simon's algorithm under measurement noise."""
    from src.noisy_simon import run_noisy_simons_algorithm, run_noisy_vs_clean_comparison
    from src.simons_algorithm import build_oracle_from_secret

    print("=" * 64)
    print("EXTENSION 2: Simon's Algorithm with Noise")
    print("=" * 64)
    print()
    print("  Simulates imperfect measurements where y . s != 0 with")
    print("  probability epsilon. Uses majority-vote decoding to recover.")
    print()

    secret = "1010"
    oracle = build_oracle_from_secret(secret)

    print(f"  Secret: {secret}")
    print(f"  {'Noise (eps)':>12}  {'Recovered':>10}  {'Correct?':>9}  {'Valid samples':>14}")
    print(f"  {'-'*12}  {'-'*10}  {'-'*9}  {'-'*14}")

    for eps in [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30]:
        result = run_noisy_simons_algorithm(
            oracle, n=4, epsilon=eps,
            n_samples=60, secret_for_noise=secret, seed=42,
        )
        rec = result["recovered_s"]
        ok = "YES" if rec == secret else "NO"
        n_correct = result["n_correct_samples"]
        total = result["n_samples"]
        pct = f"{n_correct}/{total}" if n_correct is not None else "N/A"
        print(f"  {eps:>12.0%}  {rec:>10}  {ok:>9}  {pct:>14}")

    print()

    # Comparison over multiple trials
    print("  Aggregate over 20 trials (n=4, secret=1010):")
    for eps in [0.0, 0.10, 0.20, 0.30]:
        comp = run_noisy_vs_clean_comparison(n=4, secret="1010", epsilon=eps, n_trials=20)
        print(f"    eps={eps:.0%}: clean={comp['clean_success_rate']:.0%}, "
              f"noisy={comp['noisy_success_rate']:.0%}")
    print()


def demo_offline_simon():
    """Q1 offline attack: classical queries + local quantum processing."""
    from src.even_mansour import EvenMansourCipher
    from src.offline_simon import offline_simon_attack, compare_q1_vs_q2

    print("=" * 64)
    print("EXTENSION 3: Q1 Offline Simon (No Quantum Network Needed)")
    print("=" * 64)
    print()
    print("  Q2 model: quantum superposition queries to the cipher")
    print("  Q1 model: classical queries only + offline quantum computer")
    print("  Both recover keys, but Q1 needs no quantum channel!")
    print()

    cipher = EvenMansourCipher(n_bits=4, k1=11, k2=6, perm_seed=42)
    print(f"  Target: Even-Mansour, n=4, k1={cipher.k1:04b}, k2={cipher.k2:04b}")
    print()

    # Offline attack
    t0 = time.time()
    result = offline_simon_attack(cipher, verbose=False)
    elapsed = time.time() - t0

    print(f"  Phase 1: {result['classical_queries']} classical queries")
    print(f"  Phase 2: ~{result['quantum_queries']} quantum oracle calls (offline)")
    print(f"  Recovered: k1={result['recovered_k1']:04b}, k2={result['recovered_k2']:04b}")
    print(f"  Success: {result['success']}  ({elapsed:.2f}s)")
    print()

    # Q1 vs Q2 comparison
    comp = compare_q1_vs_q2(cipher)
    print("  Model comparison:")
    print(f"    Q2 (quantum queries): success={comp['q2_attack']['success']}, "
          f"requires quantum network: {comp['q2_attack']['requires_quantum_network']}")
    print(f"    Q1 (classical + offline): success={comp['q1_attack']['success']}, "
          f"requires quantum network: {comp['q1_attack']['requires_quantum_network']}")
    print()


def demo_hardware_noise():
    """Simulate Simon's algorithm on noisy quantum hardware."""
    from src.hardware_noise import (
        run_simon_noisy_hardware, hardware_comparison,
        IBM_HERON, NISQ_GENERIC, FUTURE_DEVICE,
    )

    print("=" * 64)
    print("EXTENSION 4: Hardware Noise Simulation")
    print("=" * 64)
    print()
    print("  Simulates depolarizing gate noise + readout errors")
    print("  across three hardware profiles.")
    print()

    secret = "110"
    print(f"  Secret: {secret}")
    print()

    for profile in [FUTURE_DEVICE, IBM_HERON, NISQ_GENERIC]:
        t0 = time.time()
        result = run_simon_noisy_hardware(
            secret, profile=profile, n_shots=1024, n_rounds=12,
        )
        elapsed = time.time() - t0

        print(f"  {profile.name}:")
        print(f"    1Q error={profile.single_qubit_error}, "
              f"2Q error={profile.two_qubit_error}, "
              f"readout={profile.readout_error}")
        print(f"    Valid equations: {result['fraction_valid']:.0%}")
        print(f"    Recovered: {result['recovered']}  "
              f"Success: {result['success']}  ({elapsed:.2f}s)")
        stats = result["circuit_stats"]
        print(f"    Circuit: {stats['n_qubits']} qubits, "
              f"{stats['cx_count']} CX gates, depth {stats['depth']}")
        print()


def demo_resource_estimation():
    """Project physical resource requirements for real-world ciphers."""
    from src.resource_estimation import (
        generate_scaling_report, compare_with_grover,
    )

    print("=" * 64)
    print("EXTENSION 5: Resource Estimation")
    print("=" * 64)
    print()
    print("  Estimates fault-tolerant (surface code) resources for")
    print("  Simon's attack at cryptographically relevant scales.")
    print()

    report = generate_scaling_report([4, 8, 16, 32, 64, 128, 256])

    print(f"  {'n':>4}  {'Logical':>8}  {'Physical':>10}  {'T-gates':>12}  {'Code dist':>9}")
    print(f"  {'─'*4}  {'─'*8}  {'─'*10}  {'─'*12}  {'─'*9}")
    for n, data in report["scaling_data"].items():
        print(f"  {n:>4}  {data['logical_qubits']:>8}  "
              f"{data['physical_qubits']:>10,}  "
              f"{data['t_gates']:>12,}  "
              f"{data['code_distance']:>9}")
    print()

    # Simon vs Grover
    print("  Simon's vs Grover query comparison:")
    print(f"  {'n':>4}  {'Simon':>8}  {'Grover':>14}  {'Speedup':>16}")
    print(f"  {'─'*4}  {'─'*8}  {'─'*14}  {'─'*16}")
    for n in [16, 32, 64, 128]:
        comp = compare_with_grover(n)
        simon_q = comp["simon_attack"]["oracle_queries"]
        grover_q = comp["grover_brute_force"]["oracle_queries"]
        speedup = comp["speedup_factor"]
        print(f"  {n:>4}  {simon_q:>8}  {grover_q:>14,}  {speedup:>14,.0f}x")
    print()


def demo_prince_attack():
    """Attack a PRINCE-like cipher with real PRINCE S-box."""
    from src.prince_attack import (
        PRINCELikeCipher, attack_prince_cipher, prince_security_analysis,
    )

    print("=" * 64)
    print("EXTENSION 6: Attack on PRINCE-like Cipher (Real S-box)")
    print("=" * 64)
    print()
    print("  PRINCE structure: E(x) = k0' XOR Core_{k1}(x XOR k0)")
    print("  This IS the FX construction — vulnerable to Grover-meet-Simon.")
    print("  Using the actual PRINCE 4-bit S-box.")
    print()

    for trial in range(3):
        cipher = PRINCELikeCipher(n_bits=4, seed=42)
        k0, k1 = cipher.k0, cipher.k1

        t0 = time.time()
        result = attack_prince_cipher(cipher)
        elapsed = time.time() - t0

        rk0 = result.get("recovered_k0", "?")
        rk1 = result.get("recovered_k1", "?")
        ok = result["success"]

        print(f"  Trial {trial+1}: k0={k0:04b}, k1={k1:04b}")
        print(f"    Recovered k0={rk0:04b}, k1={rk1:04b}")
        print(f"    Success: {ok}  ({elapsed:.2f}s)")
        print()

    # Security analysis for real PRINCE-64
    analysis = prince_security_analysis(4)
    real = analysis["real_prince_64"]
    print(f"  Real PRINCE-64 implications:")
    print(f"    Block: {real['block_size']}-bit, Key: {real['key_size']}-bit")
    print(f"    Classical security: ~2^{real['classical_security_bits']} operations")
    print(f"    Grover brute-force: ~2^{real['quantum_grover_bits']} operations")
    print(f"    Grover-meet-Simon:  ~2^{real['quantum_gms_bits']} operations")
    print(f"    --> {real['conclusion']}")
    print()


def main():
    print()
    print("Advanced Extensions: Quantum Cryptanalysis via Simon's Algorithm")
    print("=" * 64)
    print()

    demo_grover_meet_simon()
    demo_noisy_simon()
    demo_offline_simon()
    demo_hardware_noise()
    demo_resource_estimation()
    demo_prince_attack()

    print("=" * 64)
    print("All extension demonstrations complete.")
    print("=" * 64)


if __name__ == "__main__":
    main()
