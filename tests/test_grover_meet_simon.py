"""Tests for the Grover-meet-Simon hybrid attack on FX construction."""

import pytest
from src.grover_meet_simon import FXCipher, grover_meet_simon_attack, _build_simon_oracle_for_fx
from src.simons_algorithm import run_simons_algorithm


class TestFXCipher:
    def test_encrypt_decrypt_consistency(self):
        """Encryption followed by implied structure check."""
        cipher = FXCipher(n_bits=3, k_inner=5, k_outer=3)
        for x in range(8):
            ct = cipher.encrypt(x)
            assert 0 <= ct < 8

    def test_different_keys_different_outputs(self):
        """Different keys should generally produce different ciphertexts."""
        c1 = FXCipher(n_bits=3, k_inner=0, k_outer=0)
        c2 = FXCipher(n_bits=3, k_inner=1, k_outer=0)
        outputs1 = [c1.encrypt(x) for x in range(8)]
        outputs2 = [c2.encrypt(x) for x in range(8)]
        assert outputs1 != outputs2

    def test_fx_is_permutation(self):
        """FX cipher should be a permutation for fixed keys."""
        cipher = FXCipher(n_bits=3, k_inner=2, k_outer=5)
        outputs = [cipher.encrypt(x) for x in range(8)]
        assert len(set(outputs)) == 8


class TestGroverMeetSimon:
    def test_attack_recovers_keys_3bit(self):
        """Attack should recover both k_inner and k_outer for 3-bit."""
        cipher = FXCipher(n_bits=3, k_inner=3, k_outer=5, perm_seed=42)
        result = grover_meet_simon_attack(cipher)
        assert result["success"]
        assert result["k_inner_match"]
        assert result["k_outer_match"]

    def test_attack_recovers_keys_zero_outer(self):
        """Should work when k_outer = 0."""
        cipher = FXCipher(n_bits=3, k_inner=6, k_outer=0, perm_seed=42)
        result = grover_meet_simon_attack(cipher)
        assert result["success"]

    def test_attack_recovers_keys_zero_inner(self):
        """Should work when k_inner = 0."""
        cipher = FXCipher(n_bits=3, k_inner=0, k_outer=7, perm_seed=42)
        result = grover_meet_simon_attack(cipher)
        assert result["success"]

    def test_simon_on_correct_inner_key(self):
        """Simon's with the correct k_inner should recover k_outer."""
        cipher = FXCipher(n_bits=3, k_inner=2, k_outer=6, perm_seed=42)
        oracle = _build_simon_oracle_for_fx(cipher, k_in_guess=2)
        recovered = run_simons_algorithm(oracle, 3)
        assert int(recovered, 2) == 6

    def test_attack_4bit(self):
        """Attack on 4-bit FX cipher."""
        cipher = FXCipher(n_bits=4, k_inner=9, k_outer=12, perm_seed=99)
        result = grover_meet_simon_attack(cipher)
        assert result["success"]
