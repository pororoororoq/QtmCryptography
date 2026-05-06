"""
Quantum resource estimation for Simon-based cryptographic attacks.

Estimates the physical resources (qubits, gates, time) needed to
execute Simon's algorithm attacks at cryptographically relevant scales.

Key metrics:
    - Logical qubits: 2n for Simon's circuit (input + output registers)
    - T-gates: dominate fault-tolerant cost (from Toffoli decomposition)
    - Circuit depth: determines wall-clock time
    - Physical qubits: logical * overhead from error correction (surface code)

Surface code overhead:
    - Code distance d determines error suppression: p_logical ~ (p_phys/p_th)^{d/2}
    - Physical qubits per logical qubit: ~2d^2 for surface code
    - T-gate via magic state distillation adds ~15d^2 additional qubits

Reference scales:
    - AES-128: n = 128, need 256 logical qubits minimum
    - AES-256: n = 256, need 512 logical qubits minimum
    - Lightweight (PRINCE): n = 64, need 128 logical qubits
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from qiskit import QuantumCircuit, transpile

from .simons_algorithm import build_oracle_from_secret


@dataclass
class ResourceEstimate:
    """Complete resource estimate for running Simon's attack."""
    n_bits: int
    logical_qubits: int
    t_gate_count: int
    cx_gate_count: int
    circuit_depth: int
    surface_code_distance: int
    physical_qubits: int
    physical_qubits_with_distillation: int
    execution_time_us: float
    total_queries: int
    target_logical_error_rate: float


def count_gates(oracle: QuantumCircuit, n: int) -> dict:
    """Count gates in a Simon circuit after transpilation to fault-tolerant basis.

    Decomposes to {H, CNOT, T, T†, S} basis (Clifford + T).
    MCX (multi-controlled X) gates decompose into O(n) Toffolis,
    each Toffoli costs 7 T-gates.
    """
    # Build full Simon circuit
    qc = QuantumCircuit(2 * n)
    qc.h(range(n))
    qc.compose(oracle, inplace=True)
    qc.h(range(n))

    # Transpile to basis gates
    transpiled = transpile(
        qc,
        basis_gates=["cx", "h", "t", "tdg", "s", "sdg", "x", "z"],
        optimization_level=2,
    )

    ops = transpiled.count_ops()

    # MCX gates get decomposed into Toffolis.
    # Each n-controlled X uses ~2(n-2) Toffolis (linear decomposition).
    # Each Toffoli = 7 T-gates + 8 CNOT gates.
    mcx_count = ops.get("mcx", 0)
    toffoli_from_mcx = mcx_count * max(2 * (n - 2), 1)

    t_count = ops.get("t", 0) + ops.get("tdg", 0) + toffoli_from_mcx * 7
    cx_count = ops.get("cx", 0) + toffoli_from_mcx * 8

    return {
        "h": ops.get("h", 0),
        "cx": cx_count,
        "t": t_count,
        "x": ops.get("x", 0),
        "total_gates": sum(ops.values()),
        "depth": transpiled.depth(),
        "mcx_original": mcx_count,
    }


def estimate_oracle_cost(n: int) -> dict:
    """Estimate the gate cost of the Simon oracle for n-bit secrets.

    For a truth-table oracle on n bits:
        - Worst case: 2^n MCX gates (one per input), each with n controls.
        - Each MCX with n controls -> O(n) Toffolis -> O(n) T-gates.
        - Total T-gates: O(n * 2^n) per oracle call.
        - Simon's uses O(n) oracle calls.
        - Total: O(n^2 * 2^n) T-gates for the full attack.

    For structured oracles (Even-Mansour, Feistel):
        - Can be much more efficient if the structure is exploited.
        - Even-Mansour oracle: O(n * 2^n) for truth-table, but O(n^2)
          if the permutation has efficient circuit implementation.
    """
    # Truth-table based (worst case, our current implementation)
    mcx_per_call_worst = 2**n  # One MCX per active input
    toffoli_per_mcx = max(2 * (n - 2), 1)  # Linear decomposition
    t_per_toffoli = 7

    t_gates_per_call_worst = mcx_per_call_worst * toffoli_per_mcx * t_per_toffoli
    simon_queries = n  # O(n) oracle calls needed

    # Efficient implementation (if permutation has polynomial circuit)
    # A permutation on n bits implemented as a reversible circuit
    # typically uses O(n * 2^n / log(n)) gates (Shannon bound),
    # but structured permutations (like AES S-box) can be much cheaper.
    t_gates_per_call_efficient = n * n * 50  # Rough estimate for structured P

    return {
        "n_bits": n,
        "truth_table_oracle": {
            "t_gates_per_query": t_gates_per_call_worst,
            "total_t_gates": t_gates_per_call_worst * simon_queries,
            "notes": "Exponential — only feasible for small n",
        },
        "efficient_oracle": {
            "t_gates_per_query": t_gates_per_call_efficient,
            "total_t_gates": t_gates_per_call_efficient * simon_queries,
            "notes": "Polynomial — requires structured permutation circuit",
        },
        "simon_queries": simon_queries,
    }


def surface_code_overhead(
    logical_qubits: int,
    t_gate_count: int,
    target_error_rate: float = 1e-10,
    physical_gate_error: float = 1e-3,
) -> dict:
    """Estimate surface code overhead for fault-tolerant execution.

    Args:
        logical_qubits: Number of logical qubits needed.
        t_gate_count: Total number of T-gates in the circuit.
        target_error_rate: Desired probability of logical error.
        physical_gate_error: Physical gate error rate of the device.

    Returns:
        Physical resource estimates.
    """
    # Error threshold for surface code: ~1% (0.01)
    p_threshold = 0.01

    # Required code distance: p_logical ~ (p_phys/p_th)^{(d+1)/2}
    # Solve for d: d ~ 2 * log(1/target) / log(p_th/p_phys)
    ratio = physical_gate_error / p_threshold
    if ratio >= 1.0:
        # Below threshold — error correction won't help
        return {
            "feasible": False,
            "reason": "Physical error rate exceeds threshold",
        }

    # Each T-gate can fail, so total error budget = target / t_gate_count
    per_gate_target = target_error_rate / max(t_gate_count, 1)
    d_needed = 2 * math.ceil(
        math.log(1.0 / per_gate_target) / math.log(1.0 / ratio)
    ) + 1
    d_needed = max(d_needed, 3)  # Minimum distance 3

    # Physical qubits per logical qubit: 2 * d^2 (data + syndrome)
    phys_per_logical = 2 * d_needed * d_needed

    # Magic state distillation factory for T-gates
    # One factory ~ 15 * d^2 qubits, produces T-states
    distillation_qubits = 15 * d_needed * d_needed

    total_phys = logical_qubits * phys_per_logical + distillation_qubits

    # Time estimate: surface code cycle ~ 1 microsecond
    # Circuit depth in surface code cycles (each logical gate ~ d cycles)
    # T-gate latency dominated by distillation: ~10*d cycles per T-gate
    # (can be pipelined)
    cycle_time_us = 1.0  # microsecond
    t_gate_latency_cycles = 10 * d_needed
    # Assume some parallelism in T-gate execution
    sequential_t_fraction = 0.3  # 30% of T-gates are sequential
    time_us = sequential_t_fraction * t_gate_count * t_gate_latency_cycles * cycle_time_us

    return {
        "feasible": True,
        "code_distance": d_needed,
        "physical_qubits_per_logical": phys_per_logical,
        "total_physical_qubits": total_phys,
        "distillation_qubits": distillation_qubits,
        "logical_qubits": logical_qubits,
        "estimated_time_us": time_us,
        "estimated_time_seconds": time_us / 1e6,
        "estimated_time_hours": time_us / 3.6e9,
    }


def full_resource_estimate(n: int, use_efficient_oracle: bool = True) -> ResourceEstimate:
    """Complete resource estimate for Simon's attack at n-bit security level.

    Args:
        n: Number of bits (key size of the target cipher).
        use_efficient_oracle: If True, assume polynomial oracle circuit.
                              If False, use exponential truth-table oracle.
    """
    logical_qubits = 2 * n  # Input + output registers

    oracle_costs = estimate_oracle_cost(n)
    if use_efficient_oracle:
        t_gates = oracle_costs["efficient_oracle"]["total_t_gates"]
    else:
        t_gates = oracle_costs["truth_table_oracle"]["total_t_gates"]

    # CX gates: roughly 10x T-gates for structured circuits
    cx_gates = t_gates * 10

    # Depth: T-gates dominate, assume partial parallelism
    depth = int(t_gates * 0.3)

    # Surface code overhead
    target_error = 1e-10
    phys_error = 1e-3
    sc = surface_code_overhead(logical_qubits, t_gates, target_error, phys_error)

    if not sc.get("feasible", False):
        code_distance = -1
        physical_qubits = -1
        physical_with_distill = -1
        exec_time = -1.0
    else:
        code_distance = sc["code_distance"]
        physical_qubits = logical_qubits * sc["physical_qubits_per_logical"]
        physical_with_distill = sc["total_physical_qubits"]
        exec_time = sc["estimated_time_us"]

    return ResourceEstimate(
        n_bits=n,
        logical_qubits=logical_qubits,
        t_gate_count=t_gates,
        cx_gate_count=cx_gates,
        circuit_depth=depth,
        surface_code_distance=code_distance,
        physical_qubits=physical_qubits,
        physical_qubits_with_distillation=physical_with_distill,
        execution_time_us=exec_time,
        total_queries=n,
        target_logical_error_rate=target_error,
    )


def generate_scaling_report(
    bit_sizes: list[int] | None = None,
) -> dict:
    """Generate a resource scaling report for various cipher sizes.

    Shows how resources grow with n, demonstrating feasibility thresholds.
    """
    if bit_sizes is None:
        bit_sizes = [4, 8, 16, 32, 64, 128, 256]

    results = {}
    for n in bit_sizes:
        est = full_resource_estimate(n, use_efficient_oracle=True)
        results[n] = {
            "logical_qubits": est.logical_qubits,
            "physical_qubits": est.physical_qubits_with_distillation,
            "t_gates": est.t_gate_count,
            "code_distance": est.surface_code_distance,
            "time_seconds": est.execution_time_us / 1e6 if est.execution_time_us > 0 else None,
            "time_hours": est.execution_time_us / 3.6e9 if est.execution_time_us > 0 else None,
        }

    return {
        "scaling_data": results,
        "assumptions": {
            "physical_error_rate": 1e-3,
            "target_logical_error": 1e-10,
            "oracle": "efficient (polynomial circuit for permutation)",
            "error_correction": "surface code with magic state distillation",
        },
        "interpretation": {
            "n=4": "Trivially simulable on classical hardware",
            "n=64": "PRINCE-class ciphers; thousands of physical qubits",
            "n=128": "AES-128; millions of physical qubits needed",
            "n=256": "AES-256; tens of millions of physical qubits",
        },
    }


def compare_with_grover(n: int) -> dict:
    """Compare resource requirements: Simon's attack vs Grover's brute-force.

    For a cipher with n-bit key:
        - Grover: O(2^{n/2}) oracle calls, each oracle costs O(n) T-gates
        - Simon (Even-Mansour): O(n) oracle calls, same oracle cost
        - Simon savings: exponential in queries, same per-query cost
    """
    simon_queries = n
    grover_queries = int(2 ** (n / 2) * math.pi / 4)

    oracle_t_cost = n * n * 50  # Per-query T-gate cost (efficient oracle)

    simon_total_t = simon_queries * oracle_t_cost
    grover_total_t = grover_queries * oracle_t_cost

    return {
        "n_bits": n,
        "simon_attack": {
            "oracle_queries": simon_queries,
            "t_gates_total": simon_total_t,
            "requires": "Q2 access (superposition queries) or Q1 + 2^{n/2} classical",
        },
        "grover_brute_force": {
            "oracle_queries": grover_queries,
            "t_gates_total": grover_total_t,
            "requires": "Only Q1 access (quantum circuit for cipher needed)",
        },
        "speedup_factor": grover_total_t / max(simon_total_t, 1),
        "speedup_exponential": f"2^{n//2} / n = {2**(n//2) // n}x",
    }
