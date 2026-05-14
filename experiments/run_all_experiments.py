#!/usr/bin/env python3
"""
Comprehensive data collection for quantum cryptanalysis experiments.

Runs systematic experiments across all attack types and key sizes,
collecting presentation-ready data for science-fair poster.

Run with:  python -m experiments.run_all_experiments
Run one:   python -m experiments.run_all_experiments 2 7

Experiments:
    1. Success rate vs key size (all 4 core attacks, n=3-5)
    2. Query complexity: actual queries vs theoretical O(n) (n=3-8)
    3. Noise phase transition: success rate vs (epsilon, n) (n=3-6)
    4. Slide attack round-independence (n=3-5)
    5. Wall-clock timing curves (n=3-8, 3 trials)
    6. Hardware noise: success across device profiles (n=3-4)
    7. Rank convergence curves (n=3-8)
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np


RESULTS_DIR = Path(__file__).parent / "results"


def _ensure_results_dir():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def _flush(msg: str):
    sys.stdout.write(msg)
    sys.stdout.flush()


# ── Experiment 1: Success Rate vs Key Size ────────────────────────────

def experiment_success_rate_vs_n():
    """Attack success rate at each key size (truth-table attacks: n=3-5)."""
    from src.simons_algorithm import build_oracle_from_secret, run_simons_algorithm
    from src.even_mansour import EvenMansourCipher, attack_even_mansour
    from src.feistel_attack import Feistel3RoundNonlinear, attack_feistel_3round
    from src.slide_attack import SlideBlockCipher, attack_slide_cipher

    print("=" * 70)
    print("EXPERIMENT 1: Success Rate vs Key Size")
    print("=" * 70)

    results = {}
    configs = [(3, 50), (4, 50), (5, 10)]

    for n, trials in configs:
        N = 1 << n
        rng = np.random.default_rng(42)
        row = {"n": n, "n_trials": trials}
        _flush(f"  n={n} ({trials} trials): ")

        # Simon's basic
        rng2 = np.random.default_rng(42)
        simon_ok = 0
        for t in range(trials):
            s_int = rng2.integers(1, N)
            secret = format(s_int, f"0{n}b")
            oracle = build_oracle_from_secret(secret)
            if run_simons_algorithm(oracle, n) == secret:
                simon_ok += 1
        row["simon_basic"] = simon_ok / trials
        _flush(f"S={simon_ok}/{trials} ")

        # Even-Mansour
        em_ok = 0
        for t in range(trials):
            k1, k2 = int(rng2.integers(0, N)), int(rng2.integers(0, N))
            cipher = EvenMansourCipher(n_bits=n, k1=k1, k2=k2, perm_seed=42)
            if attack_even_mansour(cipher)["functionally_equivalent"]:
                em_ok += 1
        row["even_mansour"] = em_ok / trials
        _flush(f"EM={em_ok}/{trials} ")

        # Feistel 3-round (skip n=3)
        if n >= 4:
            feistel_ok = 0
            for t in range(trials):
                key = int(rng2.integers(0, N))
                cipher = Feistel3RoundNonlinear(half_bits=n, key=key, seed=42)
                if attack_feistel_3round(cipher)["success"]:
                    feistel_ok += 1
            row["feistel_3round"] = feistel_ok / trials
        else:
            row["feistel_3round"] = None
        f3 = f"{row['feistel_3round']:.0%}" if row['feistel_3round'] is not None else "N/A"
        _flush(f"F={f3} ")

        # Slide attack
        slide_ok = 0
        for t in range(trials):
            key = int(rng2.integers(1, N))
            cipher = SlideBlockCipher(n_bits=n, n_rounds=5, key=key, perm_seed=42)
            if attack_slide_cipher(cipher)["success"]:
                slide_ok += 1
        row["slide_5rounds"] = slide_ok / trials

        results[n] = row
        print(f"Sl={slide_ok}/{trials}")

    _ensure_results_dir()
    with open(RESULTS_DIR / "success_rate_vs_n.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"  -> Saved to {RESULTS_DIR / 'success_rate_vs_n.json'}")
    print()
    return results


# ── Experiment 2: Query Complexity ────────────────────────────────────

def experiment_query_complexity():
    """Actual queries needed vs theoretical O(n). Uses basic oracle (fast)."""
    from src.simons_algorithm import build_oracle_from_secret, _sample_y_bits, _rank_gf2

    print("=" * 70)
    print("EXPERIMENT 2: Query Complexity — Actual vs Theoretical")
    print("=" * 70)

    results = {}
    configs = [(3, 100), (4, 100), (5, 80), (6, 40), (7, 15), (8, 5)]

    for n, trials in configs:
        N = 1 << n
        rng = np.random.default_rng(42)
        queries_list = []
        _flush(f"  n={n} ({trials} trials): ")

        for t in range(trials):
            s_int = rng.integers(1, N)
            secret = format(s_int, f"0{n}b")
            oracle = build_oracle_from_secret(secret)

            equations = []
            queries = 0
            for q in range(20 * n):
                y_bits = _sample_y_bits(oracle, n)
                queries += 1
                if all(b == 0 for b in y_bits):
                    continue
                equations.append(y_bits)
                if _rank_gf2(equations, n) >= n - 1:
                    queries_list.append(queries)
                    break

        arr = np.array(queries_list)
        results[n] = {
            "n": n,
            "theoretical_min": n - 1,
            "mean_queries": float(np.mean(arr)),
            "median_queries": float(np.median(arr)),
            "std_queries": float(np.std(arr)),
            "min_queries": int(np.min(arr)),
            "max_queries": int(np.max(arr)),
            "ratio_to_n": float(np.mean(arr) / n),
            "n_solved": len(queries_list),
            "n_trials": trials,
        }

        r = results[n]
        print(f"mean={r['mean_queries']:.1f} ({r['ratio_to_n']:.2f}n), "
              f"median={r['median_queries']:.0f}, [{r['min_queries']},{r['max_queries']}]")

    _ensure_results_dir()
    with open(RESULTS_DIR / "query_complexity.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"  -> Saved to {RESULTS_DIR / 'query_complexity.json'}")
    print()
    return results


# ── Experiment 3: Noise Phase Transition ──────────────────────────────

def experiment_noise_phase_transition():
    """2D sweep: success rate as function of (noise epsilon, bit size n)."""
    from src.noisy_simon import run_noisy_simons_algorithm
    from src.simons_algorithm import build_oracle_from_secret

    print("=" * 70)
    print("EXPERIMENT 3: Noise Phase Transition")
    print("=" * 70)

    configs = [(3, 50), (4, 50), (5, 20)]
    epsilons = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
    results = {}

    for n, trials in configs:
        N = 1 << n
        results[n] = {}
        _flush(f"  n={n} ({trials} trials): ")

        for eps in epsilons:
            rng = np.random.default_rng(42)
            successes = 0
            for t in range(trials):
                s_int = rng.integers(1, N)
                secret = format(s_int, f"0{n}b")
                oracle = build_oracle_from_secret(secret)
                n_samples = max(60, int(10 * n / max(1 - 2 * eps, 0.1) ** 2))
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
            _flush(f"{eps:.0%}→{rate:.0%} ")
        print()

    _ensure_results_dir()
    with open(RESULTS_DIR / "noise_phase_transition.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"  -> Saved to {RESULTS_DIR / 'noise_phase_transition.json'}")
    print()
    return results


# ── Experiment 4: Slide Attack Round-Independence ─────────────────────

def experiment_slide_round_independence():
    """Verify that slide attack cost is constant regardless of round count."""
    from src.slide_attack import SlideBlockCipher, attack_slide_cipher

    print("=" * 70)
    print("EXPERIMENT 4: Slide Attack Round-Independence")
    print("=" * 70)

    configs = [(3, 30), (4, 20)]
    round_counts = [1, 2, 5, 10, 20, 50, 100]
    results = {}

    for n, trials in configs:
        N = 1 << n
        results[n] = {}

        for r in round_counts:
            rng = np.random.default_rng(42)
            successes = 0
            times = []
            for t in range(trials):
                key = int(rng.integers(1, N))
                cipher = SlideBlockCipher(n_bits=n, n_rounds=r, key=key, perm_seed=42)
                t0 = time.time()
                result = attack_slide_cipher(cipher)
                times.append(time.time() - t0)
                if result["success"]:
                    successes += 1

            rate = successes / trials
            mean_time = float(np.mean(times))
            results[n][r] = {"success_rate": rate, "mean_time_s": mean_time, "n_trials": trials}
            print(f"  n={n}, r={r:>3}: success={rate:.0%}, time={mean_time:.4f}s")

    _ensure_results_dir()
    with open(RESULTS_DIR / "slide_round_independence.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"  -> Saved to {RESULTS_DIR / 'slide_round_independence.json'}")
    print()
    return results


# ── Experiment 5: Wall-Clock Timing Curves ────────────────────────────

def experiment_timing_curves():
    """Wall-clock time vs n — shows exponential classical simulation cost."""
    from src.simons_algorithm import build_oracle_from_secret, run_simons_algorithm
    from src.even_mansour import EvenMansourCipher, attack_even_mansour

    print("=" * 70)
    print("EXPERIMENT 5: Wall-Clock Timing Curves")
    print("=" * 70)

    results = {}

    # Simon's basic: lightweight oracle, can go up to n=8
    print("  Simon's basic (build_oracle_from_secret):")
    for n in [3, 4, 5, 6, 7, 8]:
        trials = 5 if n <= 6 else 3
        N = 1 << n
        rng = np.random.default_rng(42)
        times = []
        for t in range(trials):
            s_int = rng.integers(1, N)
            secret = format(s_int, f"0{n}b")
            oracle = build_oracle_from_secret(secret)
            t0 = time.time()
            run_simons_algorithm(oracle, n)
            times.append(time.time() - t0)

        mean_t = float(np.mean(times))
        if n not in results:
            results[n] = {"n": n}
        results[n]["simon_basic_s"] = mean_t
        print(f"    n={n}: {mean_t:.4f}s")

    # Even-Mansour: truth-table oracle, expensive at large n
    print("  Even-Mansour attack (truth-table oracle):")
    for n in [3, 4, 5, 6]:
        trials = 3
        N = 1 << n
        rng = np.random.default_rng(42)
        times = []
        for t in range(trials):
            k1, k2 = int(rng.integers(0, N)), int(rng.integers(0, N))
            cipher = EvenMansourCipher(n_bits=n, k1=k1, k2=k2, perm_seed=42)
            t0 = time.time()
            attack_even_mansour(cipher)
            times.append(time.time() - t0)

        mean_t = float(np.mean(times))
        if n not in results:
            results[n] = {"n": n}
        results[n]["even_mansour_s"] = mean_t
        print(f"    n={n}: {mean_t:.4f}s")

    _ensure_results_dir()
    with open(RESULTS_DIR / "timing_curves.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"  -> Saved to {RESULTS_DIR / 'timing_curves.json'}")
    print()
    return results


# ── Experiment 6: Hardware Noise Success Across Profiles ──────────────

def experiment_hardware_noise():
    """Success rate across hardware noise profiles."""
    from src.hardware_noise import (
        run_simon_noisy_hardware,
        IBM_HERON, NISQ_GENERIC, FUTURE_DEVICE,
    )

    print("=" * 70)
    print("EXPERIMENT 6: Hardware Noise — Success Across Profiles")
    print("=" * 70)

    configs = [(3, 30), (4, 20), (5, 10)]
    profiles = [FUTURE_DEVICE, IBM_HERON, NISQ_GENERIC]
    results = {}

    for n, trials in configs:
        N = 1 << n
        results[n] = {}

        for profile in profiles:
            rng = np.random.default_rng(42)
            successes = 0
            valid_fracs = []
            for t in range(trials):
                s_int = rng.integers(1, N)
                secret = format(s_int, f"0{n}b")
                result = run_simon_noisy_hardware(
                    secret, profile=profile,
                    n_shots=512, n_rounds=4 * n,
                )
                if result["success"]:
                    successes += 1
                valid_fracs.append(result["fraction_valid"])

            rate = successes / trials
            mean_valid = float(np.mean(valid_fracs))
            results[n][profile.name] = {
                "success_rate": rate,
                "mean_valid_fraction": mean_valid,
                "n_trials": trials,
            }
            print(f"  n={n}, {profile.name}: success={rate:.0%}, valid_eqs={mean_valid:.0%}")

    _ensure_results_dir()
    with open(RESULTS_DIR / "hardware_noise_profiles.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"  -> Saved to {RESULTS_DIR / 'hardware_noise_profiles.json'}")
    print()
    return results


# ── Experiment 7: Rank Convergence Curves ─────────────────────────────

def experiment_rank_convergence():
    """GF(2) rank growth with each query — convergence speed."""
    from src.simons_algorithm import build_oracle_from_secret, _sample_y_bits, _rank_gf2

    print("=" * 70)
    print("EXPERIMENT 7: Rank Convergence Curves")
    print("=" * 70)

    configs = [(3, 100), (4, 100), (5, 60), (6, 30), (7, 10), (8, 5)]
    max_queries = 30
    results = {}

    for n, trials in configs:
        N = 1 << n
        rng = np.random.default_rng(42)
        _flush(f"  n={n} ({trials} trials): ")

        solved_by_query = np.zeros(max_queries + 1)
        rank_at_query = np.zeros((trials, max_queries + 1))

        for t in range(trials):
            s_int = rng.integers(1, N)
            secret = format(s_int, f"0{n}b")
            oracle = build_oracle_from_secret(secret)

            equations = []
            solved = False
            for q in range(1, max_queries + 1):
                y_bits = _sample_y_bits(oracle, n)
                if not all(b == 0 for b in y_bits):
                    equations.append(y_bits)

                if equations:
                    rank = _rank_gf2(equations, n)
                    rank_at_query[t, q] = rank
                    if rank >= n - 1 and not solved:
                        solved = True
                        for qq in range(q, max_queries + 1):
                            solved_by_query[qq] += 1

        fraction_solved = solved_by_query / trials
        mean_rank = np.mean(rank_at_query, axis=0)

        row = {}
        for q in range(1, max_queries + 1):
            row[q] = {
                "fraction_solved": float(fraction_solved[q]),
                "mean_rank": float(mean_rank[q]),
            }
        results[n] = {"data": row, "n_trials": trials}

        q50 = next((q for q in range(1, max_queries + 1) if fraction_solved[q] >= 0.5), None)
        q90 = next((q for q in range(1, max_queries + 1) if fraction_solved[q] >= 0.9), None)
        q100 = next((q for q in range(1, max_queries + 1) if fraction_solved[q] >= 1.0), None)
        print(f"50%@q={q50}, 90%@q={q90}, 100%@q={q100}")

    _ensure_results_dir()
    with open(RESULTS_DIR / "rank_convergence.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"  -> Saved to {RESULTS_DIR / 'rank_convergence.json'}")
    print()
    return results


# ── Summary Table Generator ───────────────────────────────────────────

def generate_summary_tables():
    """Read all results and print formatted summary tables."""
    print()
    print("=" * 70)
    print("SUMMARY TABLES")
    print("=" * 70)
    print()

    # Table 1: Success rates
    path = RESULTS_DIR / "success_rate_vs_n.json"
    if path.exists():
        with open(path) as f:
            data = json.load(f)
        print("Table 1: Attack Success Rate by Key Size")
        print(f"  {'n':>3}  {'Trials':>6}  {'Simon':>7}  {'EM':>7}  {'Feistel':>8}  {'Slide':>7}")
        print(f"  {'─'*3}  {'─'*6}  {'─'*7}  {'─'*7}  {'─'*8}  {'─'*7}")
        for n_str, row in sorted(data.items(), key=lambda x: int(x[0])):
            f3 = f"{row['feistel_3round']:.0%}" if row.get('feistel_3round') is not None else "N/A"
            print(f"  {row['n']:>3}  {row['n_trials']:>6}  "
                  f"{row['simon_basic']:>6.0%}  {row['even_mansour']:>6.0%}  "
                  f"{f3:>8}  {row['slide_5rounds']:>6.0%}")
        print()

    # Table 2: Query complexity
    path = RESULTS_DIR / "query_complexity.json"
    if path.exists():
        with open(path) as f:
            data = json.load(f)
        print("Table 2: Query Complexity (queries to reach rank n-1)")
        print(f"  {'n':>3}  {'Mean':>7}  {'Ratio':>7}  {'Median':>7}  {'Min':>4}  {'Max':>4}")
        print(f"  {'─'*3}  {'─'*7}  {'─'*7}  {'─'*7}  {'─'*4}  {'─'*4}")
        for n_str, row in sorted(data.items(), key=lambda x: int(x[0])):
            print(f"  {row['n']:>3}  {row['mean_queries']:>7.1f}  "
                  f"{row['ratio_to_n']:>6.2f}n  "
                  f"{row['median_queries']:>7.0f}  "
                  f"{row['min_queries']:>4}  {row['max_queries']:>4}")
        print()

    # Table 3: Noise phase transition
    path = RESULTS_DIR / "noise_phase_transition.json"
    if path.exists():
        with open(path) as f:
            data = json.load(f)
        print("Table 3: Noise Phase Transition (success rate)")
        eps_keys = sorted(set(k for v in data.values() for k in v.keys()), key=float)
        n_keys = sorted(data.keys(), key=int)
        header = f"  {'eps':>5}" + "".join(f"  {'n='+n:>6}" for n in n_keys)
        print(header)
        print(f"  {'─'*5}" + "".join(f"  {'─'*6}" for _ in n_keys))
        for eps in eps_keys:
            row = f"  {float(eps):>4.0%}"
            for n in n_keys:
                val = data[n].get(eps, 0)
                row += f"  {val:>5.0%} "
            print(row)
        print()

    # Table 4: Timing
    path = RESULTS_DIR / "timing_curves.json"
    if path.exists():
        with open(path) as f:
            data = json.load(f)
        print("Table 4: Wall-Clock Time (seconds)")
        print(f"  {'n':>3}  {'Simon basic':>12}  {'EM attack':>12}")
        print(f"  {'─'*3}  {'─'*12}  {'─'*12}")
        for n_str in sorted(data.keys(), key=int):
            row = data[n_str]
            simon = f"{row.get('simon_basic_s', 0):>12.4f}"
            em = f"{row.get('even_mansour_s', 0):>12.4f}" if 'even_mansour_s' in row else "         N/A"
            print(f"  {int(n_str):>3}  {simon}  {em}")
        print()

    # Table 5: Rank convergence
    path = RESULTS_DIR / "rank_convergence.json"
    if path.exists():
        with open(path) as f:
            data = json.load(f)
        print("Table 5: Rank Convergence (queries to solve)")
        for n_str in sorted(data.keys(), key=int):
            n = int(n_str)
            qdata = data[n_str].get("data", data[n_str])
            q50 = next((int(q) for q, v in sorted(qdata.items(), key=lambda x: int(x[0]))
                        if isinstance(v, dict) and v.get("fraction_solved", 0) >= 0.5), "—")
            q90 = next((int(q) for q, v in sorted(qdata.items(), key=lambda x: int(x[0]))
                        if isinstance(v, dict) and v.get("fraction_solved", 0) >= 0.9), "—")
            q99 = next((int(q) for q, v in sorted(qdata.items(), key=lambda x: int(x[0]))
                        if isinstance(v, dict) and v.get("fraction_solved", 0) >= 0.99), "—")
            print(f"  n={n}: 50% at q={q50}, 90% at q={q90}, 99% at q={q99}")
        print()

    # Table 6: Hardware noise
    path = RESULTS_DIR / "hardware_noise_profiles.json"
    if path.exists():
        with open(path) as f:
            data = json.load(f)
        print("Table 6: Hardware Noise — Success Rate")
        profiles = sorted(set(p for v in data.values() for p in v.keys()))
        for n_str in sorted(data.keys(), key=int):
            print(f"  n={int(n_str)}:")
            for p in profiles:
                info = data[n_str].get(p, {})
                sr = info.get("success_rate", 0)
                vf = info.get("mean_valid_fraction", 0)
                print(f"    {p}: success={sr:.0%}, valid_equations={vf:.0%}")
        print()

    # Table 7: Slide round-independence
    path = RESULTS_DIR / "slide_round_independence.json"
    if path.exists():
        with open(path) as f:
            data = json.load(f)
        print("Table 7: Slide Attack — Success Rate vs Round Count")
        n_keys = sorted(data.keys(), key=int)
        r_keys = sorted(set(int(r) for v in data.values() for r in v.keys()))
        header = f"  {'rounds':>6}" + "".join(f"  {'n='+n:>6}" for n in n_keys)
        print(header)
        print(f"  {'─'*6}" + "".join(f"  {'─'*6}" for _ in n_keys))
        for r in r_keys:
            row = f"  {r:>6}"
            for n in n_keys:
                val = data[n].get(str(r), {}).get("success_rate", 0)
                row += f"  {val:>5.0%} "
            print(row)
        print()


# ── Main ──────────────────────────────────────────────────────────────

def main():
    overall_t0 = time.time()
    print()
    print("Quantum Cryptanalysis — Comprehensive Data Collection")
    print("=" * 70)
    print()

    experiments = [
        ("1", "Success rate vs key size", experiment_success_rate_vs_n),
        ("2", "Query complexity", experiment_query_complexity),
        ("3", "Noise phase transition", experiment_noise_phase_transition),
        ("4", "Slide round-independence", experiment_slide_round_independence),
        ("5", "Wall-clock timing", experiment_timing_curves),
        ("6", "Hardware noise profiles", experiment_hardware_noise),
        ("7", "Rank convergence", experiment_rank_convergence),
    ]

    selected = sys.argv[1:] if len(sys.argv) > 1 else [e[0] for e in experiments]

    for exp_id, name, func in experiments:
        if exp_id in selected:
            print(f"\n[{exp_id}/7] {name}")
            t0 = time.time()
            try:
                func()
            except Exception as e:
                print(f"  ERROR: {e}")
                import traceback
                traceback.print_exc()
            elapsed = time.time() - t0
            print(f"  [{name}: {elapsed:.1f}s]")

    generate_summary_tables()

    total = time.time() - overall_t0
    print(f"\nTotal: {total:.1f}s ({total/60:.1f} min)")
    print(f"Results: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
