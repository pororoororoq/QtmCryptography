"""
Time quantum (Simon's) vs classical brute-force attacks on PRINCE-like ciphers.

For each key size n, we:
  1. Create a PRINCE-like cipher (FX/Even-Mansour structure)
  2. Run Simon's algorithm (quantum simulation) to recover k0 — time it
  3. Run classical brute-force to recover k0 — time it (cap at 120s)

The quantum attack uses the Even-Mansour reduction (core step of
Grover-meet-Simon): f(x) = E(x) XOR Core_k1(x), which has period k0.
"""

import json
import sys
import time
import signal

sys.path.insert(0, ".")

from src.prince_attack import PRINCELikeCipher, build_prince_attack_oracle
from src.simons_algorithm import run_simons_algorithm

TIMEOUT_QUANTUM = 600   # 10 min max per quantum run
TIMEOUT_CLASSICAL = 120  # 2 min max per classical run

results = {}
classical_timed_out = False


def classical_brute_force(cipher):
    """Try all possible k0 values until finding the right one."""
    n = cipher.n_bits
    N = 1 << n
    test_pt = 0
    test_ct = cipher.encrypt(test_pt)
    test_pt2 = 1
    test_ct2 = cipher.encrypt(test_pt2)

    for k0_guess in range(N):
        k0_prime_guess = (k0_guess ^ cipher.alpha) & cipher.mask
        for k1_guess in range(N):
            predicted = (cipher.core_encrypt(test_pt ^ k0_guess, key=k1_guess)
                         ^ k0_prime_guess) & cipher.mask
            if predicted == test_ct:
                predicted2 = (cipher.core_encrypt(test_pt2 ^ k0_guess, key=k1_guess)
                              ^ k0_prime_guess) & cipher.mask
                if predicted2 == test_ct2:
                    return k0_guess, k1_guess
    return None, None


def quantum_attack(cipher):
    """Run Simon's algorithm on the PRINCE oracle (assuming correct k1)."""
    n = cipher.n_bits
    oracle = build_prince_attack_oracle(cipher, cipher.k1)
    recovered_bits = run_simons_algorithm(oracle, n)
    recovered_k0 = int(recovered_bits, 2)
    return recovered_k0


# Range of n to test
n_values = list(range(3, 21))  # Start optimistic, bail if too slow

quantum_timed_out = False

print("=" * 65)
print(f"{'n':>4} | {'Quantum (s)':>14} | {'Classical (s)':>14} | {'Speedup':>10}")
print("-" * 65)

for n in n_values:
    entry = {"n": n}

    # --- Quantum attack ---
    if not quantum_timed_out:
        try:
            cipher = PRINCELikeCipher(n_bits=n, k0=None, k1=None, seed=42)
            t0 = time.time()
            recovered_k0 = quantum_attack(cipher)
            t_quantum = time.time() - t0
            q_success = (recovered_k0 == cipher.k0)
            entry["quantum_time_s"] = t_quantum
            entry["quantum_success"] = q_success
        except (MemoryError, Exception) as e:
            entry["quantum_time_s"] = None
            entry["quantum_error"] = str(e)
            quantum_timed_out = True
            print(f"  Quantum simulation hit wall at n={n}: {e}")
    else:
        entry["quantum_time_s"] = None

    if entry.get("quantum_time_s") is not None and entry["quantum_time_s"] > TIMEOUT_QUANTUM:
        quantum_timed_out = True

    # --- Classical brute-force ---
    if not classical_timed_out:
        try:
            cipher_c = PRINCELikeCipher(n_bits=n, k0=None, k1=None, seed=42)
            t0 = time.time()

            # Use alarm for timeout on unix
            def timeout_handler(signum, frame):
                raise TimeoutError("Classical search exceeded 120s")

            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(TIMEOUT_CLASSICAL)

            k0_found, k1_found = classical_brute_force(cipher_c)
            t_classical = time.time() - t0

            signal.alarm(0)  # Cancel alarm

            c_success = (k0_found == cipher_c.k0 and k1_found == cipher_c.k1)
            entry["classical_time_s"] = t_classical
            entry["classical_success"] = c_success
        except (TimeoutError, Exception) as e:
            t_classical = time.time() - t0
            entry["classical_time_s"] = None
            entry["classical_timeout"] = True
            classical_timed_out = True
            signal.alarm(0)
            print(f"  Classical brute-force timed out at n={n} (>{TIMEOUT_CLASSICAL}s)")
    else:
        entry["classical_time_s"] = None
        entry["classical_timeout"] = True

    # Print row
    qt = f"{entry['quantum_time_s']:.4f}" if entry.get("quantum_time_s") is not None else "---"
    ct = f"{entry['classical_time_s']:.4f}" if entry.get("classical_time_s") is not None else ">120"
    if entry.get("quantum_time_s") and entry.get("classical_time_s"):
        speedup = entry["classical_time_s"] / entry["quantum_time_s"]
        sp = f"{speedup:.1f}x"
    else:
        sp = "---"
    print(f"{n:>4} | {qt:>14} | {ct:>14} | {sp:>10}")

    results[str(n)] = entry

    # Save incrementally
    with open("experiments/results/prince_timing.json", "w") as f:
        json.dump(results, f, indent=2)

    # Bail if quantum is also too slow
    if quantum_timed_out:
        print(f"\nQuantum simulation wall reached at n={n}. Stopping.")
        break

print("=" * 65)
print(f"\nResults saved to experiments/results/prince_timing.json")
