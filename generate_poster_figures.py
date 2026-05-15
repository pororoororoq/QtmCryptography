"""
Generate all poster figures for the quantum cryptanalysis science fair poster.
Each figure is saved as a high-resolution PNG suitable for printing.

Usage:
    python generate_poster_figures.py
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path

RESULTS = Path("experiments/results")
OUT = Path("poster_figures")
OUT.mkdir(exist_ok=True)

COLORS = {
    "dark":   "#3D4028",
    "sage":   "#A5A685",
    "mint":   "#CDDBCE",
    "teal":   "#90CBC5",
    "navy":   "#013440",
    "coral":  "#F96C77",
}

def style_ax(ax, title, xlabel, ylabel):
    ax.set_title(title, fontsize=16, pad=12)
    ax.set_xlabel(xlabel, fontsize=13)
    ax.set_ylabel(ylabel, fontsize=13)
    ax.tick_params(labelsize=11)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


# ── Figure 1: Noise Phase Transition (the "cliff" plot) ─────────────
def fig_noise_phase_transition():
    with open(RESULTS / "noise_phase_transition.json") as f:
        data = json.load(f)

    fig, ax = plt.subplots(figsize=(7, 5))

    markers = ["o", "s", "D"]
    colors = [COLORS["navy"], COLORS["teal"], COLORS["sage"]]
    for i, (n, rates) in enumerate(sorted(data.items(), key=lambda x: int(x[0]))):
        eps = [float(e) * 100 for e in sorted(rates.keys(), key=float)]
        success = [rates[e] * 100 for e in sorted(rates.keys(), key=float)]
        ax.plot(eps, success, marker=markers[i], color=colors[i],
                linewidth=2.5, markersize=8, label=f"n = {n} bits",
                zorder=3)

    ax.axvspan(30, 42, alpha=0.15, color=COLORS["coral"], zorder=0)
    ax.annotate("Phase\ntransition", xy=(36, 72), fontsize=11,
                color=COLORS["coral"], ha="center", fontweight="normal")

    ax.axhline(y=50, color=COLORS["sage"], linestyle=":", linewidth=1, alpha=0.5)
    ax.text(2, 52, "Random guessing", fontsize=9, color=COLORS["sage"])

    style_ax(ax, "Noise Resilience: Sharp Phase Transition",
             "Measurement Noise Rate (%)", "Key Recovery Success (%)")
    ax.set_ylim(45, 102)
    ax.set_xlim(-1, 42)
    ax.legend(fontsize=12, loc="lower left")
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d%%'))
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d%%'))

    fig.tight_layout()
    fig.savefig(OUT / "1_noise_phase_transition.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  [1] Noise phase transition")


# ── Figure 2: Slide Attack Round-Independence ────────────────────────
def fig_slide_round_independence():
    with open(RESULTS / "slide_round_independence.json") as f:
        data = json.load(f)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))

    for n_str, results in sorted(data.items(), key=lambda x: int(x[0])):
        rounds = sorted(results.keys(), key=int)
        r_vals = [int(r) for r in rounds]
        success = [results[r]["success_rate"] * 100 for r in rounds]
        times = [results[r]["mean_time_s"] for r in rounds]
        color = COLORS["navy"] if n_str == "3" else COLORS["teal"]
        marker = "o" if n_str == "3" else "s"

        ax1.plot(r_vals, success, marker=marker, color=color,
                 linewidth=2.5, markersize=8, label=f"n = {n_str} bits")
        ax2.plot(r_vals, times, marker=marker, color=color,
                 linewidth=2.5, markersize=8, label=f"n = {n_str} bits")

    style_ax(ax1, "Success Rate vs Round Count",
             "Number of Cipher Rounds", "Key Recovery Success (%)")
    ax1.set_xscale("log")
    ax1.set_ylim(0, 115)
    ax1.set_xticks([1, 2, 5, 10, 20, 50, 100])
    ax1.get_xaxis().set_major_formatter(ticker.ScalarFormatter())
    ax1.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d%%'))
    ax1.legend(fontsize=11)

    ax1.annotate("Flat line = round count\nis irrelevant!",
                 xy=(50, 60), xytext=(10, 30),
                 fontsize=10, color=COLORS["navy"],
                 arrowprops=dict(arrowstyle="->", color=COLORS["navy"]),
                 fontweight="normal")

    style_ax(ax2, "Attack Time vs Round Count",
             "Number of Cipher Rounds", "Execution Time (seconds)")
    ax2.set_xscale("log")
    ax2.set_xticks([1, 2, 5, 10, 20, 50, 100])
    ax2.get_xaxis().set_major_formatter(ticker.ScalarFormatter())
    ax2.legend(fontsize=11)

    fig.suptitle("Quantum Slide Attack: Round Count is Irrelevant",
                 fontsize=17, fontweight="normal", y=1.03)
    fig.tight_layout()
    fig.savefig(OUT / "2_slide_round_independence.png", dpi=300,
                bbox_inches="tight")
    plt.close(fig)
    print("  [2] Slide round-independence")


# ── Figure 3: Query Complexity ───────────────────────────────────────
def fig_query_complexity():
    with open(RESULTS / "query_complexity.json") as f:
        data = json.load(f)

    fig, ax = plt.subplots(figsize=(7, 5))

    ns = sorted(data.keys(), key=int)
    n_vals = [int(n) for n in ns]
    means = [data[n]["mean_queries"] for n in ns]
    stds = [data[n]["std_queries"] for n in ns]
    theoretical = [int(n) - 1 for n in ns]

    x = np.arange(len(n_vals))
    width = 0.35

    bars = ax.bar(x - width/2, means, width, yerr=stds, capsize=5,
                  color=COLORS["navy"], alpha=0.85, label="Measured (mean ± std)",
                  zorder=3, edgecolor="white", linewidth=0.5)
    ax.bar(x + width/2, theoretical, width,
           color=COLORS["sage"], alpha=0.5, label="Theoretical min (n−1)",
           zorder=3, edgecolor="white", linewidth=0.5)

    for i, (m, n) in enumerate(zip(means, n_vals)):
        ax.text(i - width/2, m + stds[i] + 0.3, f"{m/n:.2f}n",
                ha="center", fontsize=9, fontweight="normal", color=COLORS["navy"])

    ax.set_xticks(x)
    ax.set_xticklabels([f"n={n}" for n in n_vals])
    style_ax(ax, "Oracle Queries to Recover Secret Key",
             "Key Size (bits)", "Number of Queries")
    ax.legend(fontsize=11)

    fig.tight_layout()
    fig.savefig(OUT / "3_query_complexity.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  [3] Query complexity")


# ── Figure 4: Timing Curves (log scale) ──────────────────────────────
def fig_timing_curves():
    with open(RESULTS / "timing_curves.json") as f:
        data = json.load(f)

    fig, ax = plt.subplots(figsize=(7, 5))

    ns_simon = []
    times_simon = []
    ns_em = []
    times_em = []

    for n_str in sorted(data.keys(), key=int):
        entry = data[n_str]
        n = int(n_str)
        if "simon_basic_s" in entry:
            ns_simon.append(n)
            times_simon.append(entry["simon_basic_s"])
        if "even_mansour_s" in entry:
            ns_em.append(n)
            times_em.append(entry["even_mansour_s"])

    ax.semilogy(ns_simon, times_simon, "o-", color=COLORS["navy"],
                linewidth=2.5, markersize=8, label="Simon's (basic oracle)")
    ax.semilogy(ns_em, times_em, "s-", color=COLORS["coral"],
                linewidth=2.5, markersize=8, label="Even-Mansour (truth-table)")

    for n, t in zip(ns_simon, times_simon):
        label = f"{t:.2f}s" if t >= 0.1 else f"{t*1000:.0f}ms"
        ax.annotate(label, (n, t), textcoords="offset points",
                    xytext=(10, 5), fontsize=9, color=COLORS["navy"])
    for n, t in zip(ns_em, times_em):
        label = f"{t:.1f}s" if t >= 1 else f"{t:.2f}s"
        ax.annotate(label, (n, t), textcoords="offset points",
                    xytext=(10, -15), fontsize=9, color=COLORS["coral"])

    style_ax(ax, "Simulation Time Scales Exponentially",
             "Key Size n (bits)", "Wall-Clock Time (seconds, log scale)")
    ax.legend(fontsize=11)
    ax.set_xticks(range(3, 9))
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUT / "4_timing_curves.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  [4] Timing curves")


# ── Figure 5: Rank Convergence (S-curves) ────────────────────────────
def fig_rank_convergence():
    with open(RESULTS / "rank_convergence.json") as f:
        data = json.load(f)

    fig, ax = plt.subplots(figsize=(7, 5))

    from matplotlib.colors import LinearSegmentedColormap
    palette = [COLORS["navy"], COLORS["teal"], COLORS["mint"], COLORS["sage"], COLORS["dark"]]
    cmap = LinearSegmentedColormap.from_list("poster", palette, N=256)
    n_keys = sorted(data.keys(), key=int)
    colors_list = [cmap(i / (len(n_keys) - 1)) for i in range(len(n_keys))]

    for idx, n_str in enumerate(n_keys):
        entry = data[n_str]["data"]
        queries = []
        fracs = []
        for q_str in sorted(entry.keys(), key=lambda x: int(x.split("-")[0])):
            q = int(q_str.split("-")[0])
            if q > 20:
                break
            queries.append(q)
            fracs.append(entry[q_str]["fraction_solved"] * 100)

        ax.plot(queries, fracs, "o-", color=colors_list[idx],
                linewidth=2, markersize=5, label=f"n = {n_str}")

    ax.axhline(y=50, color=COLORS["sage"], linestyle=":", linewidth=1, alpha=0.5)
    ax.axhline(y=99, color=COLORS["teal"], linestyle="--", linewidth=1, alpha=0.4)
    ax.text(18, 52, "50%", fontsize=9, color=COLORS["sage"])
    ax.text(18, 95, "99%", fontsize=9, color=COLORS["teal"])

    style_ax(ax, "How Quickly Does Simon's Algorithm Converge?",
             "Number of Oracle Queries", "Trials Solved (%)")
    ax.set_ylim(-2, 105)
    ax.set_xlim(0, 20)
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d%%'))
    ax.legend(fontsize=10, ncol=2, loc="lower right")

    fig.tight_layout()
    fig.savefig(OUT / "5_rank_convergence.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  [5] Rank convergence")


# ── Figure 6: Attack Success Rate (grouped bars) ────────────────────
def fig_success_rates():
    with open(RESULTS / "success_rate_vs_n.json") as f:
        data = json.load(f)

    fig, ax = plt.subplots(figsize=(7, 5))

    attacks = ["simon_basic", "even_mansour", "feistel_3round", "slide_5rounds"]
    labels = ["Simon's", "Even-Mansour", "3-Round Feistel", "Slide Attack"]
    atk_colors = [COLORS["navy"], COLORS["teal"], COLORS["sage"], COLORS["coral"]]

    ns = ["3", "4", "5"]
    x = np.arange(len(ns))
    width = 0.18

    for i, (atk, label, color) in enumerate(zip(attacks, labels, atk_colors)):
        vals = []
        for n in ns:
            v = data[n].get(atk)
            vals.append(v * 100 if v is not None else 0)
        offset = (i - 1.5) * width
        bars = ax.bar(x + offset, vals, width, label=label, color=color,
                      alpha=0.85, edgecolor="white", linewidth=0.5, zorder=3)
        for j, v in enumerate(vals):
            if data[ns[j]].get(atk) is None:
                ax.text(x[j] + offset, 3, "N/A", ha="center", fontsize=8,
                        color=COLORS["sage"], rotation=90)
            elif v < 100:
                ax.text(x[j] + offset, v + 2, f"{v:.0f}%", ha="center",
                        fontsize=9, fontweight="normal")

    ax.set_xticks(x)
    ax.set_xticklabels([f"n = {n} bits" for n in ns], fontsize=12)
    style_ax(ax, "All Attacks Achieve 100% Success at n ≥ 4",
             "", "Key Recovery Success (%)")
    ax.set_ylim(0, 115)
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d%%'))
    ax.legend(fontsize=10, ncol=2, loc="upper left")

    fig.tight_layout()
    fig.savefig(OUT / "6_success_rates.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  [6] Success rates")


# ── Figure 7: Simon vs Grover (exponential gap) ─────────────────────
def fig_simon_vs_grover():
    fig, ax = plt.subplots(figsize=(7, 5))

    n_vals = [4, 8, 16, 32, 64, 128]
    simon_queries = n_vals.copy()
    grover_queries = [int(np.pi / 4 * 2 ** (n / 2)) for n in n_vals]
    classical = [2 ** n for n in n_vals]

    ax.semilogy(n_vals, classical, "^--", color=COLORS["sage"],
                linewidth=2, markersize=8, label="Classical brute force  O(2ⁿ)",
                alpha=0.6)
    ax.semilogy(n_vals, grover_queries, "s-", color=COLORS["teal"],
                linewidth=2.5, markersize=8, label="Grover's search  O(2^{n/2})")
    ax.semilogy(n_vals, simon_queries, "o-", color=COLORS["navy"],
                linewidth=2.5, markersize=10, label="Simon's algorithm  O(n)")

    ax.fill_between(n_vals, simon_queries, grover_queries,
                    alpha=0.1, color=COLORS["navy"])
    ax.annotate("Exponential\ngap!",
                xy=(64, 1e5), fontsize=13, fontweight="normal",
                color=COLORS["coral"], ha="center")

    style_ax(ax, "Simon's Algorithm vs Classical & Grover",
             "Key Size n (bits)", "Oracle Queries (log scale)")
    ax.legend(fontsize=10, loc="upper left")
    ax.set_xticks(n_vals)
    ax.set_xticklabels([str(n) for n in n_vals])
    ax.grid(axis="y", alpha=0.2)

    fig.tight_layout()
    fig.savefig(OUT / "7_simon_vs_grover.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  [7] Simon vs Grover")


# ── Figure 8: Resource Estimates (bar chart) ─────────────────────────
def fig_resource_estimates():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))

    targets = ["PRINCE\n(n=64)", "AES-128\n(n=128)", "AES-256\n(n=256)"]
    physical_qubits = [371_000, 802_000, 1_580_000]
    t_gates = [13.1e6, 104.9e6, 838.9e6]

    bars1 = ax1.bar(targets, [q / 1e6 for q in physical_qubits],
                    color=[COLORS["teal"], COLORS["navy"], COLORS["dark"]],
                    alpha=0.85, edgecolor="white", linewidth=0.5, zorder=3)
    for bar, q in zip(bars1, physical_qubits):
        label = f"~{q/1e6:.1f}M" if q >= 1e6 else f"~{q/1e3:.0f}K"
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                 label, ha="center", fontsize=11, fontweight="normal")

    style_ax(ax1, "Physical Qubits Required",
             "", "Millions of Physical Qubits")

    bars2 = ax2.bar(targets, [t / 1e6 for t in t_gates],
                    color=[COLORS["teal"], COLORS["navy"], COLORS["dark"]],
                    alpha=0.85, edgecolor="white", linewidth=0.5, zorder=3)
    for bar, t in zip(bars2, t_gates):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                 f"{t/1e6:.0f}M", ha="center", fontsize=11, fontweight="normal")

    style_ax(ax2, "T-Gate Count",
             "", "Millions of T-Gates")

    fig.suptitle("Fault-Tolerant Resources for Real-World Cipher Attacks",
                 fontsize=16, fontweight="normal", y=1.03)
    fig.tight_layout()
    fig.savefig(OUT / "8_resource_estimates.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  [8] Resource estimates")


# ── Figure 9: PRINCE Security Reduction ──────────────────────────────
def fig_prince_security():
    fig, ax = plt.subplots(figsize=(7, 5))

    methods = ["Classical\nexhaustive", "Classical\nmeet-in-middle",
               "Quantum\nGrover", "Quantum\nGrover-meet-Simon"]
    bits = [127, 64, 64, 37]
    colors = [COLORS["sage"], COLORS["sage"], COLORS["teal"], COLORS["coral"]]

    bars = ax.bar(methods, bits, color=colors, alpha=0.85,
                  edgecolor="white", linewidth=0.5, zorder=3, width=0.6)

    for bar, b in zip(bars, bits):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f"{b} bits", ha="center", fontsize=13, fontweight="normal")

    ax.annotate("", xy=(3, 40), xytext=(0, 127),
                arrowprops=dict(arrowstyle="->,head_width=0.4",
                                color=COLORS["coral"], linewidth=2.5))
    ax.text(1.5, 88, "90-bit\nreduction!", fontsize=14,
            fontweight="normal", color=COLORS["coral"], ha="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=COLORS["coral"], alpha=0.9))

    style_ax(ax, "PRINCE-64 Cipher: Security Under Different Attacks",
             "", "Effective Security (bits)")
    ax.set_ylim(0, 145)

    fig.tight_layout()
    fig.savefig(OUT / "9_prince_security.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  [9] PRINCE security reduction")


# ── Figure 10: Attack Overview Diagram ───────────────────────────────
def fig_attack_overview():
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    box_style = dict(boxstyle="round,pad=0.5", facecolor=COLORS["mint"],
                     edgecolor=COLORS["navy"], linewidth=2)
    target_style = dict(boxstyle="round,pad=0.5", facecolor="#FDE8E9",
                        edgecolor=COLORS["coral"], linewidth=2)
    result_style = dict(boxstyle="round,pad=0.4", facecolor=COLORS["mint"],
                        edgecolor=COLORS["teal"], linewidth=2)

    ax.text(5, 5.5, "Simon's Algorithm", fontsize=18, ha="center",
            fontweight="normal", color=COLORS["dark"],
            bbox=dict(boxstyle="round,pad=0.6", facecolor=COLORS["mint"],
                      edgecolor=COLORS["navy"], linewidth=3))

    targets = [
        (1.5, 3.5, "Even-Mansour\nE(x) = P(x⊕k₁)⊕k₂"),
        (5.0, 3.5, "3-Round Feistel\nF(x) = S[x⊕k]"),
        (8.5, 3.5, "Slide Cipher\nE(x) = Fₖʳ(x)"),
    ]
    for x, y, text in targets:
        ax.text(x, y, text, fontsize=11, ha="center", va="center",
                bbox=target_style)
        ax.annotate("", xy=(x, 4.0), xytext=(5, 5.05),
                    arrowprops=dict(arrowstyle="->,head_width=0.3",
                                    color=COLORS["navy"], linewidth=1.5))

    reductions = [
        (1.5, 1.8, "f(x) = E(x)⊕P(x)\nperiod s = k₁"),
        (5.0, 1.8, "f(x) = E_L(x,0)⊕E_L(x,1)\nperiod s = S[k]⊕S[1⊕k]"),
        (8.5, 1.8, "f(x) = Fₖ(x)⊕P(x)\nperiod s = k"),
    ]
    for (tx, ty, _), (rx, ry, rtext) in zip(targets, reductions):
        ax.annotate("", xy=(rx, ry + 0.55), xytext=(tx, ty - 0.55),
                    arrowprops=dict(arrowstyle="->,head_width=0.2",
                                    color=COLORS["teal"], linewidth=1.5))
        ax.text(rx, ry, rtext, fontsize=9, ha="center", va="center",
                bbox=result_style, family="monospace")

    ax.text(5, 0.5, "All recover the secret key in O(n) quantum queries",
            fontsize=14, ha="center", fontweight="normal", color=COLORS["navy"],
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                      edgecolor=COLORS["navy"], linewidth=2, alpha=0.9))

    fig.tight_layout()
    fig.savefig(OUT / "10_attack_overview.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  [10] Attack overview diagram")


# ── Main ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating poster figures...")
    print()
    fig_noise_phase_transition()
    fig_slide_round_independence()
    fig_query_complexity()
    fig_timing_curves()
    fig_rank_convergence()
    fig_success_rates()
    fig_simon_vs_grover()
    fig_resource_estimates()
    fig_prince_security()
    fig_attack_overview()
    print()
    print(f"Done! {len(list(OUT.glob('*.png')))} figures saved to {OUT}/")
    print()
    print("Recommended poster layout:")
    print("  INTRODUCTION:  Fig 10 (attack overview), Fig 7 (Simon vs Grover)")
    print("  METHODOLOGY:   Fig 10 (attack overview)")
    print("  RESULTS:       Fig 6 (success rates), Fig 1 (noise cliff),")
    print("                 Fig 2 (slide independence), Fig 5 (convergence)")
    print("  CONCLUSION:    Fig 9 (PRINCE security), Fig 8 (resource estimates)")
