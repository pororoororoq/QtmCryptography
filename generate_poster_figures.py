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


# ── Figure 11: Simon's Algorithm Quantum Circuit ───────────────────
def fig_simons_circuit():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(-0.5, 11)
    ax.set_ylim(-0.5, 7.5)
    ax.axis("off")
    ax.set_aspect("equal")

    n = 3
    wire_y_input = [6, 5, 4]
    wire_y_output = [2, 1, 0]
    all_wires = wire_y_input + wire_y_output
    x_start, x_end = 0.5, 10

    for y in all_wires:
        ax.plot([x_start, x_end], [y, y], color=COLORS["dark"], linewidth=1, zorder=1)

    for i, y in enumerate(wire_y_input):
        ax.text(0, y, f"|0⟩", fontsize=13, ha="right", va="center",
                family="serif", color=COLORS["dark"])
    for i, y in enumerate(wire_y_output):
        ax.text(0, y, f"|0⟩", fontsize=13, ha="right", va="center",
                family="serif", color=COLORS["dark"])

    ax.text(-0.3, 6.8, "input", fontsize=9, ha="right", va="center",
            color=COLORS["sage"], style="italic")
    ax.text(-0.3, 2.8, "output", fontsize=9, ha="right", va="center",
            color=COLORS["sage"], style="italic")

    h_x = 1.5
    h_size = 0.35
    for y in wire_y_input:
        rect = plt.Rectangle((h_x - h_size, y - h_size), 2*h_size, 2*h_size,
                              facecolor=COLORS["mint"], edgecolor=COLORS["navy"],
                              linewidth=1.5, zorder=3)
        ax.add_patch(rect)
        ax.text(h_x, y, "H", fontsize=13, ha="center", va="center",
                color=COLORS["navy"], family="serif")

    oracle_x1, oracle_x2 = 3.5, 5.5
    oracle_rect = plt.Rectangle((oracle_x1, -0.4), oracle_x2 - oracle_x1, 6.8,
                                 facecolor="#FDE8E9", edgecolor=COLORS["coral"],
                                 linewidth=2, zorder=2, alpha=0.9)
    ax.add_patch(oracle_rect)
    ax.text((oracle_x1 + oracle_x2)/2, 3, "Oracle\nUf", fontsize=15,
            ha="center", va="center", color=COLORS["coral"], family="serif")
    ax.text((oracle_x1 + oracle_x2)/2, 3.0 + 1.5,
            "|x⟩|y⟩ → |x⟩|y⊕f(x)⟩", fontsize=9,
            ha="center", va="center", color=COLORS["dark"], family="serif")

    h2_x = 7.0
    for y in wire_y_input:
        rect = plt.Rectangle((h2_x - h_size, y - h_size), 2*h_size, 2*h_size,
                              facecolor=COLORS["mint"], edgecolor=COLORS["navy"],
                              linewidth=1.5, zorder=3)
        ax.add_patch(rect)
        ax.text(h2_x, y, "H", fontsize=13, ha="center", va="center",
                color=COLORS["navy"], family="serif")

    meter_x = 8.8
    for y in wire_y_input:
        arc = plt.Circle((meter_x, y - 0.1), 0.3, fill=False,
                          edgecolor=COLORS["navy"], linewidth=1.5, zorder=3)
        ax.add_patch(arc)
        ax.plot([meter_x, meter_x + 0.15], [y - 0.1, y + 0.25],
                color=COLORS["navy"], linewidth=1.5, zorder=4)
        ax.plot([meter_x - 0.3, meter_x + 0.3], [y - 0.4, y - 0.4],
                color=COLORS["navy"], linewidth=1.5, zorder=4)

    ax.text(10.3, 5, "y", fontsize=14, ha="center", va="center",
            color=COLORS["navy"], family="serif")
    ax.text(10.3, 4.3, "(y·s = 0)", fontsize=10, ha="center", va="center",
            color=COLORS["sage"], family="serif")

    ax.annotate("", xy=(3.2, 3), xytext=(2.0, 3),
                arrowprops=dict(arrowstyle="->,head_width=0.15",
                                color=COLORS["sage"], linewidth=1))
    ax.text(2.6, 3.4, "superposition\nof all x", fontsize=8, ha="center",
            color=COLORS["sage"], style="italic")

    ax.text(5.5, 7.2, "Simon's Algorithm Quantum Circuit (n = 3)",
            fontsize=16, ha="center", va="center", color=COLORS["dark"])

    fig.tight_layout()
    fig.savefig(OUT / "11_simons_circuit.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  [11] Simon's circuit diagram")


# ── Figure 12: Simon's Algorithm Worked Example ───────────────────
def fig_simons_worked_example():
    fig, axes = plt.subplots(1, 3, figsize=(14, 5.5),
                              gridspec_kw={"width_ratios": [1, 1, 1]})

    ax1, ax2, ax3 = axes
    for ax in axes:
        ax.axis("off")

    # Panel 1: The hidden function truth table
    ax1.set_xlim(0, 5.5)
    ax1.set_ylim(-0.5, 9)
    ax1.text(2, 8.5, "Step 1: Hidden Function", fontsize=13,
             ha="center", color=COLORS["dark"])
    ax1.text(2, 7.8, "Secret s = 101 (unknown)", fontsize=10,
             ha="center", color=COLORS["coral"])

    table_data = [
        ("x", "f(x)"),
        ("000", "010"),
        ("001", "110"),
        ("010", "000"),
        ("011", "100"),
        ("100", "010"),
        ("101", "110"),
        ("110", "000"),
        ("111", "100"),
    ]
    for i, (x_val, fx_val) in enumerate(table_data):
        y = 7.0 - i * 0.75
        if i == 0:
            ax1.text(1.2, y, x_val, fontsize=11, ha="center", va="center",
                     color=COLORS["dark"], family="monospace")
            ax1.text(2.8, y, fx_val, fontsize=11, ha="center", va="center",
                     color=COLORS["dark"], family="monospace")
            ax1.plot([0.5, 3.5], [y - 0.35, y - 0.35], color=COLORS["dark"],
                     linewidth=1)
        else:
            highlight = (i - 1) < 4
            bg = COLORS["mint"] if highlight else "#FDE8E9"
            rect = plt.Rectangle((0.5, y - 0.3), 3, 0.6, facecolor=bg,
                                  edgecolor="none", alpha=0.5, zorder=0)
            ax1.add_patch(rect)
            ax1.text(1.2, y, x_val, fontsize=11, ha="center", va="center",
                     color=COLORS["navy"], family="monospace")
            ax1.text(2.8, y, fx_val, fontsize=11, ha="center", va="center",
                     color=COLORS["navy"], family="monospace")

    # Draw matching pairs with clean brackets
    pairs = [(1, 5), (2, 6), (3, 7), (4, 8)]
    bracket_xs = [4.0, 4.5, 5.0, 5.5]
    pair_labels = ["000→010", "001→110", "010→000", "011→100"]
    for (a, b), bx in zip(pairs, bracket_xs):
        ya = 7.0 - a * 0.75
        yb = 7.0 - b * 0.75
        ax1.plot([3.55, bx], [ya, ya], color=COLORS["coral"], linewidth=1.2)
        ax1.plot([3.55, bx], [yb, yb], color=COLORS["coral"], linewidth=1.2)
        ax1.plot([bx, bx], [ya, yb], color=COLORS["coral"], linewidth=1.2)

    ax1.text(2, -0.2, "f(x) = f(x ⊕ 101)  →  period s = 101", fontsize=9,
             ha="center", color=COLORS["coral"])

    # Panel 2: Quantum measurements → equations
    ax2.set_xlim(0, 5)
    ax2.set_ylim(-0.5, 9)
    ax2.text(2.5, 8.5, "Step 2: Measure", fontsize=13,
             ha="center", color=COLORS["dark"])
    ax2.text(2.5, 7.8, "Each y satisfies y · s = 0 mod 2", fontsize=10,
             ha="center", color=COLORS["sage"])

    measurements = [
        ("y₁ = 010", "0·s₁ + 1·s₂ + 0·s₃ = 0"),
        ("y₂ = 110", "1·s₁ + 1·s₂ + 0·s₃ = 0"),
        ("y₃ = 101", "1·s₁ + 0·s₂ + 1·s₃ = 0"),
    ]
    for i, (meas, eq) in enumerate(measurements):
        y = 6.5 - i * 2.0
        rect = plt.Rectangle((0.3, y - 0.5), 4.4, 1.6, facecolor=COLORS["mint"],
                              edgecolor=COLORS["teal"], linewidth=1.5,
                              alpha=0.6, zorder=0)
        ax2.add_patch(rect)
        ax2.text(2.5, y + 0.3, meas, fontsize=12, ha="center", va="center",
                 color=COLORS["navy"], family="monospace")
        ax2.text(2.5, y - 0.2, eq, fontsize=10, ha="center", va="center",
                 color=COLORS["dark"], family="monospace")

    ax2.annotate("", xy=(2.5, 1.3), xytext=(2.5, 2.2),
                 arrowprops=dict(arrowstyle="->,head_width=0.2",
                                 color=COLORS["navy"], linewidth=2))
    ax2.text(2.5, 0.7, "n−1 = 2 independent\nequations needed", fontsize=10,
             ha="center", color=COLORS["navy"])

    # Panel 3: GF(2) solution
    ax3.set_xlim(0, 5)
    ax3.set_ylim(-0.5, 9)
    ax3.text(2.5, 8.5, "Step 3: Solve over GF(2)", fontsize=13,
             ha="center", color=COLORS["dark"])

    # Matrix
    ax3.text(2.5, 7.3, "Gaussian Elimination mod 2:", fontsize=10,
             ha="center", color=COLORS["sage"])

    matrix_lines = [
        "⎡ 0 1 0 | 0 ⎤",
        "⎢ 1 1 0 | 0 ⎥",
        "⎣ 1 0 1 | 0 ⎦",
    ]
    for i, line in enumerate(matrix_lines):
        ax3.text(2.5, 6.4 - i * 0.55, line, fontsize=11, ha="center",
                 va="center", color=COLORS["navy"], family="monospace")

    ax3.annotate("", xy=(2.5, 4.6), xytext=(2.5, 5.0),
                 arrowprops=dict(arrowstyle="->,head_width=0.15",
                                 color=COLORS["navy"], linewidth=1.5))

    matrix_reduced = [
        "⎡ 1 0 1 | 0 ⎤",
        "⎢ 0 1 0 | 0 ⎥",
        "⎣ 0 0 0 | 0 ⎦",
    ]
    for i, line in enumerate(matrix_reduced):
        ax3.text(2.5, 4.2 - i * 0.55, line, fontsize=11, ha="center",
                 va="center", color=COLORS["navy"], family="monospace")

    ax3.text(2.5, 2.6, "Free variable: s₃ = 1", fontsize=10,
             ha="center", color=COLORS["dark"])
    ax3.text(2.5, 2.1, "Back-substitute: s₁ = 1, s₂ = 0", fontsize=10,
             ha="center", color=COLORS["dark"])

    result_rect = plt.Rectangle((0.6, 0.8), 3.8, 1.0,
                                 facecolor="#FDE8E9", edgecolor=COLORS["coral"],
                                 linewidth=2, zorder=2)
    ax3.add_patch(result_rect)
    ax3.text(2.5, 1.3, "s = 101  ✓  Key recovered!", fontsize=13,
             ha="center", va="center", color=COLORS["coral"],
             family="monospace")

    fig.suptitle("Simon's Algorithm: Complete Worked Example (n = 3)",
                 fontsize=16, y=1.02, color=COLORS["dark"])
    fig.tight_layout()
    fig.savefig(OUT / "12_simons_worked_example.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  [12] Simon's worked example")


# ── Figure 13: Even-Mansour Attack Diagram ─────────────────────────
def fig_even_mansour_worked():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7),
                                     gridspec_kw={"height_ratios": [1, 1.2]})

    # Top panel: cipher structure
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 4)
    ax1.axis("off")
    ax1.set_title("Even-Mansour Cipher Structure", fontsize=14,
                   color=COLORS["dark"], pad=10)

    # Input
    ax1.text(0.5, 2, "x", fontsize=16, ha="center", va="center",
             color=COLORS["navy"], family="serif",
             bbox=dict(boxstyle="round,pad=0.3", facecolor=COLORS["mint"],
                       edgecolor=COLORS["navy"], linewidth=1.5))

    # XOR with k1
    ax1.annotate("", xy=(1.8, 2), xytext=(1.0, 2),
                 arrowprops=dict(arrowstyle="->", color=COLORS["dark"], linewidth=1.5))
    circle1 = plt.Circle((2.2, 2), 0.3, fill=False, edgecolor=COLORS["navy"],
                          linewidth=2, zorder=3)
    ax1.add_patch(circle1)
    ax1.text(2.2, 2, "⊕", fontsize=16, ha="center", va="center",
             color=COLORS["navy"])
    ax1.annotate("", xy=(2.2, 2.7), xytext=(2.2, 3.3),
                 arrowprops=dict(arrowstyle="->", color=COLORS["coral"], linewidth=1.5))
    ax1.text(2.2, 3.6, "k₁", fontsize=14, ha="center", va="center",
             color=COLORS["coral"],
             bbox=dict(boxstyle="round,pad=0.2", facecolor="#FDE8E9",
                       edgecolor=COLORS["coral"], linewidth=1.5))

    # Permutation P
    ax1.annotate("", xy=(3.5, 2), xytext=(2.6, 2),
                 arrowprops=dict(arrowstyle="->", color=COLORS["dark"], linewidth=1.5))
    perm_rect = plt.Rectangle((3.5, 1.3), 1.8, 1.4, facecolor=COLORS["mint"],
                               edgecolor=COLORS["teal"], linewidth=2, zorder=2)
    ax1.add_patch(perm_rect)
    ax1.text(4.4, 2, "P", fontsize=18, ha="center", va="center",
             color=COLORS["navy"], family="serif")
    ax1.text(4.4, 1.0, "(public permutation)", fontsize=8, ha="center",
             color=COLORS["sage"])

    # XOR with k2
    ax1.annotate("", xy=(6.0, 2), xytext=(5.4, 2),
                 arrowprops=dict(arrowstyle="->", color=COLORS["dark"], linewidth=1.5))
    circle2 = plt.Circle((6.4, 2), 0.3, fill=False, edgecolor=COLORS["navy"],
                          linewidth=2, zorder=3)
    ax1.add_patch(circle2)
    ax1.text(6.4, 2, "⊕", fontsize=16, ha="center", va="center",
             color=COLORS["navy"])
    ax1.annotate("", xy=(6.4, 2.7), xytext=(6.4, 3.3),
                 arrowprops=dict(arrowstyle="->", color=COLORS["coral"], linewidth=1.5))
    ax1.text(6.4, 3.6, "k₂", fontsize=14, ha="center", va="center",
             color=COLORS["coral"],
             bbox=dict(boxstyle="round,pad=0.2", facecolor="#FDE8E9",
                       edgecolor=COLORS["coral"], linewidth=1.5))

    # Output
    ax1.annotate("", xy=(7.5, 2), xytext=(6.8, 2),
                 arrowprops=dict(arrowstyle="->", color=COLORS["dark"], linewidth=1.5))
    ax1.text(8.0, 2, "E(x)", fontsize=16, ha="center", va="center",
             color=COLORS["navy"], family="serif",
             bbox=dict(boxstyle="round,pad=0.3", facecolor=COLORS["mint"],
                       edgecolor=COLORS["navy"], linewidth=1.5))

    # Formula
    ax1.text(5, 0.3, "E(x) = P(x ⊕ k₁) ⊕ k₂", fontsize=13,
             ha="center", color=COLORS["dark"], family="serif",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                       edgecolor=COLORS["sage"], linewidth=1))

    # Bottom panel: attack reduction
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 5)
    ax2.axis("off")
    ax2.set_title("Simon's Attack Reduction", fontsize=14,
                   color=COLORS["dark"], pad=10)

    # The reduction
    steps = [
        (0.5, 4.0, "Define:", "f(x) = E(x) ⊕ P(x)"),
        (0.5, 3.0, "Expand:", "f(x) = P(x⊕k₁)⊕k₂ ⊕ P(x)"),
        (0.5, 2.0, "Key insight:", "f(x⊕k₁) = P(x)⊕k₂ ⊕ P(x⊕k₁) = f(x)"),
    ]
    for x, y, label, formula in steps:
        ax2.text(x, y, label, fontsize=11, ha="left", va="center",
                 color=COLORS["sage"])
        ax2.text(x + 1.8, y, formula, fontsize=12, ha="left", va="center",
                 color=COLORS["navy"], family="monospace")

    ax2.annotate("", xy=(5, 2.0 - 0.5), xytext=(5, 2.0 - 0.2),
                 arrowprops=dict(arrowstyle="->,head_width=0.15",
                                 color=COLORS["navy"], linewidth=1.5))

    result_rect = plt.Rectangle((1.5, 0.3), 7, 1.0,
                                 facecolor="#FDE8E9", edgecolor=COLORS["coral"],
                                 linewidth=2, zorder=2)
    ax2.add_patch(result_rect)
    ax2.text(5, 0.8, "f(x) has period s = k₁  →  Simon's algorithm recovers k₁ in O(n) queries",
             fontsize=11, ha="center", va="center", color=COLORS["coral"])

    fig.tight_layout()
    fig.savefig(OUT / "13_even_mansour_attack.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  [13] Even-Mansour attack diagram")


# ── Figure 14: 3-Round Feistel Attack Diagram ──────────────────────
def fig_feistel_worked():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6),
                                     gridspec_kw={"width_ratios": [1.1, 1]})

    # Left panel: Feistel network structure
    ax1.set_xlim(0, 8)
    ax1.set_ylim(-0.5, 9)
    ax1.axis("off")
    ax1.set_title("3-Round Feistel Network", fontsize=14,
                   color=COLORS["dark"], pad=10)

    # Draw 3 rounds
    for rnd in range(3):
        y_top = 7.5 - rnd * 2.5
        y_bot = y_top - 1.8

        # L and R wires
        ax1.plot([1.5, 1.5], [y_top, y_bot], color=COLORS["dark"], linewidth=1.5)
        ax1.plot([5.5, 5.5], [y_top, y_bot + 0.8], color=COLORS["dark"], linewidth=1.5)
        ax1.plot([5.5, 5.5], [y_bot + 0.4, y_bot], color=COLORS["dark"], linewidth=1.5)

        # Cross-over (swap)
        ax1.plot([1.5, 5.5], [y_bot, y_bot - 0.15], color=COLORS["dark"],
                 linewidth=1, linestyle="--", alpha=0.4)
        ax1.plot([5.5, 1.5], [y_bot, y_bot - 0.15], color=COLORS["dark"],
                 linewidth=1, linestyle="--", alpha=0.4)

        # F box (round function)
        f_rect = plt.Rectangle((3.8, y_top - 1.4), 1.2, 0.8,
                                facecolor="#FDE8E9", edgecolor=COLORS["coral"],
                                linewidth=1.5, zorder=3)
        ax1.add_patch(f_rect)
        ax1.text(4.4, y_top - 1.0, f"F", fontsize=13, ha="center", va="center",
                 color=COLORS["coral"], family="serif")

        # Arrow from R into F
        ax1.annotate("", xy=(3.8, y_top - 1.0), xytext=(5.5, y_top - 1.0),
                     arrowprops=dict(arrowstyle="<-", color=COLORS["dark"],
                                     linewidth=1))

        # Arrow from F to XOR
        ax1.annotate("", xy=(2.0, y_top - 1.0), xytext=(3.8, y_top - 1.0),
                     arrowprops=dict(arrowstyle="->", color=COLORS["dark"],
                                     linewidth=1))

        # XOR circle on L wire
        circle = plt.Circle((1.5, y_top - 1.0), 0.2, fill=False,
                             edgecolor=COLORS["navy"], linewidth=1.5, zorder=3)
        ax1.add_patch(circle)
        ax1.text(1.5, y_top - 1.0, "⊕", fontsize=11, ha="center", va="center",
                 color=COLORS["navy"])

        # Round label
        ax1.text(6.8, y_top - 0.9, f"Round {rnd+1}", fontsize=10,
                 color=COLORS["sage"])

    # Labels
    ax1.text(1.5, 8.0, "L", fontsize=14, ha="center", color=COLORS["navy"])
    ax1.text(5.5, 8.0, "R", fontsize=14, ha="center", color=COLORS["navy"])
    ax1.text(1.5, -0.3, "L'", fontsize=14, ha="center", color=COLORS["navy"])
    ax1.text(5.5, -0.3, "R'", fontsize=14, ha="center", color=COLORS["navy"])
    ax1.text(4.0, 8.3, "F(x) = S[x ⊕ k]", fontsize=11, ha="center",
             color=COLORS["coral"], family="monospace")

    # Right panel: attack reduction
    ax2.set_xlim(0, 6)
    ax2.set_ylim(0, 9)
    ax2.axis("off")
    ax2.set_title("Simon's Attack on Feistel", fontsize=14,
                   color=COLORS["dark"], pad=10)

    steps = [
        (0.3, 8.0, "Construct function:"),
        (0.3, 7.2, "f(x) = E_L(x, 0) ⊕ E_L(x, 1)"),
        (0.3, 6.2, "Encrypt (x, 0) and (x, 1),"),
        (0.3, 5.7, "XOR the left halves"),
        (0.3, 4.7, "After 3-round analysis:"),
        (0.3, 3.9, "f(x) = S[x ⊕ a] ⊕ S[x ⊕ b]"),
        (0.3, 3.2, "where a = S[k]⊕k, b = S[1⊕k]⊕k"),
    ]

    for x, y, text in steps:
        if "Construct" in text or "Encrypt" in text or "After" in text:
            ax2.text(x, y, text, fontsize=11, color=COLORS["sage"])
        elif "f(x) = E_L" in text or "f(x) = S[" in text:
            ax2.text(x, y, text, fontsize=12, color=COLORS["navy"],
                     family="monospace")
        elif "where" in text:
            ax2.text(x, y, text, fontsize=10, color=COLORS["dark"],
                     family="monospace")
        else:
            ax2.text(x, y, text, fontsize=10, color=COLORS["dark"])

    ax2.annotate("", xy=(3, 2.5), xytext=(3, 2.9),
                 arrowprops=dict(arrowstyle="->,head_width=0.15",
                                 color=COLORS["navy"], linewidth=1.5))

    ax2.text(3, 2.1, "Period: s = a ⊕ b = S[k] ⊕ S[1⊕k]",
             fontsize=11, ha="center", color=COLORS["navy"], family="monospace")

    result_rect = plt.Rectangle((0.3, 0.5), 5.4, 1.2,
                                 facecolor="#FDE8E9", edgecolor=COLORS["coral"],
                                 linewidth=2, zorder=2)
    ax2.add_patch(result_rect)
    ax2.text(3, 1.1, "Simon recovers s, then brute-force\nk from S[k] ⊕ S[1⊕k] = s",
             fontsize=11, ha="center", va="center", color=COLORS["coral"])

    fig.suptitle("3-Round Feistel: Structure and Quantum Attack",
                 fontsize=16, y=1.02, color=COLORS["dark"])
    fig.tight_layout()
    fig.savefig(OUT / "14_feistel_attack.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  [14] Feistel attack diagram")


# ── Figure 15: Slide Attack Diagram ────────────────────────────────
def fig_slide_worked():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5),
                                     gridspec_kw={"width_ratios": [1.2, 1]})

    # Left panel: iterated cipher rounds
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 7)
    ax1.axis("off")
    ax1.set_title("Iterated Cipher: r Identical Rounds", fontsize=14,
                   color=COLORS["dark"], pad=10)

    # Draw chain of rounds
    x_positions = [1, 3, 5, 7.5]
    labels = ["Fk", "Fk", "Fk", "Fk"]
    round_labels = ["Round 1", "Round 2", "Round 3", "Round r"]

    ax1.text(0.2, 4, "x", fontsize=16, ha="center", va="center",
             color=COLORS["navy"], family="serif",
             bbox=dict(boxstyle="round,pad=0.3", facecolor=COLORS["mint"],
                       edgecolor=COLORS["navy"], linewidth=1.5))

    for i, (xp, lab, rlab) in enumerate(zip(x_positions, labels, round_labels)):
        if i == 2:
            ax1.text(xp + 0.5, 4, "···", fontsize=20, ha="center", va="center",
                     color=COLORS["sage"])
            continue

        rect = plt.Rectangle((xp, 3.2), 1.5, 1.6,
                               facecolor=COLORS["mint"], edgecolor=COLORS["navy"],
                               linewidth=1.5, zorder=2)
        ax1.add_patch(rect)
        ax1.text(xp + 0.75, 4, lab, fontsize=14, ha="center", va="center",
                 color=COLORS["navy"], family="serif")
        ax1.text(xp + 0.75, 3.0, rlab, fontsize=9, ha="center",
                 color=COLORS["sage"])

        # Key input
        ax1.annotate("", xy=(xp + 0.75, 4.8), xytext=(xp + 0.75, 5.5),
                     arrowprops=dict(arrowstyle="->", color=COLORS["coral"],
                                     linewidth=1))
        if i == 0:
            ax1.text(xp + 0.75, 5.8, "k", fontsize=13, ha="center",
                     color=COLORS["coral"],
                     bbox=dict(boxstyle="round,pad=0.2", facecolor="#FDE8E9",
                               edgecolor=COLORS["coral"], linewidth=1))

        # Arrows between rounds
        if i == 0:
            ax1.annotate("", xy=(xp, 4), xytext=(0.6, 4),
                         arrowprops=dict(arrowstyle="->", color=COLORS["dark"],
                                         linewidth=1.5))
        if i < 3:
            ax1.annotate("", xy=(xp + 2.0 if i < 2 else xp + 2.5, 4),
                         xytext=(xp + 1.5, 4),
                         arrowprops=dict(arrowstyle="->", color=COLORS["dark"],
                                         linewidth=1.5))

    # Same key for all rounds annotation
    ax1.text(5, 6.3, "Same key k used in every round", fontsize=11,
             ha="center", color=COLORS["coral"],
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#FDE8E9",
                       edgecolor=COLORS["coral"], linewidth=1, alpha=0.8))

    ax1.text(9.5, 4, "E(x)", fontsize=16, ha="center", va="center",
             color=COLORS["navy"], family="serif",
             bbox=dict(boxstyle="round,pad=0.3", facecolor=COLORS["mint"],
                       edgecolor=COLORS["navy"], linewidth=1.5))
    ax1.annotate("", xy=(9.0, 4), xytext=(8.5 + 0.5, 4),
                 arrowprops=dict(arrowstyle="->", color=COLORS["dark"],
                                 linewidth=1.5))

    # Bottom: key insight
    insight_rect = plt.Rectangle((0.5, 0.8), 9, 1.5,
                                  facecolor=COLORS["mint"], edgecolor=COLORS["teal"],
                                  linewidth=1.5, alpha=0.7, zorder=0)
    ax1.add_patch(insight_rect)
    ax1.text(5, 1.8, "Fk(x) = P(x ⊕ k)  where P is a public permutation",
             fontsize=11, ha="center", color=COLORS["navy"], family="monospace")
    ax1.text(5, 1.15, "Attack uses only ONE round — ignores all others!",
             fontsize=11, ha="center", color=COLORS["coral"])

    # Right panel: attack
    ax2.set_xlim(0, 6)
    ax2.set_ylim(0, 7)
    ax2.axis("off")
    ax2.set_title("Quantum Slide Attack", fontsize=14,
                   color=COLORS["dark"], pad=10)

    steps = [
        (0.3, 6.2, "Construct:", "f(x) = Fk(x) ⊕ P(x)"),
        (0.3, 5.2, "Expand:", "f(x) = P(x⊕k) ⊕ P(x)"),
        (0.3, 4.2, "Verify:", "f(x⊕k) = P(x) ⊕ P(x⊕k)"),
        (0.3, 3.5, "", "         = f(x)  ✓"),
    ]
    for x, y, label, formula in steps:
        if label:
            ax2.text(x, y, label, fontsize=11, color=COLORS["sage"])
        ax2.text(x + (1.8 if label else 0), y, formula, fontsize=12,
                 color=COLORS["navy"], family="monospace")

    ax2.annotate("", xy=(3, 2.5), xytext=(3, 3.0),
                 arrowprops=dict(arrowstyle="->,head_width=0.15",
                                 color=COLORS["navy"], linewidth=1.5))

    result_rect = plt.Rectangle((0.3, 1.2), 5.4, 1.1,
                                 facecolor="#FDE8E9", edgecolor=COLORS["coral"],
                                 linewidth=2, zorder=2)
    ax2.add_patch(result_rect)
    ax2.text(3, 1.75, "Period s = k  →  direct key recovery!",
             fontsize=12, ha="center", va="center", color=COLORS["coral"])

    # Complexity comparison
    ax2.text(3, 0.5, "O(n) queries regardless of round count r",
             fontsize=10, ha="center", color=COLORS["navy"],
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                       edgecolor=COLORS["navy"], linewidth=1, alpha=0.8))

    fig.suptitle("Quantum Slide Attack: Round Count is Irrelevant",
                 fontsize=16, y=1.02, color=COLORS["dark"])
    fig.tight_layout()
    fig.savefig(OUT / "15_slide_attack.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  [15] Slide attack diagram")


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
    fig_simons_circuit()
    fig_simons_worked_example()
    fig_even_mansour_worked()
    fig_feistel_worked()
    fig_slide_worked()
    print()
    print(f"Done! {len(list(OUT.glob('*.png')))} figures saved to {OUT}/")
    print()
    print("Recommended poster layout:")
    print("  INTRODUCTION:  Fig 10 (attack overview), Fig 7 (Simon vs Grover)")
    print("  METHODOLOGY:   Fig 11 (circuit), Fig 12 (worked example),")
    print("                 Fig 13 (Even-Mansour), Fig 14 (Feistel), Fig 15 (Slide)")
    print("  RESULTS:       Fig 6 (success rates), Fig 1 (noise cliff),")
    print("                 Fig 2 (slide independence), Fig 5 (convergence)")
    print("  CONCLUSION:    Fig 9 (PRINCE security), Fig 8 (resource estimates)")
