# Poster Text: Breaking Encryption with Quantum Computers
### Jake Kim — Quantum and Optics Lab, TJHSST

---

## INTRODUCTION

Encryption protects every text message, bank login, and credit card tap you make. It scrambles data with a secret key, and security depends on one thing: no computer can find that key fast enough to matter.

**[Place Fig 7: Simon vs Grover]**

- Shor's algorithm breaks public-key cryptography (RSA, Diffie-Hellman, elliptic curves) in polynomial time (Shor, 1997). NIST responded with post-quantum standards FIPS 203, 204, and 205 in August 2024 (NIST, 2024). Symmetric-key cryptography faces a different threat
- Grover's algorithm (Grover, 1996) halves the security level of any block cipher, and practitioners treat this as solved: double the key length, migrate from AES-128 to AES-256 (Bernstein, 2009). That response assumes generic search is the only quantum speedup available against symmetric constructions
- Kuwakado and Morii (2010, 2012) proved it wrong. In the Q2 threat model, where an adversary queries the encryption oracle in quantum superposition (Boneh & Zhandry, 2013; Gagliardoni et al., 2016), certain symmetric schemes fall to exponential quantum speedups through Simon's algorithm (Simon, 1997), not Grover search
- Simon's algorithm finds hidden periods in O(n) quantum queries, where classical methods require O(2^(n/2)) (Simon, 1997). A classical computer needs 10^38 attempts to crack a 128-bit key. Grover's needs 10^19. Simon's needs 128

**[Place Fig 10: Attack Overview]**

- Kaplan et al. (2016) showed at CRYPTO 2016 that Simon's algorithm breaks a wide array of symmetric constructions in the Q2 model, including CBC-MAC, PMAC, GMAC, GCM, and OCB. The vulnerability extends well beyond the three ciphers we attack here
- The Luby-Rackoff theorem (Luby & Rackoff, 1988) guarantees that a 3-round Feistel network with pseudorandom round functions resists classical chosen-plaintext attacks. The quantum attack collapses that guarantee (Kuwakado & Morii, 2010)
- Prior work on these attacks was theoretical. Few researchers had built end-to-end executable circuits, and no single framework compared how Simon's algorithm works across Even-Mansour, Feistel, and slide settings (Bonnetain & Jaques, 2022). We fill that gap with a complete, open-source implementation and 1,600+ experimental trials

---

## HOW SIMON'S ALGORITHM WORKS

A classical computer tries keys one by one. Simon's algorithm takes a different path: if the encryption function has a repeating pattern (a "period"), a quantum computer can extract that pattern and recover the key (Simon, 1997).

**[Place Fig 11: Simon's Circuit]**

- The circuit uses 2n qubits: n for input, n for output (Nielsen & Chuang, 2010)
- Hadamard gates place all inputs into superposition. The oracle computes f(x) into the output register. A second layer of Hadamard gates interferes the results
- Each measurement produces a vector y satisfying y · s = 0 (mod 2), where s is the secret key
- After n-1 measurements, Gaussian elimination over GF(2) recovers s. Standard floating-point linear algebra (e.g., numpy) gives incorrect results over GF(2), so we implemented custom modular arithmetic

**[Place Fig 12: Worked Example]**

- With a 3-bit key (s = 101), the function maps 8 inputs to 4 outputs. Each input shares its output with one partner: 000 and 101 both map to 010, 001 and 100 both map to 110, and so on. The distance between partners is 101, the hidden period
- Three measurements yield three equations. Gaussian elimination mod 2 solves the system: s = 101, key recovered

---

## THREE CIPHERS, THREE ATTACKS

Many cipher designs create hidden periods by accident. We attacked three different designs to confirm the vulnerability is structural, not specific to one cipher. All three share a common Simon's algorithm core, implemented as quantum circuits on the Qiskit statevector backend (Qiskit Contributors, 2024).

### Attack 1: Even-Mansour

**[Place Fig 13: Even-Mansour Attack]**

- **The cipher:** E(x) = P(x XOR k1) XOR k2, where P is a public permutation and k1, k2 are secret keys (Even & Mansour, 1997). Its classical security has a tight lower bound of T = Omega(2^n / D) for D known plaintexts (Dunkelman et al., 2012). PRINCE, a cipher used in IoT devices and smart cards (Borghoff et al., 2012), uses this structure
- **The reduction:** Define f(x) = E(x) XOR P(x). This function repeats with period k1 (Kuwakado & Morii, 2012). Simon's algorithm recovers k1, and k2 follows as k2 = E(0) XOR P(k1)
- **The lesson:** A cipher with a proven classical security bound falls in O(n) quantum queries

### Attack 2: 3-Round Feistel Network

**[Place Fig 14: Feistel Attack]**

- **The cipher:** Splits data in half and mixes the halves through multiple rounds using a round function F(x) = S[x XOR k] (Luby & Rackoff, 1988). DES, the former U.S. encryption standard, uses this architecture
- **The reduction:** Construct f(x) = E_L(x, 0) XOR E_L(x, 1), where E_L is the left half of the ciphertext. This function has period s = S[k] XOR S[1 XOR k] (Kuwakado & Morii, 2010; Kaplan et al., 2016). Simon's algorithm extracts s, and a short brute-force search recovers k
- **The lesson:** The Luby-Rackoff security guarantee, which holds against all classical chosen-plaintext adversaries, provides no protection in the Q2 model

### Attack 3: Quantum Slide Attack

**[Place Fig 15: Slide Attack]**

- **The cipher:** Applies the same round function Fk(x) = P(x XOR k) for r rounds. More rounds should mean more security (Biryukov & Wagner, 1999)
- **The reduction:** Define f(x) = Fk(x) XOR P(x). This function repeats with period k. The attack uses one round and ignores every other round (Kaplan et al., 2016; Bonnetain et al., 2019). The classical slide attack requires O(2^(n/2)) known plaintexts to find a slide pair; the quantum version recovers the key in O(n) queries
- **The lesson:** We tested 1 round through 100 rounds: identical success rate, identical speed. Adding rounds provides zero additional protection

---

## RESULTS

### Does it work?

**[Place Fig 6: Success Rates]**

- All four attacks recover the key 100% of the time for key sizes n >= 4, across 50 trials each
- The slide attack drops to 40% at n=3 (too few qubits to resolve the pattern) and reaches 100% at n=4

### How efficient is it?

**[Place Fig 3: Query Complexity]**

- The measured query count averages 1.1n, close to the theoretical minimum of n-1 (Simon, 1997)
- A 128-bit key needs about 141 quantum measurements. A classical computer needs 10^19 attempts

**[Place Fig 5: Rank Convergence]**

- After n queries, over 99% of trials have solved the key. The convergence follows a sharp S-curve

### Does adding more rounds help?

**[Place Fig 2: Slide Round-Independence]**

- The slide attack produces flat lines from 1 to 100 rounds: same success rate, same execution time
- This confirms the theoretical prediction of Kaplan et al. (2016): round count is irrelevant against a quantum adversary with access to the round function

### How does noise affect it?

**[Place Fig 1: Noise Phase Transition]**

- We corrupted up to 40% of measurements with random noise. The algorithm maintains near-perfect success below 30% noise, then collapses at 35-40% through a sharp phase transition
- Current quantum hardware already achieves error rates below 30%, placing the attack within reach of near-term devices

**[Place Fig 4: Timing Curves]**

- Classical simulation time grows exponentially with key size, confirming that scaling these attacks requires quantum hardware. This is expected: statevector simulation requires O(2^(2n)) memory for an n-bit cipher (Nielsen & Chuang, 2010)

---

## WHAT THIS MEANS FOR REAL ENCRYPTION

The experiments above used 3-8 bit keys. Real ciphers use 64-128+ bit keys. We tested whether the attack scales.

**[Place Fig 16: PRINCE Timing]**

- We ran Simon's algorithm on PRINCE-like ciphers (Borghoff et al., 2012) from n=3 to n=127. The quantum attack cracked a 127-bit key in 21 milliseconds. Classical brute-force timed out at n=29 (71 seconds), and the extrapolated classical curve crosses the age of the universe around n=60

**[Place Fig 9: PRINCE Security Reduction]**

- PRINCE-64 is deployed in IoT devices, smart cards, and embedded systems. It uses the FX construction, which is the Even-Mansour structure from Attack 1
- Leander and May (2017) combined Grover search with Simon period finding to attack FX constructions. Classical security: 127 bits. Grover-meet-Simon hybrid security: 37 bits. That is a 90-bit reduction

**[Place Fig 8: Resource Estimates]**

- These attacks need quantum computers that do not exist yet. Bonnetain and Jaques (2022) estimated concrete resources for quantum period-finding attacks, placing qubit counts near those for breaking RSA-2048:
  - PRINCE: ~371,000 physical qubits, 13.1M T-gates
  - AES-128: ~802,000 physical qubits, 104.9M T-gates (Jaques et al., 2020)
  - AES-256: ~1.58 million physical qubits, 838.9M T-gates
- IBM's largest current chip has 1,121 qubits. Projected timelines suggest machines this size may arrive within 10-15 years

### Takeaways

- Simon's algorithm reduces key recovery from 10^19 attempts to ~128 measurements for a 128-bit key
- All attacks succeed 100% of the time at n >= 4, using about 1.1n queries
- Noise below 30% does not degrade performance. Above 35%, success collapses
- Round count has no effect on the slide attack
- PRINCE-64 drops from 127-bit to 37-bit security under the Grover-meet-Simon hybrid (Leander & May, 2017)
- Data encrypted today can be stored and decrypted when quantum hardware matures. Cipher designs need to account for this timeline

---

## DEFENSES AND FUTURE DIRECTIONS

Post-quantum replacements exist. Whether they are sufficient is an open and active question.

**The post-quantum standards:**

- NIST finalized three post-quantum standards in August 2024 (NIST, 2024), replacing the public-key algorithms that Shor's algorithm breaks (Shor, 1997)
- **Lattice-based (ML-KEM, ML-DSA):** Security relies on finding the closest point in a high-dimensional lattice with noise added. No known quantum algorithm solves this efficiently. These handle key exchange and digital signatures
- **Hash-based signatures (SLH-DSA):** Security depends on hash functions being one-way. Signatures are large but the security assumption is minimal
- **Code-based (Classic McEliece):** Decoding random error-correcting codes has resisted attack since 1978, including quantum approaches. Public keys are hundreds of kilobytes

**The post-quantum standards carry their own risks:**

- SIKE, a NIST post-quantum finalist based on elliptic curve isogenies, was broken by a classical attack in 2022 (Castryck & Decru, 2023) after years of expert review. It passed multiple rounds of evaluation before researchers discovered hidden mathematical structure that collapsed its security
- The lattice problems underlying ML-KEM and ML-DSA have been studied for about 20 years. RSA was studied for 45 years before practical attacks matured. The lattice attack surface is not yet fully mapped, and structured lattice variants (Ring-LWE, Module-LWE) introduce algebraic properties that could harbor undiscovered weaknesses
- Side-channel attacks on lattice implementations have already been demonstrated. Even if the math is sound, the code running it may leak the key through timing, power consumption, or electromagnetic emissions

**Why this research matters:**

Our project demonstrates a specific, repeating pattern in cryptographic history: schemes that appear secure under known attacks turn out to contain hidden structure that enables new attacks.

- PRINCE was published in 2012 (Borghoff et al., 2012), passed years of peer review, and was deployed in production hardware. The Grover-meet-Simon attack (Leander & May, 2017) reduced its security from 127 bits to 37 bits
- SIKE followed the same trajectory: proposed, vetted by the international community, selected as a NIST finalist, then broken by Castryck and Decru (2023) using structure the designers did not know was there
- The Even-Mansour cipher has a proven optimal classical security bound (Dunkelman et al., 2012). Our Attack 1 breaks it in O(n) quantum queries (Kuwakado & Morii, 2012). The classical security proof provided no protection against a quantum adversary

The lesson is not that any specific cipher is broken. The lesson is that hidden algebraic structure is difficult to detect and has collapsed the security of multiple schemes that experts believed were safe. Every new cryptographic standard, including the post-quantum ones, faces this same risk.

**For symmetric crypto specifically:**

- Simon's algorithm requires the cipher to produce a function with a hidden period. AES in standard modes does not have the Even-Mansour or slide structure our attacks require (Zhandry, 2016)
- The vulnerability is design-specific: Even-Mansour, Feistel with identical round keys, and iterated ciphers with a single repeated round function all create exploitable periods
- Against Grover's algorithm (generic key search), doubling the key length restores security. AES-256 maintains 128-bit security against Grover (Bernstein, 2009)
- Our attacks require the Q2 threat model (quantum superposition queries to the cipher). Whether a real-world deployment allows this depends on the system: hardware tokens may expose this interface, while network protocols may not (Kaplan et al., 2016; Bonnetain & Jaques, 2022)

**The bottom line:** Post-quantum cryptography is a work in progress, not a finished solution. Our research shows what happens when hidden structure goes undetected, and every generation of cryptographic standards has faced this problem. Ongoing quantum cryptanalysis, including the kind of period-finding analysis in this project, is how the community finds these weaknesses before adversaries do.

---

## ACKNOWLEDGEMENTS

This work was conducted at the Quantum and Optics Lab, Thomas Jefferson High School for Science and Technology. We thank our mentors for guidance on quantum circuit design and cryptographic theory.

---

## REFERENCES

Bernstein, D. J. (2009). Cost analysis of hash collisions: Will quantum computers make SHARCS obsolete? In *Workshop Record of SHARCS*.

Biryukov, A., & Wagner, D. (1999). Slide attacks. In *Fast Software Encryption (FSE 1999)*, LNCS 1636, pp. 245-259. Springer.

Boneh, D., & Zhandry, M. (2013). Quantum-secure message authentication codes. In *Advances in Cryptology — EUROCRYPT 2013*, LNCS 7881, pp. 592-608. Springer.

Bonnetain, X., & Jaques, S. (2022). Quantum period finding against symmetric primitives in practice. *IACR Transactions on Cryptographic Hardware and Embedded Systems*, 2022(1), 1-27.

Bonnetain, X., Naya-Plasencia, M., & Schrottenloher, A. (2019). On quantum slide attacks. In *Selected Areas in Cryptography — SAC 2019*, LNCS 11959, pp. 492-519. Springer.

Borghoff, J., Canteaut, A., Güneysu, T., Kavun, E. B., Knežević, M., Knudsen, L. R., Leander, G., Nikov, V., Paar, C., Rechberger, C., Rombouts, P., Thomsen, S. S., & Yalçın, T. (2012). PRINCE — A low-latency block cipher for pervasive computing applications. In *Advances in Cryptology — ASIACRYPT 2012*, LNCS 7658, pp. 208-225. Springer.

Castryck, W., & Decru, T. (2023). An efficient key recovery attack on SIDH. In *Advances in Cryptology — EUROCRYPT 2023*, LNCS 14008, pp. 423-447. Springer.

Dong, X., Dong, B., & Wang, X. (2020). Quantum attacks on some Feistel block ciphers. *Designs, Codes and Cryptography*, 88, 1179-1203.

Dunkelman, O., Keller, N., & Shamir, A. (2012). Minimalism in cryptography: The Even-Mansour scheme revisited. In *Advances in Cryptology — EUROCRYPT 2012*, LNCS 7237, pp. 336-354. Springer.

Even, S., & Mansour, Y. (1997). A construction of a cipher from a single pseudorandom permutation. *Journal of Cryptology*, 10(3), 151-162.

Gagliardoni, T., Hülsing, A., & Schaffner, C. (2016). Semantic security and indistinguishability in the quantum world. In *Advances in Cryptology — CRYPTO 2016*, LNCS 9816, pp. 60-89. Springer.

Grover, L. K. (1996). A fast quantum mechanical algorithm for database search. In *Proc. 28th ACM Symposium on Theory of Computing (STOC)*, pp. 212-219.

Jaques, S., Naehrig, M., Roetteler, M., & Virdia, F. (2020). Implementing Grover oracles for quantum key search on AES and LowMC. In *Advances in Cryptology — EUROCRYPT 2020*, LNCS 12106, pp. 280-310. Springer.

Kaplan, M., Leurent, G., Leverrier, A., & Naya-Plasencia, M. (2016). Breaking symmetric cryptosystems using quantum period finding. In *Advances in Cryptology — CRYPTO 2016*, LNCS 9815, pp. 207-237. Springer.

Kuwakado, H., & Morii, M. (2010). Quantum distinguisher between the 3-round Feistel cipher and the random permutation. In *Proc. IEEE International Symposium on Information Theory (ISIT)*, pp. 2682-2685.

Kuwakado, H., & Morii, M. (2012). Security on the quantum-type Even-Mansour cipher. In *Proc. International Symposium on Information Theory and its Applications (ISITA)*, pp. 312-316.

Leander, G., & May, A. (2017). Grover meets Simon — Quantumly attacking the FX-construction. In *Advances in Cryptology — ASIACRYPT 2017*, LNCS 10625, pp. 161-178. Springer.

Luby, M., & Rackoff, C. (1988). How to construct pseudorandom permutations from pseudorandom functions. *SIAM Journal on Computing*, 17(2), 373-386.

Nielsen, M. A., & Chuang, I. L. (2010). *Quantum Computation and Quantum Information* (10th Anniversary Edition). Cambridge University Press.

National Institute of Standards and Technology. (2024). Post-Quantum Cryptography Standardization (FIPS 203, 204, 205). https://csrc.nist.gov/projects/post-quantum-cryptography

Qiskit Contributors. (2024). Qiskit: An open-source framework for quantum computing. https://qiskit.org

Shor, P. W. (1997). Polynomial-time algorithms for prime factorization and discrete logarithms on a quantum computer. *SIAM Journal on Computing*, 26(5), 1484-1509.

Simon, D. R. (1997). On the power of quantum computation. *SIAM Journal on Computing*, 26(5), 1474-1483.

Zhandry, M. (2016). A note on quantum-secure PRPs. *Cryptology ePrint Archive*, Report 2016/1076.
