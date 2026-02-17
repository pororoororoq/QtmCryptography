"""Tests for the 3-round Feistel network and its quantum attack."""

import pytest

from src.feistel_attack import (
    Feistel3RoundNonlinear,
    attack_feistel_3round,
)


class TestFeistel3RoundNonlinear:
    def test_deterministic_encryption(self):
        cipher = Feistel3RoundNonlinear(half_bits=4, key=5)
        l1, r1 = cipher.encrypt(3, 7)
        l2, r2 = cipher.encrypt(3, 7)
        assert (l1, r1) == (l2, r2)

    def test_different_keys_different_outputs(self):
        c1 = Feistel3RoundNonlinear(half_bits=4, key=3, seed=42)
        c2 = Feistel3RoundNonlinear(half_bits=4, key=7, seed=42)
        diffs = 0
        for l in range(16):
            for r in range(16):
                if c1.encrypt(l, r) != c2.encrypt(l, r):
                    diffs += 1
        assert diffs > 0

    def test_sbox_is_permutation(self):
        cipher = Feistel3RoundNonlinear(half_bits=4, key=0)
        outputs = set(cipher.sbox)
        assert len(outputs) == 16


class TestFeistelAttack:
    def test_attack_4bit_key0(self):
        cipher = Feistel3RoundNonlinear(half_bits=4, key=0, seed=42)
        result = attack_feistel_3round(cipher)
        assert result["success"]

    def test_attack_4bit_key5(self):
        cipher = Feistel3RoundNonlinear(half_bits=4, key=5, seed=42)
        result = attack_feistel_3round(cipher)
        assert result["success"]

    def test_attack_4bit_key15(self):
        cipher = Feistel3RoundNonlinear(half_bits=4, key=15, seed=42)
        result = attack_feistel_3round(cipher)
        assert result["success"]

    def test_attack_4bit_random(self):
        cipher = Feistel3RoundNonlinear(half_bits=4)
        result = attack_feistel_3round(cipher)
        assert result["success"]
