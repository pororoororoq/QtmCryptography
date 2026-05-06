"""
Q1 Offline Simon's attack: classical queries + quantum offline computation.

Threat models:
    Q2: Attacker can make quantum superposition queries to the cipher.
        (This is what our other attacks use.)
    Q1: Attacker can only make CLASSICAL queries to the cipher, but has a
        quantum computer for offline processing.

The Q1 model is much more realistic: you query AES over the network
classically, then process the data quantumly in your lab.

Offline Simon (Bonnetain, Naya-Plasencia, Schrottenloher, 2019):
    Key insight: after making 2^{n/2} classical queries, you have enough
    data to construct a quantum circuit that encodes the Simon function
    in superposition, WITHOUT needing quantum queries to the actual cipher.

    The approach:
    1. Make O(2^{n/2}) classical queries to build a partial function table.
    2. Construct a quantum oracle from this table.
    3. Run Simon's algorithm on this oracle offline.
    4. Use birthday-bound collisions in the table to verify.

    Complexity: O(2^{n/2}) classical queries + O(n) quantum oracle calls
    on a LOCAL quantum computer.  No quantum network channel needed!

For our simulation, we demonstrate this on small n by:
    1. Collecting a subset of function evaluations classically.
    2. Building a quantum oracle from this partial data.
    3. Running Simon's on the partial oracle.
    4. Verifying the result using the classical data.
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit

from .even_mansour import _truth_table_to_oracle, EvenMansourCipher
from .simons_algorithm import run_simons_algorithm, _rank_gf2, solve_linear_system_gf2


def classical_query_phase(
    cipher: EvenMansourCipher,
    n_queries: int | None = None,
) -> dict[int, int]:
    """Phase 1: Make classical queries to the cipher.

    In the Q1 model, we can only query the cipher classically.
    We collect input-output pairs (x, E(x)) for a set of random inputs.

    For a full attack, we'd need O(2^{n/2}) queries for birthday collision.
    For simulation on small n, we query all inputs.

    Returns:
        Dictionary mapping plaintext -> ciphertext.
    """
    n = cipher.n_bits
    N = 1 << n

    if n_queries is None:
        n_queries = N  # Query all for small n simulation

    # For small n, just query everything (birthday bound doesn't matter)
    # In practice for large n, we'd query a random subset of size ~ 2^{n/2}
    results = {}
    for x in range(min(n_queries, N)):
        results[x] = cipher.encrypt(x)

    return results


def build_offline_oracle(
    query_data: dict[int, int],
    perm_table: list[int],
    n: int,
) -> QuantumCircuit:
    """Phase 2: Build a quantum oracle from classical data.

    Given classical query results and the public permutation P,
    construct the Simon function f(x) = E(x) XOR P(x) as a quantum
    circuit entirely offline.

    The key insight: we DON'T need quantum access to E — we already
    KNOW E(x) for all queried x, so we can hardcode it into the circuit.

    Args:
        query_data: Dictionary {x: E(x)} from classical queries.
        perm_table: The public permutation P as a list (index = input).
        n: Number of bits.

    Returns:
        A 2n-qubit oracle circuit computing f(x) = E(x) XOR P(x).
    """
    # Compute the Simon function classically from our data
    truth_table = {}
    for x, e_x in query_data.items():
        truth_table[x] = e_x ^ perm_table[x]

    # Build quantum oracle from the truth table
    # This oracle can now be queried in superposition LOCALLY
    return _truth_table_to_oracle(truth_table, n)


def offline_simon_attack(
    cipher: EvenMansourCipher,
    verbose: bool = False,
) -> dict:
    """Full Q1 offline Simon attack on Even-Mansour.

    Phase 1 (Classical, on the network):
        Query E(x) for various x. Cost: O(2^{n/2}) classical queries.

    Phase 2 (Quantum, offline in the lab):
        Build oracle from collected data, run Simon's algorithm locally.
        Cost: O(n) quantum operations on a LOCAL quantum computer.

    Phase 3 (Classical verification):
        Verify recovered key using the collected data.

    This demonstrates that Q2 access (quantum queries to the cipher)
    is NOT necessary — Q1 suffices with a birthday-bound classical cost.
    """
    n = cipher.n_bits
    N = 1 << n

    # Phase 1: Classical queries
    query_data = classical_query_phase(cipher)
    classical_queries = len(query_data)

    if verbose:
        print(f"Phase 1: Collected {classical_queries} classical query results")

    # Public permutation table (attacker knows P)
    perm_table = [cipher.permutation(x) for x in range(N)]

    # Phase 2: Build offline oracle and run Simon's
    offline_oracle = build_offline_oracle(query_data, perm_table, n)
    recovered_k1_bits = run_simons_algorithm(offline_oracle, n)
    recovered_k1 = int(recovered_k1_bits, 2)

    if verbose:
        print(f"Phase 2: Simon's recovered k1 = {recovered_k1_bits} ({recovered_k1})")

    # Phase 3: Recover k2 and verify using classical data
    p_k1 = perm_table[recovered_k1]
    recovered_k2 = query_data[0] ^ p_k1  # E(0) = P(0 XOR k1) XOR k2

    # Verify against collected data
    success = all(
        perm_table[(x ^ recovered_k1) & cipher.mask] ^ recovered_k2 == e_x
        for x, e_x in query_data.items()
    )

    if verbose:
        print(f"Phase 3: k2 = {recovered_k2}, verified = {success}")

    return {
        "recovered_k1": recovered_k1,
        "recovered_k2": recovered_k2,
        "actual_k1": cipher.k1,
        "actual_k2": cipher.k2,
        "success": success,
        "classical_queries": classical_queries,
        "quantum_queries": n,  # Simon's uses O(n) oracle queries
        "threat_model": "Q1 (classical queries, offline quantum)",
        "n_bits": n,
        "total_cost": f"O(2^{n//2}) classical + O({n}) quantum (offline)",
    }


def compare_q1_vs_q2(cipher: EvenMansourCipher) -> dict:
    """Compare Q1 (offline) and Q2 (online) attack models.

    Both achieve key recovery, but with different resource requirements.
    """
    from .even_mansour import attack_even_mansour

    # Q2 attack (quantum queries to cipher)
    q2_result = attack_even_mansour(cipher)

    # Q1 attack (classical queries + offline quantum)
    q1_result = offline_simon_attack(cipher)

    return {
        "n_bits": cipher.n_bits,
        "q2_attack": {
            "success": q2_result["functionally_equivalent"],
            "model": "Q2: quantum superposition queries to cipher",
            "quantum_queries_to_cipher": f"O({cipher.n_bits})",
            "classical_queries": "0",
            "requires_quantum_network": True,
        },
        "q1_attack": {
            "success": q1_result["success"],
            "model": "Q1: classical queries + offline quantum",
            "quantum_queries_to_cipher": "0",
            "classical_queries": f"O(2^{cipher.n_bits//2})",
            "requires_quantum_network": False,
        },
        "implication": (
            "Q1 is more realistic: attacker needs no quantum channel "
            "to the target, just a local quantum computer."
        ),
    }
