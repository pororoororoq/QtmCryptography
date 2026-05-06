"""Tests for quantum resource estimation."""

import pytest
from src.resource_estimation import (
    estimate_oracle_cost,
    surface_code_overhead,
    full_resource_estimate,
    generate_scaling_report,
    compare_with_grover,
    count_gates,
)
from src.simons_algorithm import build_oracle_from_secret


class TestOracleCost:
    def test_cost_grows_with_n(self):
        """Oracle cost should grow with bit size."""
        cost_4 = estimate_oracle_cost(4)
        cost_8 = estimate_oracle_cost(8)
        assert (cost_8["truth_table_oracle"]["t_gates_per_query"] >
                cost_4["truth_table_oracle"]["t_gates_per_query"])

    def test_efficient_cheaper_than_truth_table(self):
        """Efficient oracle should be cheaper for large n."""
        cost = estimate_oracle_cost(16)
        assert (cost["efficient_oracle"]["total_t_gates"] <
                cost["truth_table_oracle"]["total_t_gates"])

    def test_simon_queries_is_n(self):
        """Simon's uses O(n) queries."""
        for n in [4, 8, 16]:
            cost = estimate_oracle_cost(n)
            assert cost["simon_queries"] == n


class TestSurfaceCodeOverhead:
    def test_feasible_with_good_hardware(self):
        """Should be feasible with error rate below threshold."""
        result = surface_code_overhead(
            logical_qubits=8, t_gate_count=1000,
            target_error_rate=1e-6, physical_gate_error=1e-3,
        )
        assert result["feasible"]
        assert result["code_distance"] >= 3
        assert result["total_physical_qubits"] > 8

    def test_infeasible_above_threshold(self):
        """Should report infeasible if error rate >= threshold."""
        result = surface_code_overhead(
            logical_qubits=8, t_gate_count=1000,
            target_error_rate=1e-6, physical_gate_error=0.02,
        )
        assert not result["feasible"]

    def test_more_t_gates_need_higher_distance(self):
        """More T-gates should require higher code distance."""
        r1 = surface_code_overhead(8, 100, 1e-10, 1e-3)
        r2 = surface_code_overhead(8, 10000, 1e-10, 1e-3)
        assert r2["code_distance"] >= r1["code_distance"]


class TestFullEstimate:
    def test_4bit_estimate(self):
        """4-bit estimate should complete and be reasonable."""
        est = full_resource_estimate(4, use_efficient_oracle=True)
        assert est.logical_qubits == 8
        assert est.n_bits == 4
        assert est.total_queries == 4

    def test_128bit_estimate(self):
        """128-bit estimate should produce large numbers."""
        est = full_resource_estimate(128)
        assert est.logical_qubits == 256
        assert est.physical_qubits_with_distillation > 256


class TestScalingReport:
    def test_report_has_all_sizes(self):
        """Report should include all requested bit sizes."""
        report = generate_scaling_report([4, 8, 16])
        assert 4 in report["scaling_data"]
        assert 8 in report["scaling_data"]
        assert 16 in report["scaling_data"]

    def test_physical_qubits_grow(self):
        """Physical qubit count should grow with n."""
        report = generate_scaling_report([4, 8, 16, 32])
        data = report["scaling_data"]
        assert data[32]["physical_qubits"] > data[4]["physical_qubits"]


class TestGroverComparison:
    def test_simon_cheaper_than_grover(self):
        """Simon's should always be cheaper than Grover's."""
        for n in [8, 16, 32]:
            result = compare_with_grover(n)
            assert result["simon_attack"]["t_gates_total"] < result["grover_brute_force"]["t_gates_total"]
            assert result["speedup_factor"] > 1

    def test_speedup_grows_exponentially(self):
        """Speedup should grow exponentially with n."""
        r8 = compare_with_grover(8)
        r16 = compare_with_grover(16)
        assert r16["speedup_factor"] > r8["speedup_factor"]


class TestGateCounting:
    def test_count_gates_small(self):
        """Gate counting should work on a small oracle."""
        oracle = build_oracle_from_secret("110")
        gates = count_gates(oracle, 3)
        assert gates["h"] > 0
        assert gates["cx"] > 0
        assert gates["depth"] > 0
