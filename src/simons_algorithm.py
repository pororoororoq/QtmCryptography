"""
Simon's Algorithm — core implementation.

Simon's problem: Given f: {0,1}^n -> {0,1}^n with the promise that there
exists s in {0,1}^n such that f(x) = f(y) iff x XOR y in {0, s}, find s.

Classically this requires O(2^{n/2}) queries (birthday bound).
Quantumly Simon's algorithm solves it in O(n) queries.

The algorithm:
    1. Prepare |0^n>|0^n>
    2. Apply H^{⊗n} to the first register
    3. Apply U_f (oracle) to get sum_x |x>|f(x)>
    4. Apply H^{⊗n} to the first register
    5. Measure the first register -> get y such that y · s = 0
    6. Repeat O(n) times to collect n-1 linearly independent equations
    7. Solve the linear system over GF(2) to recover s

Bitstring convention: all bitstrings are MSB-first (big-endian).
  "1010" means the integer 10.  Position 0 in the string is the MSB.
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


def build_simon_circuit(
    oracle: QuantumCircuit,
    n: int,
) -> QuantumCircuit:
    """Build a single-shot Simon circuit.

    Args:
        oracle: A 2n-qubit circuit implementing U_f: |x>|y> -> |x>|y XOR f(x)>.
        n: Number of input bits.

    Returns:
        A QuantumCircuit that, when measured on the first n qubits,
        yields y with y · s = 0.
    """
    qc = QuantumCircuit(2 * n, n)

    # Step 1: Hadamard on input register
    qc.h(range(n))

    # Step 2: Apply oracle
    qc.compose(oracle, inplace=True)

    # Step 3: Hadamard on input register again
    qc.h(range(n))

    # Step 4: Measure input register
    qc.measure(range(n), range(n))

    return qc


def solve_linear_system_gf2(equations: list[list[int]], n: int) -> str:
    """Solve a system of equations y · s = 0 over GF(2).

    Uses Gaussian elimination to find the null space, then returns
    the non-trivial solution s (if one exists).

    Args:
        equations: List of binary vectors y_i (each of length n).
        n: Dimension.

    Returns:
        The secret string s as a MSB-first bitstring, or '0'*n if only
        the trivial solution exists (meaning s = 0^n, i.e. f is 1-to-1).
    """
    matrix = np.array(equations, dtype=int) % 2

    # Gaussian elimination over GF(2)
    pivots = []
    row = 0
    for col in range(n):
        # Find pivot
        found = None
        for r in range(row, len(matrix)):
            if matrix[r, col] == 1:
                found = r
                break
        if found is None:
            continue
        # Swap
        matrix[[row, found]] = matrix[[found, row]]
        # Eliminate
        for r in range(len(matrix)):
            if r != row and matrix[r, col] == 1:
                matrix[r] = (matrix[r] + matrix[row]) % 2
        pivots.append(col)
        row += 1

    rank = len(pivots)
    if rank >= n:
        return "0" * n

    # Find a free variable (column not in pivots)
    free_cols = [c for c in range(n) if c not in pivots]
    free_col = free_cols[0]

    # Back-substitute: set free variable to 1, solve for pivot variables
    s = [0] * n
    s[free_col] = 1

    pivot_matrix = matrix[:rank]
    for i, pcol in enumerate(pivots):
        s[pcol] = pivot_matrix[i, free_col]

    return "".join(str(b) for b in s)


def _rank_gf2(equations: list[list[int]], n: int) -> int:
    """Compute the rank of a binary matrix over GF(2).

    np.linalg.matrix_rank works over the reals and gives wrong results
    for GF(2) (e.g., [1,1] and [1,0] and [0,1] have rank 3 over R but
    rank 2 over GF(2) since [1,1] = [1,0] + [0,1] mod 2).
    """
    matrix = np.array(equations, dtype=int) % 2
    row = 0
    for col in range(n):
        found = None
        for r in range(row, len(matrix)):
            if matrix[r, col] == 1:
                found = r
                break
        if found is None:
            continue
        matrix[[row, found]] = matrix[[found, row]]
        for r in range(len(matrix)):
            if r != row and matrix[r, col] == 1:
                matrix[r] = (matrix[r] + matrix[row]) % 2
        row += 1
    return row


def _sample_y_bits(oracle: QuantumCircuit, n: int) -> list[int]:
    """Run one round of Simon's circuit and return the measurement as a
    MSB-first list of bits.

    Returns:
        List of n ints, where index 0 is the MSB (qubit n-1)
        and index n-1 is the LSB (qubit 0).
    """
    qc = QuantumCircuit(2 * n)
    qc.h(range(n))
    qc.compose(oracle, inplace=True)
    qc.h(range(n))

    sv = Statevector.from_instruction(qc)
    outcome = sv.sample_memory(1)[0]

    # outcome is Qiskit big-endian: outcome[0] = qubit 2n-1, outcome[2n-1] = qubit 0.
    # Input register = qubits 0..n-1.
    # MSB-first: y_bits[k] = qubit n-1-k = outcome[2n - 1 - (n-1-k)] = outcome[n + k].
    return [int(outcome[n + k]) for k in range(n)]


def run_simons_algorithm(
    oracle: QuantumCircuit,
    n: int,
    max_iterations: int | None = None,
) -> str:
    """Run Simon's algorithm end-to-end using statevector simulation.

    Args:
        oracle: The 2n-qubit oracle circuit for f.
        n: Number of input bits.
        max_iterations: Maximum sampling rounds (default: 10*n).

    Returns:
        The recovered secret string s (MSB-first bitstring).
        Returns '0'*n if f is 1-to-1 (s = 0).
    """
    if max_iterations is None:
        max_iterations = 10 * n

    equations: list[list[int]] = []
    rank_reached_n_minus_1 = False
    extra_after_rank = 0

    for _ in range(max_iterations):
        y_bits = _sample_y_bits(oracle, n)

        if all(b == 0 for b in y_bits):
            continue

        equations.append(y_bits)

        rank = _rank_gf2(equations, n)

        if rank >= n:
            # Full rank means only the trivial solution: s = 0
            return "0" * n

        if rank >= n - 1:
            if not rank_reached_n_minus_1:
                rank_reached_n_minus_1 = True
                extra_after_rank = 0
            else:
                extra_after_rank += 1
                # For s != 0, all y satisfy y·s = 0, so rank can never
                # exceed n-1.  Collect a few extra samples to be sure we
                # aren't in the s=0 case (where rank CAN reach n).
                if extra_after_rank >= n:
                    break

    if not equations:
        return "0" * n

    return solve_linear_system_gf2(equations, n)


def build_oracle_from_secret(s: str) -> QuantumCircuit:
    """Build a Simon oracle for a known secret string s.

    This constructs U_f such that f(x) = f(x XOR s) by implementing:
        - Copy input to output via CNOTs.
        - For each bit position where s = 1, CNOT from a fixed input qubit
          (the first position where s = 1) to the corresponding output qubit.
        - This creates the 2-to-1 structure required by Simon's promise.

    Args:
        s: The secret as a MSB-first bitstring.  "1010" means integer 10.

    Returns:
        A 2n-qubit QuantumCircuit implementing the oracle.
    """
    n = len(s)
    qc = QuantumCircuit(2 * n)

    # If s is all zeros, f is 1-to-1: just copy input to output
    if all(c == "0" for c in s):
        for i in range(n):
            qc.cx(i, n + i)
        return qc

    # s is MSB-first.  s[k] = bit (n-1-k), which lives on qubit (n-1-k).
    j_str = s.index("1")        # first '1' position in the string
    j_qubit = n - 1 - j_str     # corresponding qubit index

    # Copy input register to output register
    for i in range(n):
        qc.cx(i, n + i)

    # For each position where s has a 1, CNOT from j_qubit to that output qubit.
    for k in range(n):
        if s[k] == "1":
            target_qubit = n - 1 - k
            qc.cx(j_qubit, n + target_qubit)

    return qc
