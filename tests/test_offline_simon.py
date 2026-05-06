"""Tests for Q1 offline Simon's attack."""

import pytest
from src.offline_simon import (
    classical_query_phase,
    build_offline_oracle,
    offline_simon_attack,
    compare_q1_vs_q2,
)
from src.even_mansour import EvenMansourCipher
from src.simons_algorithm import run_simons_algorithm


class TestClassicalQueryPhase:
    def test_collects_all_pairs(self):
        """Should collect all input-output pairs for small n."""
        cipher = EvenMansourCipher(n_bits=3, k1=5, k2=3)
        data = classical_query_phase(cipher)
        assert len(data) == 8
        for x in range(8):
            assert data[x] == cipher.encrypt(x)

    def test_partial_queries(self):
        """Should collect only requested number of queries."""
        cipher = EvenMansourCipher(n_bits=4, k1=10, k2=7)
        data = classical_query_phase(cipher, n_queries=8)
        assert len(data) == 8


class TestOfflineOracle:
    def test_oracle_produces_correct_function(self):
        """Offline oracle should compute f(x) = E(x) XOR P(x)."""
        cipher = EvenMansourCipher(n_bits=3, k1=6, k2=2)
        data = classical_query_phase(cipher)
        perm_table = [cipher.permutation(x) for x in range(8)]
        oracle = build_offline_oracle(data, perm_table, n=3)

        # Run Simon's on this oracle — should recover k1
        recovered = run_simons_algorithm(oracle, 3)
        assert int(recovered, 2) == 6


class TestOfflineSimonAttack:
    def test_recovers_keys_3bit(self):
        """Full offline attack should recover functionally equivalent keys."""
        cipher = EvenMansourCipher(n_bits=3, k1=2, k2=6)
        result = offline_simon_attack(cipher)
        assert result["success"]
        assert result["recovered_k1"] == 2
        assert result["threat_model"] == "Q1 (classical queries, offline quantum)"

    def test_recovers_keys_4bit(self):
        """Offline attack on 4-bit cipher."""
        cipher = EvenMansourCipher(n_bits=4, k1=11, k2=9)
        result = offline_simon_attack(cipher)
        assert result["success"]
        assert result["recovered_k1"] == 11

    def test_zero_key(self):
        """Should handle k1 = 0 (identity period)."""
        cipher = EvenMansourCipher(n_bits=3, k1=0, k2=4)
        result = offline_simon_attack(cipher)
        assert result["success"]
        assert result["recovered_k1"] == 0


class TestQ1VsQ2:
    def test_both_attacks_succeed(self):
        """Both Q1 and Q2 attacks should succeed on the same cipher."""
        cipher = EvenMansourCipher(n_bits=3, k1=7, k2=2)
        comparison = compare_q1_vs_q2(cipher)
        assert comparison["q1_attack"]["success"]
        assert comparison["q2_attack"]["success"]
        assert comparison["q1_attack"]["requires_quantum_network"] is False
        assert comparison["q2_attack"]["requires_quantum_network"] is True
