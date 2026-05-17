# Poster Text: Breaking Encryption with Quantum Computers

---

## INTRODUCTION

Encryption protects every text message, bank login, and credit card tap you make. It scrambles data with a secret key, and security depends on one thing: no computer can find that key fast enough to matter.

**[Place Fig 7: Simon vs Grover]**

- Quantum computers threaten public-key crypto (Shor's algorithm), and the standard defense for symmetric crypto is longer keys. Grover's algorithm halves the security level, so doubling the key length should be enough
- Simon's algorithm breaks that logic. A classical computer needs 10^38 attempts to crack a 128-bit key. Grover's needs 10^19. Simon's needs 128
- We built Simon's algorithm from scratch, attacked three cipher designs used in textbooks and deployed systems, and ran 1,600+ experiments measuring speed and reliability

**[Place Fig 10: Attack Overview]**

- Each cipher reduces to a function with a hidden repeating pattern. Simon's algorithm finds the pattern in O(n) quantum queries, where n is the key length. Classical methods need O(2^(n/2)) queries for the same task

---

## HOW SIMON'S ALGORITHM WORKS

A classical computer tries keys one by one. Simon's algorithm takes a different path: if the encryption function has a repeating pattern (a "period"), a quantum computer can extract that pattern and recover the key.

**[Place Fig 11: Simon's Circuit]**

- The circuit uses 2n qubits: n for input, n for output
- Hadamard gates place all inputs into superposition. The oracle computes f(x) into the output register. A second layer of Hadamard gates interferes the results
- Each measurement produces a vector y satisfying y · s = 0 (mod 2), where s is the secret key
- After n-1 measurements, Gaussian elimination over GF(2) recovers s

**[Place Fig 12: Worked Example]**

- With a 3-bit key (s = 101), the function maps 8 inputs to 4 outputs. Each input shares its output with one partner: 000 and 101 both map to 010, 001 and 100 both map to 110, and so on. The distance between partners is 101, the hidden period
- Three measurements yield three equations. Gaussian elimination mod 2 solves the system: s = 101, key recovered

---

## THREE CIPHERS, THREE ATTACKS

Many cipher designs create hidden periods by accident. We attacked three different designs to confirm the vulnerability is structural, not specific to one cipher.

### Attack 1: Even-Mansour

**[Place Fig 13: Even-Mansour Attack]**

- **The cipher:** XOR a secret key k1, apply a public permutation P, XOR another secret key k2. Written as E(x) = P(x XOR k1) XOR k2. PRINCE, a cipher used in IoT devices and smart cards, uses this structure
- **The reduction:** Define f(x) = E(x) XOR P(x). This function repeats with period k1. Simon's algorithm recovers k1, and k2 follows from one encryption query
- **The lesson:** The simplest practical cipher falls in O(n) queries

### Attack 2: 3-Round Feistel Network

**[Place Fig 14: Feistel Attack]**

- **The cipher:** Splits data in half and mixes the halves through multiple rounds using a round function F(x) = S[x XOR k]. DES, the former U.S. encryption standard, uses this architecture
- **The reduction:** Encrypt two inputs differing only in the right half, then XOR the left halves of the ciphertexts. The result repeats with a period derived from the key. Simon's algorithm extracts it, and a short brute-force search recovers k
- **The lesson:** Multi-round, well-studied designs are vulnerable too

### Attack 3: Quantum Slide Attack

**[Place Fig 15: Slide Attack]**

- **The cipher:** Applies the same round function Fk(x) = P(x XOR k) for r rounds. More rounds should mean more security
- **The reduction:** Define f(x) = Fk(x) XOR P(x). This function repeats with period k. The attack uses one round and ignores every other round
- **The lesson:** We tested 1 round through 100 rounds: identical success rate, identical speed. Adding rounds provides zero additional protection

---

## RESULTS

### Does it work?

**[Place Fig 6: Success Rates]**

- All four attacks recover the key 100% of the time for key sizes n >= 4, across 50 trials each
- The slide attack drops to 40% at n=3 (too few qubits to resolve the pattern) and reaches 100% at n=4

### How efficient is it?

**[Place Fig 3: Query Complexity]**

- The measured query count averages 1.1n, close to the theoretical minimum of n-1
- A 128-bit key needs about 141 quantum measurements. A classical computer needs 10^19 attempts

**[Place Fig 5: Rank Convergence]**

- After n queries, over 99% of trials have solved the key. The convergence follows a sharp S-curve

### Does adding more rounds help?

**[Place Fig 2: Slide Round-Independence]**

- The slide attack produces flat lines from 1 to 100 rounds: same success rate, same execution time
- "More rounds = more security" does not hold against a quantum adversary with access to the round function

### How does noise affect it?

**[Place Fig 1: Noise Phase Transition]**

- We corrupted up to 40% of measurements with random noise. The algorithm maintains near-perfect success below 30% noise, then collapses at 35-40% through a sharp phase transition
- Current quantum hardware already achieves error rates below 30%, placing the attack within reach of near-term devices

**[Place Fig 4: Timing Curves]**

- Classical simulation time grows exponentially with key size, confirming that scaling these attacks requires quantum hardware

---

## WHAT THIS MEANS FOR REAL ENCRYPTION

The experiments above used 3-8 bit keys. Real ciphers use 64-128+ bit keys. We tested whether the attack scales.

**[Place Fig 16: PRINCE Timing]**

- We ran Simon's algorithm on PRINCE-like ciphers from n=3 to n=127. The quantum attack cracked a 127-bit key in 21 milliseconds. Classical brute-force timed out at n=27 (57 seconds), and the extrapolated classical curve crosses the age of the universe around n=60

**[Place Fig 9: PRINCE Security Reduction]**

- PRINCE-64 is deployed in IoT devices, smart cards, and embedded systems. It uses the Even-Mansour structure from Attack 1
- Classical security: 127 bits (10^38 operations). Grover-meet-Simon hybrid security: 37 bits (10^11 operations). That is a 90-bit reduction

**[Place Fig 8: Resource Estimates]**

- These attacks need quantum computers that do not exist yet:
  - PRINCE: ~371,000 physical qubits
  - AES-128: ~802,000 physical qubits
  - AES-256: ~1.58 million physical qubits
- IBM's largest current chip has 1,121 qubits. Projected timelines suggest machines this size may arrive within 10-15 years

### Takeaways

- Simon's algorithm reduces key recovery from 10^19 attempts to ~128 measurements for a 128-bit key
- All attacks succeed 100% of the time at n >= 4, using about 1.1n queries
- Noise below 30% does not degrade performance. Above 35%, success collapses
- Round count has no effect on the slide attack
- PRINCE-64 drops from 127-bit to 37-bit security under the quantum hybrid attack
- Data encrypted today can be stored and decrypted when quantum hardware matures. Cipher designs need to account for this timeline

---

## DEFENSES AND FUTURE DIRECTIONS

Our attacks exploit specific algebraic structure in cipher designs. Defenses exist, and they fall into two categories.

**Symmetric crypto (what we attacked):**

- Simon's algorithm requires the cipher to produce a function with a hidden period. Not all ciphers do this. AES in standard modes does not have the Even-Mansour or slide structure our attacks require
- The vulnerability is design-specific: Even-Mansour, Feistel with identical round keys, and iterated ciphers with a single repeated round function all create exploitable periods. Designers who avoid these patterns eliminate the attack surface
- Against Grover's algorithm (generic key search), doubling the key length restores security. AES-256 maintains 128-bit security even against a quantum adversary running Grover
- The Q2 threat model (quantum superposition queries to the cipher) is required for our attacks. Whether a real-world system allows superposition queries depends on the deployment: hardware tokens may expose this interface, while network protocols likely do not

**Public-key crypto (RSA, Diffie-Hellman, elliptic curves):**

- NIST finalized three post-quantum standards in August 2024 (FIPS 203, 204, 205), replacing the algorithms Shor's algorithm breaks
- **Lattice-based (ML-KEM, ML-DSA):** Security relies on finding the closest point in a high-dimensional lattice with noise added. No known quantum algorithm solves this efficiently. These handle key exchange and digital signatures
- **Hash-based signatures (SLH-DSA):** Security depends only on hash functions being one-way. No algebraic structure for a quantum algorithm to exploit. Signatures are large but the security assumption is minimal
- **Code-based (Classic McEliece):** Decoding random error-correcting codes has resisted attack since 1978, including quantum approaches. Public keys are hundreds of kilobytes, which limits some applications

**The open question:** Our work shows that hidden algebraic structure in symmetric ciphers creates quantum vulnerabilities the designers did not anticipate. PRINCE was published in 2012 and analyzed for years before the Grover-meet-Simon attack reduced its security from 127 to 37 bits. Future cipher designs need formal analysis against quantum period-finding, not only against classical cryptanalysis.

---

## ACKNOWLEDGEMENTS

- Kuwakado & Morii (2010, 2012): first Simon's algorithm attacks on Even-Mansour and Feistel
- Kaplan et al. (2016): quantum slide attack framework
- Leander & May (2017): Grover-meet-Simon hybrid for PRINCE/FX
- Jaques et al. (2020): AES quantum resource estimation
- Implemented with IBM Qiskit for quantum circuit simulation
