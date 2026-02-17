"""Tests for the Even-Mansour cipher and its quantum attack."""

import pytest

from src.even_mansour import EvenMansourCipher, attack_even_mansour


class TestEvenMansourCipher:
    def test_encrypt_decrypt_roundtrip(self):
        cipher = EvenMansourCipher(n_bits=8)
        for x in range(256):
            assert cipher.decrypt(cipher.encrypt(x)) == x

    def test_permutation_is_bijective(self):
        cipher = EvenMansourCipher(n_bits=8)
        outputs = {cipher.permutation(x) for x in range(256)}
        assert len(outputs) == 256

    def test_different_keys_different_ciphertexts(self):
        c1 = EvenMansourCipher(n_bits=8, k1=1, k2=2)
        c2 = EvenMansourCipher(n_bits=8, k1=3, k2=4)
        diffs = sum(1 for x in range(256) if c1.encrypt(x) != c2.encrypt(x))
        assert diffs > 0


class TestEvenMansourAttack:
    def test_attack_4bit(self):
        cipher = EvenMansourCipher(n_bits=4, k1=10, k2=5)
        result = attack_even_mansour(cipher)
        assert result["functionally_equivalent"]

    def test_attack_4bit_zero_keys(self):
        cipher = EvenMansourCipher(n_bits=4, k1=0, k2=0)
        result = attack_even_mansour(cipher)
        assert result["functionally_equivalent"]

    def test_attack_4bit_random(self):
        cipher = EvenMansourCipher(n_bits=4)
        result = attack_even_mansour(cipher)
        assert result["functionally_equivalent"]
