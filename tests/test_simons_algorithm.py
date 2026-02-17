"""Tests for Simon's algorithm core."""

import numpy as np
import pytest
from qiskit.quantum_info import Statevector

from src.simons_algorithm import (
    build_oracle_from_secret,
    run_simons_algorithm,
    solve_linear_system_gf2,
)


class TestSolveLinearSystemGF2:
    def test_single_equation(self):
        result = solve_linear_system_gf2([[1, 0]], 2)
        s = [int(b) for b in result]
        # Must satisfy: 1*s[0] + 0*s[1] = 0 mod 2 → s[0] = 0, s[1] free
        assert s[0] == 0
        assert result != "00"  # non-trivial

    def test_full_rank_gives_zero(self):
        equations = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        result = solve_linear_system_gf2(equations, 3)
        assert result == "000"

    def test_two_equations_3bits(self):
        equations = [[1, 1, 0], [0, 1, 1]]
        result = solve_linear_system_gf2(equations, 3)
        s = [int(b) for b in result]
        for eq in equations:
            dot = sum(a * b for a, b in zip(eq, s)) % 2
            assert dot == 0
        assert result != "000"


class TestBuildOracleFromSecret:
    @pytest.mark.parametrize("secret", ["10", "01", "11"])
    def test_oracle_satisfies_promise(self, secret):
        """f(x) = f(x XOR s) for all x."""
        n = len(secret)
        s_int = int(secret, 2)
        oracle = build_oracle_from_secret(secret)

        # Evaluate f on all inputs: |x>|0> -> |x>|f(x)>
        outputs = {}
        for x in range(2**n):
            basis = Statevector.from_int(x, 2 ** (2 * n))
            result = basis.evolve(oracle)
            probs = result.probabilities_dict()
            for bitstring, prob in probs.items():
                if prob > 1e-10:
                    full_val = int(bitstring, 2)
                    out_val = full_val >> n  # output register is high bits
                    outputs[x] = out_val

        # Verify f(x) = f(x XOR s)
        for x in range(2**n):
            assert outputs[x] == outputs[x ^ s_int], (
                f"f({x}) = {outputs[x]} but f({x ^ s_int}) = {outputs[x ^ s_int]}"
            )

    def test_zero_secret_is_bijection(self):
        """Secret = 0...0 means f is 1-to-1."""
        secret = "000"
        n = 3
        oracle = build_oracle_from_secret(secret)

        out_vals = []
        for x in range(8):
            # |x>|0>: input register is qubits 0..n-1 (low bits), output is n..2n-1
            basis = Statevector.from_int(x, 2 ** (2 * n))
            result = basis.evolve(oracle)
            probs = result.probabilities_dict()
            for bitstring, prob in probs.items():
                if prob > 1e-10:
                    full_val = int(bitstring, 2)
                    # Output register is qubits n..2n-1 (high bits of the integer)
                    out_val = full_val >> n
                    out_vals.append(out_val)

        assert len(out_vals) == len(set(out_vals)), "f should be 1-to-1 when s=0"


class TestRunSimonsAlgorithm:
    @pytest.mark.parametrize("secret", ["10", "01", "11", "110", "101"])
    def test_recovers_secret(self, secret):
        n = len(secret)
        oracle = build_oracle_from_secret(secret)
        recovered = run_simons_algorithm(oracle, n)
        assert recovered == secret

    def test_zero_secret(self):
        """s = 0 means the function is 1-to-1; should return all zeros."""
        secret = "00"
        oracle = build_oracle_from_secret(secret)
        recovered = run_simons_algorithm(oracle, 2)
        assert recovered == "00"

    def test_4bit_secret(self):
        secret = "1010"
        oracle = build_oracle_from_secret(secret)
        recovered = run_simons_algorithm(oracle, 4)
        assert recovered == secret
