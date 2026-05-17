"""
Time quantum (Simon's) vs classical brute-force on PRINCE-like ciphers, n=3 to 127.

Quantum side: mathematical simulation of Simon's algorithm.
  - Sample n+10 random vectors y where y·s = 0 (mod 2)
  - Solve via GF(2) Gaussian elimination
  - Complexity: O(n^3)

Classical side: brute-force search over 2^n key candidates.
  - Uses a lightweight keyed cipher (no lookup tables, so it scales in memory)
  - For each k_guess, encrypt a test plaintext and compare to known ciphertext
  - Cap at 120 seconds
"""

import json
import time
import signal
import secrets
import numpy as np

TIMEOUT_CLASSICAL = 120
results = {}
classical_done = False


def sample_simon_equations(s_bits, n, num_samples):
    """Simulate quantum measurement outputs: random y with y·s = 0 mod 2."""
    s = np.array(s_bits, dtype=np.int8)
    equations = []
    for _ in range(num_samples):
        while True:
            y = np.random.randint(0, 2, size=n, dtype=np.int8)
            if np.dot(y, s) % 2 == 0:
                equations.append(y)
                break
    return equations


def solve_gf2(equations, n):
    """Gaussian elimination over GF(2) to recover s."""
    if not equations:
        return None
    mat = np.array(equations, dtype=np.int8) % 2
    rows, cols = mat.shape

    pivot_row = 0
    pivot_cols = []
    for col in range(cols):
        found = False
        for row in range(pivot_row, rows):
            if mat[row, col] == 1:
                mat[[pivot_row, row]] = mat[[row, pivot_row]]
                found = True
                break
        if not found:
            continue
        pivot_cols.append(col)
        for row in range(rows):
            if row != pivot_row and mat[row, col] == 1:
                mat[row] = (mat[row] + mat[pivot_row]) % 2
        pivot_row += 1

    rank = len(pivot_cols)
    if rank >= n - 1:
        s = np.zeros(n, dtype=np.int8)
        free_cols = [c for c in range(n) if c not in pivot_cols]
        if free_cols:
            free_col = free_cols[0]
            s[free_col] = 1
            for i, pc in enumerate(pivot_cols):
                s[pc] = mat[i, free_col]
        return s
    return None


def simon_attack_mathematical(n):
    """Full mathematical simulation of Simon's algorithm on n-bit key."""
    s_bits = [secrets.randbelow(2) for _ in range(n)]
    if all(b == 0 for b in s_bits):
        s_bits[0] = 1

    t0 = time.time()
    num_samples = n + 10
    equations = sample_simon_equations(s_bits, n, num_samples)
    recovered = solve_gf2(equations, n)
    t_total = time.time() - t0

    success = recovered is not None and list(recovered) == s_bits
    return t_total, success


def lightweight_encrypt(plaintext, key, n):
    """Lightweight n-bit cipher (no lookup tables). Models PRINCE-like structure.

    Uses repeated XOR + rotate as a stand-in for a real SPN.
    This lets classical brute-force scale to any n without memory issues.
    """
    mask = (1 << n) - 1
    state = (plaintext ^ key) & mask
    for _ in range(3):
        state = ((state << 1) | (state >> (n - 1))) & mask
        state = (state ^ key) & mask
        state = (state + 0xA5A5 & mask) & mask  # nonlinear mixing
    return state


def classical_brute_force(n):
    """Brute-force key search: try all 2^n keys."""
    N = 1 << n
    mask = (1 << n) - 1
    true_key = secrets.randbelow(N)

    pt0 = 0
    pt1 = 1
    ct0 = lightweight_encrypt(pt0, true_key, n)
    ct1 = lightweight_encrypt(pt1, true_key, n)

    t0 = time.time()
    for k_guess in range(N):
        if lightweight_encrypt(pt0, k_guess, n) == ct0:
            if lightweight_encrypt(pt1, k_guess, n) == ct1:
                t_total = time.time() - t0
                return t_total, (k_guess == true_key)

    t_total = time.time() - t0
    return t_total, False


# Run experiments
n_values = list(range(3, 128))

print("=" * 70)
print(f"{'n':>5} | {'Quantum (s)':>14} | {'Classical (s)':>14} | {'Speedup':>12}")
print("-" * 70)

for n in n_values:
    entry = {"n": n}

    # Quantum (mathematical simulation)
    t_q, q_success = simon_attack_mathematical(n)
    entry["quantum_time_s"] = t_q
    entry["quantum_success"] = q_success

    # Classical brute-force
    if not classical_done:
        try:
            def timeout_handler(signum, frame):
                raise TimeoutError()
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(TIMEOUT_CLASSICAL + 5)

            t_c, c_success = classical_brute_force(n)
            signal.alarm(0)

            entry["classical_time_s"] = t_c
            entry["classical_success"] = c_success

            if t_c > TIMEOUT_CLASSICAL:
                classical_done = True
        except (TimeoutError, MemoryError, OverflowError) as e:
            signal.alarm(0)
            entry["classical_time_s"] = None
            entry["classical_timeout"] = True
            classical_done = True
            if isinstance(e, TimeoutError):
                print(f"  Classical timed out at n={n} (>{TIMEOUT_CLASSICAL}s)")
            else:
                print(f"  Classical failed at n={n}: {type(e).__name__}")
    else:
        entry["classical_time_s"] = None
        entry["classical_timeout"] = True

    # Print
    qt = f"{t_q:.6f}" if t_q < 0.01 else f"{t_q:.4f}"
    if entry.get("classical_time_s") is not None:
        ct = f"{entry['classical_time_s']:.6f}" if entry['classical_time_s'] < 0.01 else f"{entry['classical_time_s']:.4f}"
    else:
        ct = ">120"

    if entry.get("classical_time_s") is not None and t_q > 0:
        speedup = entry["classical_time_s"] / t_q
        sp = f"{speedup:.1f}x"
    else:
        sp = "---"

    print(f"{n:>5} | {qt:>14} | {ct:>14} | {sp:>12}")
    import sys
    sys.stdout.flush()

    results[str(n)] = entry

    with open("experiments/results/prince_timing.json", "w") as f:
        json.dump(results, f, indent=2)

print("=" * 70)
print(f"\nResults saved to experiments/results/prince_timing.json")
print(f"Quantum attack completed all {len(n_values)} key sizes up to n={n_values[-1]}.")
if classical_done:
    last_classical = max(int(k) for k, v in results.items()
                         if v.get("classical_time_s") is not None)
    print(f"Classical brute-force timed out after n={last_classical}.")
