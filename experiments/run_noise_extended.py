"""Run noise phase transition experiment for n=3..8."""
import sys, json, time
sys.path.insert(0, "/home/user/QtmCryptography")

import numpy as np
from src.noisy_simon import run_noisy_simons_algorithm
from src.simons_algorithm import build_oracle_from_secret

configs = [(3, 50), (4, 50), (5, 30), (6, 20), (7, 10), (8, 5)]
epsilons = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
results = {}

t_total = time.time()
for n, trials in configs:
    N = 1 << n
    results[n] = {}
    t0 = time.time()
    print(f"  n={n} ({trials} trials): ", end="", flush=True)

    for eps in epsilons:
        rng = np.random.default_rng(42)
        successes = 0
        for t in range(trials):
            s_int = rng.integers(1, N)
            secret = format(s_int, f"0{n}b")
            oracle = build_oracle_from_secret(secret)
            n_samples = max(60, min(500, int(10 * n / max(1 - 2 * eps, 0.1) ** 2)))
            result = run_noisy_simons_algorithm(
                oracle, n, epsilon=eps,
                n_samples=n_samples,
                secret_for_noise=secret,
                seed=t * 13 + 7,
            )
            if result["recovered_s"] == secret:
                successes += 1

        rate = successes / trials
        results[n][str(eps)] = rate
        print(f"{eps:.0%}->{rate:.0%} ", end="", flush=True)
    print(f" [{time.time()-t0:.1f}s]")

out_path = "/home/user/QtmCryptography/experiments/results/noise_phase_transition.json"
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out_path}  (total {time.time()-t_total:.1f}s)")
