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


# ── Figure 13: Even-Mansour Oracle Circuit ───────────────────────
def fig_even_mansour_worked():
    """Quantum circuit with Even-Mansour oracle, annotated for non-experts."""
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.set_xlim(0, 11)
    ax.set_ylim(-0.6, 5.0)
    ax.axis("off")

    ax.text(5.5, 4.6, "Even-Mansour:  E(x) = P(x ⊕ k₁) ⊕ k₂",
            fontsize=10.5, ha="center", color=COLORS["dark"], family="monospace",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                      edgecolor=COLORS["sage"], linewidth=1))

    yx, yy = 3.0, 1.0
    blw = 2.5
    gh = 0.35

    ax.text(0.15, yx, "|0⟩ⁿ", fontsize=11, ha="right", va="center",
            family="serif", color=COLORS["dark"])
    ax.text(0.15, yy, "|0⟩ⁿ", fontsize=11, ha="right", va="center",
            family="serif", color=COLORS["dark"])
    ax.text(0.05, yx + 0.4, "input", fontsize=7, ha="center",
            color=COLORS["sage"], style="italic")
    ax.text(0.05, yy + 0.4, "output", fontsize=7, ha="center",
            color=COLORS["sage"], style="italic")

    ax.plot([0.25, 10.3], [yx, yx], color=COLORS["dark"], lw=blw, zorder=1)
    ax.plot([0.25, 10.3], [yy, yy], color=COLORS["dark"], lw=blw, zorder=1)

    def draw_gate(cx, cy, label, w=0.55, ec=COLORS["navy"], fs=10,
                  fc=COLORS["mint"], tc=COLORS["navy"]):
        r = plt.Rectangle((cx - w / 2, cy - gh), w, 2 * gh,
                           facecolor=fc, edgecolor=ec, lw=1.5, zorder=3)
        ax.add_patch(r)
        ax.text(cx, cy, label, fontsize=fs,
                ha="center", va="center", color=tc, family="serif")

    def draw_cnot(cx):
        ax.plot([cx, cx], [yx - gh + 0.05, yy + 0.15],
                color=COLORS["navy"], lw=1.3, zorder=2)
        ax.plot(cx, yx, 'o', color=COLORS["navy"], ms=5, zorder=4)
        c = plt.Circle((cx, yy), 0.13, fill=True, facecolor="white",
                        edgecolor=COLORS["navy"], lw=1.5, zorder=4)
        ax.add_patch(c)
        ax.text(cx, yy, "⊕", fontsize=9, ha="center", va="center",
                color=COLORS["navy"], zorder=5)
        ax.text(cx + 0.18, (yx + yy) / 2, "copy", fontsize=7, ha="left",
                color=COLORS["sage"], style="italic")

    def draw_meter(cx, cy):
        bg = plt.Circle((cx, cy - 0.05), 0.22, fill=True, facecolor="white",
                         edgecolor="white", lw=0, zorder=3)
        ax.add_patch(bg)
        arc = plt.Circle((cx, cy - 0.05), 0.2, fill=False,
                          edgecolor=COLORS["navy"], lw=1.5, zorder=4)
        ax.add_patch(arc)
        ax.plot([cx, cx + 0.1], [cy - 0.05, cy + 0.2],
                color=COLORS["navy"], lw=1.5, zorder=5)
        ax.plot([cx - 0.2, cx + 0.2], [cy - 0.25, cy - 0.25],
                color=COLORS["navy"], lw=1.5, zorder=5)

    draw_gate(0.75, yx, "H⊗ⁿ", fs=9)
    ax.text(0.75, yx + gh + 0.15, "superpose", fontsize=7, ha="center",
            color=COLORS["sage"], style="italic")

    ox1, ox2 = 1.5, 7.5
    oracle_rect = plt.Rectangle((ox1, yy - 0.35), ox2 - ox1, yx - yy + 0.7,
                                 facecolor="#FDE8E9", edgecolor=COLORS["coral"],
                                 lw=1.5, linestyle=(0, (5, 3)),
                                 zorder=0, alpha=0.25)
    ax.add_patch(oracle_rect)

    draw_gate(2.5, yx, "E", w=0.6)
    draw_cnot(3.15)
    draw_gate(3.95, yx, "undo E", w=0.8, fs=8)
    ax.text(3.15, yy - 0.28, "⊕ E(x)", fontsize=8, ha="center",
            color=COLORS["coral"])

    draw_gate(5.05, yx, "P", w=0.5, ec=COLORS["teal"])
    draw_cnot(5.6)
    draw_gate(6.3, yx, "undo P", w=0.8, fs=8, ec=COLORS["teal"])
    ax.text(5.6, yy - 0.28, "⊕ P(x)", fontsize=8, ha="center",
            color=COLORS["coral"])

    draw_gate(8.1, yx, "H⊗ⁿ", fs=9)
    ax.text(8.1, yx + gh + 0.15, "interfere", fontsize=7, ha="center",
            color=COLORS["sage"], style="italic")

    draw_meter(9.1, yx)
    ax.text(9.1, yx + gh + 0.15, "measure", fontsize=7, ha="center",
            color=COLORS["sage"], style="italic")

    ax.text(10.0, yx, "y", fontsize=12, ha="center", va="center",
            color=COLORS["navy"], family="serif")
    ax.text(10.0, yx - 0.35, "(y·s = 0)", fontsize=8, ha="center",
            color=COLORS["sage"])

    ax.text(4.5, yy - 0.55, "Oracle Uf :  f(x) = E(x) ⊕ P(x)",
            fontsize=8.5, ha="center", color=COLORS["coral"], style="italic")
    ax.text(5.5, -0.35, "Period  s = k₁  →  Simon's recovers k₁ in O(n) queries",
            fontsize=9.5, ha="center", color=COLORS["coral"],
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#FDE8E9",
                      edgecolor=COLORS["coral"], lw=1.5))

    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "13_even_mansour_attack.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  [13] Even-Mansour oracle circuit")


# ── Figure 14: 3-Round Feistel Oracle Circuit ────────────────────
def fig_feistel_worked():
    """Quantum circuit with Feistel oracle, annotated for non-experts."""
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.set_xlim(0, 11)
    ax.set_ylim(-0.6, 5.0)
    ax.axis("off")

    ax.text(5.5, 4.6, "3-Round Feistel:  round function F(x) = S[x ⊕ k]",
            fontsize=10.5, ha="center", color=COLORS["dark"], family="monospace",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                      edgecolor=COLORS["sage"], linewidth=1))

    yx, yy = 3.0, 1.0
    blw = 2.5
    gh = 0.35

    ax.text(0.15, yx, "|0⟩ⁿ", fontsize=11, ha="right", va="center",
            family="serif", color=COLORS["dark"])
    ax.text(0.15, yy, "|0⟩ⁿ", fontsize=11, ha="right", va="center",
            family="serif", color=COLORS["dark"])
    ax.text(0.05, yx + 0.4, "input", fontsize=7, ha="center",
            color=COLORS["sage"], style="italic")
    ax.text(0.05, yy + 0.4, "output", fontsize=7, ha="center",
            color=COLORS["sage"], style="italic")

    ax.plot([0.25, 10.3], [yx, yx], color=COLORS["dark"], lw=blw, zorder=1)
    ax.plot([0.25, 10.3], [yy, yy], color=COLORS["dark"], lw=blw, zorder=1)

    def draw_gate(cx, cy, label, w=0.55, ec=COLORS["navy"], fs=10,
                  fc=COLORS["mint"], tc=COLORS["navy"],
                  label2=None, fs2=7):
        r = plt.Rectangle((cx - w / 2, cy - gh), w, 2 * gh,
                           facecolor=fc, edgecolor=ec, lw=1.5, zorder=3)
        ax.add_patch(r)
        if label2:
            ax.text(cx, cy + 0.1, label, fontsize=fs,
                    ha="center", va="center", color=tc, family="monospace")
            ax.text(cx, cy - 0.15, label2, fontsize=fs2,
                    ha="center", va="center", color=COLORS["sage"])
        else:
            ax.text(cx, cy, label, fontsize=fs,
                    ha="center", va="center", color=tc, family="serif")

    def draw_cnot(cx):
        ax.plot([cx, cx], [yx - gh + 0.05, yy + 0.15],
                color=COLORS["navy"], lw=1.3, zorder=2)
        ax.plot(cx, yx, 'o', color=COLORS["navy"], ms=5, zorder=4)
        c = plt.Circle((cx, yy), 0.13, fill=True, facecolor="white",
                        edgecolor=COLORS["navy"], lw=1.5, zorder=4)
        ax.add_patch(c)
        ax.text(cx, yy, "⊕", fontsize=9, ha="center", va="center",
                color=COLORS["navy"], zorder=5)
        ax.text(cx + 0.18, (yx + yy) / 2, "copy", fontsize=7, ha="left",
                color=COLORS["sage"], style="italic")

    def draw_meter(cx, cy):
        bg = plt.Circle((cx, cy - 0.05), 0.22, fill=True, facecolor="white",
                         edgecolor="white", lw=0, zorder=3)
        ax.add_patch(bg)
        arc = plt.Circle((cx, cy - 0.05), 0.2, fill=False,
                          edgecolor=COLORS["navy"], lw=1.5, zorder=4)
        ax.add_patch(arc)
        ax.plot([cx, cx + 0.1], [cy - 0.05, cy + 0.2],
                color=COLORS["navy"], lw=1.5, zorder=5)
        ax.plot([cx - 0.2, cx + 0.2], [cy - 0.25, cy - 0.25],
                color=COLORS["navy"], lw=1.5, zorder=5)

    draw_gate(0.75, yx, "H⊗ⁿ", fs=9)
    ax.text(0.75, yx + gh + 0.15, "superpose", fontsize=7, ha="center",
            color=COLORS["sage"], style="italic")

    ox1, ox2 = 1.5, 7.5
    oracle_rect = plt.Rectangle((ox1, yy - 0.35), ox2 - ox1, yx - yy + 0.7,
                                 facecolor="#FDE8E9", edgecolor=COLORS["coral"],
                                 lw=1.5, linestyle=(0, (5, 3)),
                                 zorder=0, alpha=0.25)
    ax.add_patch(oracle_rect)

    draw_gate(2.5, yx, "E(·,0)", w=0.85, fs=9, label2="left half", fs2=6)
    draw_cnot(3.3)
    draw_gate(3.9, yx, "undo", w=0.55, fs=9)
    ax.text(3.1, yy - 0.28, "⊕ E_L(x,0)", fontsize=7.5, ha="center",
            color=COLORS["coral"])

    draw_gate(5.0, yx, "E(·,1)", w=0.85, fs=9, label2="left half", fs2=6)
    draw_cnot(5.8)
    draw_gate(6.4, yx, "undo", w=0.55, fs=9)
    ax.text(5.6, yy - 0.28, "⊕ E_L(x,1)", fontsize=7.5, ha="center",
            color=COLORS["coral"])

    draw_gate(8.1, yx, "H⊗ⁿ", fs=9)
    ax.text(8.1, yx + gh + 0.15, "interfere", fontsize=7, ha="center",
            color=COLORS["sage"], style="italic")

    draw_meter(9.1, yx)
    ax.text(9.1, yx + gh + 0.15, "measure", fontsize=7, ha="center",
            color=COLORS["sage"], style="italic")

    ax.text(10.0, yx, "y", fontsize=12, ha="center", va="center",
            color=COLORS["navy"], family="serif")
    ax.text(10.0, yx - 0.35, "(y·s = 0)", fontsize=8, ha="center",
            color=COLORS["sage"])

    ax.text(4.5, yy - 0.55,
            "Oracle Uf :  f(x) = E_L(x,0) ⊕ E_L(x,1)",
            fontsize=8.5, ha="center", color=COLORS["coral"], style="italic")
    ax.text(5.5, -0.35,
            "Period  s = S[k] ⊕ S[1⊕k]  →  Simon's recovers s, brute-force k",
            fontsize=9.5, ha="center", color=COLORS["coral"],
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#FDE8E9",
                      edgecolor=COLORS["coral"], lw=1.5))

    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "14_feistel_attack.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  [14] Feistel oracle circuit")


# ── Figure 15: Slide Attack Oracle Circuit ───────────────────────
def fig_slide_worked():
    """Quantum circuit with slide attack oracle, annotated for non-experts."""
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.set_xlim(0, 11)
    ax.set_ylim(-0.6, 5.0)
    ax.axis("off")

    ax.text(5.5, 4.6,
            "Iterated cipher:  E = Fk ∘ ··· ∘ Fk  (r rounds),  Fk(x) = P(x ⊕ k)",
            fontsize=9.5, ha="center", color=COLORS["dark"], family="monospace",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                      edgecolor=COLORS["sage"], linewidth=1))

    yx, yy = 3.0, 1.0
    blw = 2.5
    gh = 0.35

    ax.text(0.15, yx, "|0⟩ⁿ", fontsize=11, ha="right", va="center",
            family="serif", color=COLORS["dark"])
    ax.text(0.15, yy, "|0⟩ⁿ", fontsize=11, ha="right", va="center",
            family="serif", color=COLORS["dark"])
    ax.text(0.05, yx + 0.4, "input", fontsize=7, ha="center",
            color=COLORS["sage"], style="italic")
    ax.text(0.05, yy + 0.4, "output", fontsize=7, ha="center",
            color=COLORS["sage"], style="italic")

    ax.plot([0.25, 10.3], [yx, yx], color=COLORS["dark"], lw=blw, zorder=1)
    ax.plot([0.25, 10.3], [yy, yy], color=COLORS["dark"], lw=blw, zorder=1)

    def draw_gate(cx, cy, label, w=0.55, ec=COLORS["navy"], fs=10,
                  fc=COLORS["mint"], tc=COLORS["navy"]):
        r = plt.Rectangle((cx - w / 2, cy - gh), w, 2 * gh,
                           facecolor=fc, edgecolor=ec, lw=1.5, zorder=3)
        ax.add_patch(r)
        ax.text(cx, cy, label, fontsize=fs,
                ha="center", va="center", color=tc, family="serif")

    def draw_cnot(cx):
        ax.plot([cx, cx], [yx - gh + 0.05, yy + 0.15],
                color=COLORS["navy"], lw=1.3, zorder=2)
        ax.plot(cx, yx, 'o', color=COLORS["navy"], ms=5, zorder=4)
        c = plt.Circle((cx, yy), 0.13, fill=True, facecolor="white",
                        edgecolor=COLORS["navy"], lw=1.5, zorder=4)
        ax.add_patch(c)
        ax.text(cx, yy, "⊕", fontsize=9, ha="center", va="center",
                color=COLORS["navy"], zorder=5)
        ax.text(cx + 0.18, (yx + yy) / 2, "copy", fontsize=7, ha="left",
                color=COLORS["sage"], style="italic")

    def draw_meter(cx, cy):
        bg = plt.Circle((cx, cy - 0.05), 0.22, fill=True, facecolor="white",
                         edgecolor="white", lw=0, zorder=3)
        ax.add_patch(bg)
        arc = plt.Circle((cx, cy - 0.05), 0.2, fill=False,
                          edgecolor=COLORS["navy"], lw=1.5, zorder=4)
        ax.add_patch(arc)
        ax.plot([cx, cx + 0.1], [cy - 0.05, cy + 0.2],
                color=COLORS["navy"], lw=1.5, zorder=5)
        ax.plot([cx - 0.2, cx + 0.2], [cy - 0.25, cy - 0.25],
                color=COLORS["navy"], lw=1.5, zorder=5)

    draw_gate(0.75, yx, "H⊗ⁿ", fs=9)
    ax.text(0.75, yx + gh + 0.15, "superpose", fontsize=7, ha="center",
            color=COLORS["sage"], style="italic")

    ox1, ox2 = 1.5, 7.5
    oracle_rect = plt.Rectangle((ox1, yy - 0.35), ox2 - ox1, yx - yy + 0.7,
                                 facecolor="#FDE8E9", edgecolor=COLORS["coral"],
                                 lw=1.5, linestyle=(0, (5, 3)),
                                 zorder=0, alpha=0.25)
    ax.add_patch(oracle_rect)

    draw_gate(2.5, yx, "Fk", w=0.6, ec=COLORS["coral"],
              fc="#FDE8E9", tc=COLORS["coral"])
    ax.text(2.5, yx + gh + 0.15, "1 round", fontsize=7, ha="center",
            color=COLORS["coral"], style="italic")
    draw_cnot(3.15)
    draw_gate(3.95, yx, "undo Fk", w=0.85, fs=8, ec=COLORS["coral"],
              fc="#FDE8E9", tc=COLORS["coral"])
    ax.text(3.15, yy - 0.28, "⊕ Fk(x)", fontsize=8, ha="center",
            color=COLORS["coral"])

    draw_gate(5.1, yx, "P", w=0.5, ec=COLORS["teal"])
    ax.text(5.1, yx + gh + 0.15, "public", fontsize=7, ha="center",
            color=COLORS["sage"], style="italic")
    draw_cnot(5.6)
    draw_gate(6.3, yx, "undo P", w=0.8, fs=8, ec=COLORS["teal"])
    ax.text(5.6, yy - 0.28, "⊕ P(x)", fontsize=8, ha="center",
            color=COLORS["coral"])

    draw_gate(8.1, yx, "H⊗ⁿ", fs=9)
    ax.text(8.1, yx + gh + 0.15, "interfere", fontsize=7, ha="center",
            color=COLORS["sage"], style="italic")

    draw_meter(9.1, yx)
    ax.text(9.1, yx + gh + 0.15, "measure", fontsize=7, ha="center",
            color=COLORS["sage"], style="italic")

    ax.text(10.0, yx, "y", fontsize=12, ha="center", va="center",
            color=COLORS["navy"], family="serif")
    ax.text(10.0, yx - 0.35, "(y·s = 0)", fontsize=8, ha="center",
            color=COLORS["sage"])

    ax.text(4.5, yy - 0.55, "Oracle Uf :  f(x) = Fk(x) ⊕ P(x)",
            fontsize=8.5, ha="center", color=COLORS["coral"], style="italic")
    ax.text(5.5, -0.35,
            "Period  s = k  →  direct key recovery in O(n) queries, any r",
            fontsize=9.5, ha="center", color=COLORS["coral"],
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#FDE8E9",
                      edgecolor=COLORS["coral"], lw=1.5))

    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "15_slide_attack.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  [15] Slide oracle circuit")


# ── Figure 16: PRINCE Timing — Quantum vs Classical ────────────────
def fig_prince_timing():
    with open(RESULTS / "prince_timing.json") as f:
        data = json.load(f)

    fig, ax = plt.subplots(figsize=(9, 5.5))

    ns_q, ts_q = [], []
    ns_c, ts_c = [], []

    for n_str in sorted(data.keys(), key=int):
        entry = data[n_str]
        n = int(n_str)

        if entry.get("quantum_time_s") is not None:
            ns_q.append(n)
            ts_q.append(entry["quantum_time_s"])

        if entry.get("classical_time_s") is not None:
            ns_c.append(n)
            ts_c.append(entry["classical_time_s"])

    # Plot quantum
    ax.semilogy(ns_q, ts_q, "-", color=COLORS["navy"],
                linewidth=2.5, label="Simon's algorithm (quantum)", zorder=3)

    # Plot classical
    ax.semilogy(ns_c, ts_c, "-", color=COLORS["coral"],
                linewidth=2.5, label="Brute-force (classical)", zorder=3)

    # Extrapolate classical (doubles per bit)
    if len(ns_c) >= 2 and ts_c[-1] > 0:
        last_n = ns_c[-1]
        last_t = ts_c[-1]
        extrap_ns = list(range(last_n + 1, 128))
        extrap_ts = [last_t * (2 ** (n - last_n)) for n in extrap_ns]
        ax.semilogy(extrap_ns, extrap_ts, "--", color=COLORS["coral"],
                    linewidth=1.5, alpha=0.5, zorder=2)

    # Annotate quantum result at n=127
    ax.annotate(f"127-bit key cracked\nin {ts_q[-1]*1000:.0f} ms",
                xy=(127, ts_q[-1]), xytext=(85, 1e-5),
                fontsize=11, color=COLORS["navy"],
                arrowprops=dict(arrowstyle="->", color=COLORS["navy"],
                                linewidth=1.5))

    # Annotate classical wall
    ax.annotate(f"Classical gives up\nat n={ns_c[-1]} ({ts_c[-1]:.0f}s)",
                xy=(ns_c[-1], ts_c[-1]), xytext=(50, 1e6),
                fontsize=10, color=COLORS["coral"],
                arrowprops=dict(arrowstyle="->", color=COLORS["coral"],
                                linewidth=1.5))

    style_ax(ax, "Cracking a PRINCE Cipher: Quantum vs Classical",
             "Key Size n (bits)", "Time to Recover Key (seconds, log scale)")
    ax.set_xlim(0, 130)
    ax.set_ylim(1e-6, 1e35)
    ax.legend(fontsize=11, loc="upper left")
    ax.grid(axis="y", alpha=0.2)

    # Age of universe reference line
    ax.axhline(y=4.3e17, color=COLORS["sage"], linestyle="--",
               linewidth=0.8, alpha=0.5)
    ax.text(65, 1.5e18, "← age of the universe (13.8 billion years)",
            fontsize=9, color=COLORS["sage"], ha="center")

    fig.tight_layout()
    fig.savefig(OUT / "16_prince_timing.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  [16] PRINCE quantum vs classical timing")


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
    fig_prince_timing()
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
