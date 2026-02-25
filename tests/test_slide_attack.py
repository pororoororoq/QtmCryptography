"""Tests for the quantum slide attack on iterated block ciphers."""

import pytest

from src.slide_attack import SlideBlockCipher, attack_slide_cipher


class TestSlideBlockCipher:
    def test_encrypt_decrypt_roundtrip(self):
        cipher = SlideBlockCipher(n_bits=4, n_rounds=4, key=7)
        for x in range(16):
            assert cipher.decrypt(cipher.encrypt(x)) == x

    def test_permutation_is_bijective(self):
        cipher = SlideBlockCipher(n_bits=4)
        outputs = {cipher.permutation(x) for x in range(16)}
        assert len(outputs) == 16

    def test_encrypt_is_bijective(self):
        cipher = SlideBlockCipher(n_bits=4, n_rounds=3, key=10)
        outputs = {cipher.encrypt(x) for x in range(16)}
        assert len(outputs) == 16

    def test_more_rounds_different_output(self):
        c1 = SlideBlockCipher(n_bits=4, n_rounds=1, key=5)
        c2 = SlideBlockCipher(n_bits=4, n_rounds=3, key=5)
        diffs = sum(1 for x in range(16) if c1.encrypt(x) != c2.encrypt(x))
        assert diffs > 0


class TestSlideAttack:
    def test_attack_1_round(self):
        cipher = SlideBlockCipher(n_bits=4, n_rounds=1, key=10)
        result = attack_slide_cipher(cipher)
        assert result["success"]

    def test_attack_4_rounds(self):
        cipher = SlideBlockCipher(n_bits=4, n_rounds=4, key=10)
        result = attack_slide_cipher(cipher)
        assert result["success"]

    def test_attack_10_rounds(self):
        cipher = SlideBlockCipher(n_bits=4, n_rounds=10, key=10)
        result = attack_slide_cipher(cipher)
        assert result["success"]

    def test_attack_zero_key(self):
        cipher = SlideBlockCipher(n_bits=4, n_rounds=4, key=0)
        result = attack_slide_cipher(cipher)
        assert result["success"]

    def test_attack_max_key(self):
        cipher = SlideBlockCipher(n_bits=4, n_rounds=4, key=15)
        result = attack_slide_cipher(cipher)
        assert result["success"]

    def test_attack_random_key(self):
        cipher = SlideBlockCipher(n_bits=4, n_rounds=6)
        result = attack_slide_cipher(cipher)
        assert result["success"]

    def test_attack_rounds_independent(self):
        """The attack succeeds for any number of rounds with the same key."""
        for r in [1, 2, 5, 8]:
            cipher = SlideBlockCipher(n_bits=4, n_rounds=r, key=13)
            result = attack_slide_cipher(cipher)
            assert result["success"], f"Failed for r={r}"
