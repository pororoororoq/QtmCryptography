# Quantum Attacks on Symmetric Cryptography via Simon's Algorithm

Implementations of quantum key-recovery attacks on symmetric ciphers using Simon's algorithm, with Qiskit statevector simulation.

## Background

**Simon's algorithm** solves the hidden period problem in O(n) quantum queries, compared to O(2^{n/2}) classically. Given a function f: {0,1}^n -> {0,1}^n with the promise that f(x) = f(y) iff x XOR y in {0, s}, it recovers the secret period s.

This exponential speedup enables practical attacks against certain symmetric cryptographic constructions when the attacker has **quantum superposition access** to the cipher (the Q2 model).

## Attacks Implemented

### 1. Even-Mansour Cipher (Kuwakado & Morii, 2010)

The Even-Mansour cipher: `E(x) = P(x XOR k1) XOR k2` where P is a public permutation.

**Attack**: Define `f(x) = E(x) XOR P(x)`. Then `f(x) = f(x XOR k1)`, satisfying Simon's promise with period `s = k1`. After recovering k1, compute `k2 = E(0) XOR P(k1)`.

### 2. 3-Round Feistel Network (Kuwakado & Morii, 2010)

A 3-round Feistel with keyed round function `F(x) = S[x XOR k]`.

**Attack**: Define `f(x) = E_L(x, 0) XOR E_L(x, 1)` where E_L is the left half of the ciphertext. This function has Simon period `s = S[k] XOR S[1 XOR k]`. Recovering s reduces the key search space, then a small brute-force finds k.

## Project Structure

```
src/
  simons_algorithm.py   # Core Simon's algorithm (circuit + GF(2) solver)
  even_mansour.py       # Even-Mansour cipher and quantum attack
  feistel_attack.py     # 3-round Feistel cipher and quantum attack
  demo.py               # Demonstration script
tests/
  test_simons_algorithm.py
  test_even_mansour.py
  test_feistel_attack.py
```

## Usage

```bash
pip install qiskit numpy

# Run the demonstration
python -m src.demo

# Run tests
pytest tests/ -v
```

## Limitations

- Block sizes are limited to ~4-8 bits due to statevector simulation constraints (2^{2n} amplitudes).
- The Q2 threat model (quantum superposition queries to a cipher) is not achievable with current technology but is relevant for post-quantum cryptographic analysis.

## References

- Kuwakado, H. & Morii, M. (2010). "Quantum distinguisher between the 3-round Feistel cipher and the random permutation." ISIT 2010.
- Kuwakado, H. & Morii, M. (2012). "Security on the quantum-type Even-Mansour cipher." ISITA 2012.
- Kaplan, M. et al. (2016). "Breaking symmetric cryptosystems using quantum period finding." CRYPTO 2016.
