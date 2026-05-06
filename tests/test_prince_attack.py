"""Tests for the PRINCE-like cipher attack."""

import pytest
from src.prince_attack import (
    PRINCELikeCipher,
    attack_prince_cipher,
    build_prince_attack_oracle,
    prince_security_analysis,
)
from src.simons_algorithm import run_simons_algorithm


class TestPRINCELikeCipher:
    def test_encrypt_is_permutation(self):
        """Cipher should be a permutation for any fixed key."""
        cipher = PRINCELikeCipher(n_bits=4, k0=5, k1=11)
        outputs = [cipher.encrypt(x) for x in range(16)]
        assert len(set(outputs)) == 16

    def test_encrypt_decrypt_roundtrip(self):
        """Decrypt should invert encrypt."""
        cipher = PRINCELikeCipher(n_bits=4, k0=7, k1=3)
        for x in range(16):
            assert cipher.decrypt(cipher.encrypt(x)) == x

    def test_different_keys_different_outputs(self):
        """Different keys should produce different permutations."""
        c1 = PRINCELikeCipher(n_bits=4, k0=0, k1=0)
        c2 = PRINCELikeCipher(n_bits=4, k0=1, k1=0)
        o1 = [c1.encrypt(x) for x in range(16)]
        o2 = [c2.encrypt(x) for x in range(16)]
        assert o1 != o2

    def test_core_is_permutation(self):
        """Core cipher should be a permutation."""
        cipher = PRINCELikeCipher(n_bits=4, k0=5, k1=9)
        outputs = [cipher.core_encrypt(x) for x in range(16)]
        assert len(set(outputs)) == 16

    def test_core_roundtrip(self):
        """Core decrypt should invert core encrypt."""
        cipher = PRINCELikeCipher(n_bits=4, k0=5, k1=9)
        for x in range(16):
            assert cipher.core_decrypt(cipher.core_encrypt(x)) == x

    def test_uses_prince_sbox_for_4bit(self):
        """4-bit version should use the actual PRINCE S-box."""
        cipher = PRINCELikeCipher(n_bits=4, k0=0, k1=0)
        # PRINCE S-box: 0->B, 1->F, 2->3, ...
        assert cipher.sbox[0] == 0xB
        assert cipher.sbox[1] == 0xF
        assert cipher.sbox[2] == 0x3


class TestPRINCEAttack:
    def test_attack_4bit_specific_keys(self):
        """Attack should recover keys for specific 4-bit cipher."""
        cipher = PRINCELikeCipher(n_bits=4, k0=5, k1=11, seed=42)
        result = attack_prince_cipher(cipher)
        assert result["success"]
        assert result["recovered_k0"] == 5
        assert result["recovered_k1"] == 11

    def test_attack_3bit(self):
        """Attack on 3-bit version."""
        cipher = PRINCELikeCipher(n_bits=3, k0=6, k1=2, seed=42)
        result = attack_prince_cipher(cipher)
        assert result["success"]
        assert result["k0_match"]
        assert result["k1_match"]

    def test_attack_zero_keys(self):
        """Should handle both keys being zero."""
        cipher = PRINCELikeCipher(n_bits=3, k0=0, k1=0, seed=42)
        result = attack_prince_cipher(cipher)
        assert result["success"]

    def test_simon_correct_inner_key(self):
        """Simon with correct k1 should recover k0."""
        cipher = PRINCELikeCipher(n_bits=3, k0=5, k1=3, seed=42)
        oracle = build_prince_attack_oracle(cipher, k1_guess=3)
        recovered = run_simons_algorithm(oracle, 3)
        assert int(recovered, 2) == 5


class TestSecurityAnalysis:
    def test_analysis_returns_data(self):
        """Security analysis should return structured data."""
        analysis = prince_security_analysis(4)
        assert "classical_security" in analysis
        assert "quantum_security" in analysis
        assert "real_prince_64" in analysis
        assert analysis["real_prince_64"]["quantum_gms_bits"] < \
               analysis["real_prince_64"]["classical_security_bits"]
