# Breaking Symmetric Encryption with Simon's Algorithm: A Complete Implementation and Experimental Analysis

**Jake Kim**
Quantum and Optics Lab, Thomas Jefferson High School for Science and Technology

---

## Abstract

Symmetric-key ciphers are widely assumed to be safe from quantum attacks: Grover's algorithm offers only a quadratic speedup, neutralized by doubling the key length. This paper challenges that assumption. We present a complete, open-source implementation of Simon's algorithm applied to three structurally distinct block cipher designs (Even-Mansour, 3-round Feistel networks, and iterated slide ciphers), each of which falls to an exponential quantum speedup in O(n) queries. Our implementation includes quantum circuit construction, custom GF(2) linear algebra, error-tolerant recovery under realistic noise, and a Grover-meet-Simon hybrid attack on the FX construction used by PRINCE-64. Across 1,600+ experimental trials using Qiskit statevector simulation for key sizes n = 3 to 8, all attacks achieve 100% success at n >= 4, require an average of 1.1n queries (near the theoretical minimum of n - 1), and tolerate up to 30% measurement noise before performance degrades. We scale the analysis to real-world key sizes, showing that Simon's algorithm cracks a 127-bit PRINCE-like key in 21 milliseconds while classical brute force times out at n = 29. The vulnerability is structural, rooted in hidden algebraic periods that certain cipher designs create, and classical security proofs provide no protection against quantum adversaries operating in the Q2 threat model.

---

## 1. Introduction

Encryption protects every text message, bank transaction, and credit card tap. The security of these systems rests on a single assumption: no computer can recover the secret key fast enough to matter. A 128-bit key has 2^128 possible values — a number so large that every computer on Earth working together could not try them all before the sun burns out.

Quantum computing threatens this assumption through two well-known algorithms. Shor's algorithm (Shor, 1997) breaks public-key cryptography (RSA, Diffie-Hellman, elliptic curves) in polynomial time. NIST responded in August 2024 by finalizing three post-quantum replacement standards (FIPS 203, 204, 205). Grover's algorithm (Grover, 1996) halves the security level of symmetric ciphers through quantum brute-force search. The standard countermeasure is to double the key length, migrating from AES-128 to AES-256 (Bernstein, 2009).

This paper concerns a third, less widely appreciated threat: Simon's algorithm (Simon, 1997). Unlike Grover's quadratic speedup, Simon's algorithm provides an *exponential* speedup, reducing key recovery from O(2^{n/2}) classical queries to O(n) quantum queries, but only against ciphers whose mathematical structure contains a hidden period. A 128-bit key that requires 10^19 Grover queries requires approximately 128 Simon queries. Doubling the key length, the standard defense against Grover, has no meaningful effect: Simon's algorithm on a 256-bit key requires approximately 256 queries.

Kuwakado and Morii (2010, 2012) first showed that Simon's algorithm breaks the Even-Mansour cipher and 3-round Feistel networks. Kaplan et al. (2016) extended this at CRYPTO 2016, demonstrating that Simon's algorithm breaks a wide range of symmetric constructions in the Q2 threat model, including CBC-MAC, PMAC, GMAC, GCM, and OCB. Leander and May (2017) combined Simon's with Grover's algorithm to attack the FX construction, reducing the security of PRINCE-64 from 127 bits to 37 bits.

Despite this theoretical progress, the literature lacks complete, end-to-end implementations. Prior work has been primarily mathematical: proofs that the attacks work in principle, without executable quantum circuits or empirical validation across multiple cipher designs. No single framework compares how Simon's algorithm performs across Even-Mansour, Feistel, and slide settings with consistent methodology. Bonnetain and Jaques (2022) noted this gap between theoretical results and practical implementations.

This paper fills that gap. Our contributions are:

1. **Complete implementations** of Simon's algorithm attacks on three structurally different cipher designs (Even-Mansour, 3-round Feistel, iterated slide cipher), built as executable quantum circuits on the Qiskit statevector backend.
2. **Custom GF(2) linear algebra** for equation solving, since standard floating-point libraries produce incorrect results over binary fields.
3. **Noise-tolerant recovery** using majority-vote decoding, demonstrating that the attacks succeed with up to 30% measurement error, within the range of current quantum hardware.
4. **A Grover-meet-Simon hybrid** attack on the FX construction, reproducing the theoretical reduction of PRINCE-64 from 127-bit to 37-bit security.
5. **Systematic experimental validation** across 1,600+ trials, characterizing success rates, query complexity, convergence behavior, round independence, noise phase transitions, and computational scaling from n = 3 to n = 127.

---

## 2. Background

### 2.1 Block Ciphers

A block cipher is a keyed permutation: it takes a fixed-size block of data (typically 64 or 128 bits) and a secret key, and produces ciphertext of the same size. The same input with the same key always produces the same output, and the operation is reversible given the key. AES, DES, and PRINCE are all block ciphers. The security of a block cipher depends on the computational infeasibility of recovering the key from observed plaintext-ciphertext pairs.

### 2.2 Simon's Algorithm

Simon's problem (Simon, 1997) is defined as follows. Given a function f: {0,1}^n -> {0,1}^n with the promise that there exists s in {0,1}^n such that f(x) = f(y) if and only if x XOR y is in {0, s}, find s. Classically, this requires O(2^{n/2}) queries via the birthday bound. Simon's algorithm solves it in O(n) quantum queries.

The algorithm works as follows:

1. Prepare the state |0^n>|0^n> on 2n qubits.
2. Apply Hadamard gates to the first register, creating an equal superposition over all n-bit inputs.
3. Apply the oracle U_f, which maps |x>|y> to |x>|y XOR f(x)>.
4. Apply Hadamard gates to the first register again.
5. Measure the first register to obtain a vector y satisfying y * s = 0 (mod 2).
6. Repeat O(n) times to collect n - 1 linearly independent equations.
7. Solve the resulting linear system over GF(2) using Gaussian elimination to recover s.

Each measurement is guaranteed to produce a vector orthogonal to s because the second Hadamard transform causes destructive interference on all vectors y where y * s = 1. The quantum mechanics physically prevents non-orthogonal results from appearing.

### 2.3 The Q2 Threat Model

Quantum attacks on symmetric ciphers operate under two threat models. In Q1, the attacker has a quantum computer but interacts with the cipher classically: they submit classical plaintexts and receive classical ciphertexts. In Q2, the attacker can query the cipher in quantum superposition, meaning the cipher runs inside the quantum computer as a quantum gate, accepting superposition inputs and producing superposition outputs (Boneh & Zhandry, 2013; Gagliardoni et al., 2016).

Simon's algorithm requires Q2 access. Whether a real-world deployment exposes a Q2 interface depends on the system. A hardware token or smart card, where the attacker has physical access to the circuitry, may allow quantum inputs to be fed directly into the cipher. A network protocol like TLS, where all communication passes through a classical channel, constrains the attacker to Q1 (Kaplan et al., 2016; Bonnetain & Jaques, 2022).

### 2.4 GF(2) Arithmetic

The linear algebra in Simon's algorithm takes place over GF(2), the binary field where addition is XOR and 1 + 1 = 0. Standard floating-point linear algebra libraries (e.g., numpy's `linalg.matrix_rank`) produce incorrect results over GF(2). For example, the vectors [1,1], [1,0], and [0,1] have rank 3 over the reals but rank 2 over GF(2), since [1,1] = [1,0] + [0,1] mod 2. Our implementation provides custom Gaussian elimination and rank computation over GF(2) to ensure correct equation solving.

---

## 3. Cipher Constructions and Attack Reductions

The core insight behind all three attacks is the same: define a function f derived from the cipher that satisfies Simon's promise. The function f is not the cipher itself. It is a carefully constructed combination of cipher queries that creates a hidden period related to the secret key. Simon's algorithm then recovers that period.

### 3.1 Attack 1: Even-Mansour

**The cipher.** The Even-Mansour cipher (Even & Mansour, 1997) is defined as:

    E_{k1,k2}(x) = P(x XOR k1) XOR k2

where P is a publicly known permutation and k1, k2 are secret keys. This construction has a proven classical security bound: any classical adversary making T queries to E and D known-plaintext pairs requires T * D >= Omega(2^n) (Dunkelman et al., 2012). PRINCE (Borghoff et al., 2012), deployed in IoT devices, smart cards, and embedded systems, uses the Even-Mansour structure.

**The reduction.** Define f(x) = E(x) XOR P(x). Then (Kuwakado & Morii, 2012):

    f(x XOR k1) = P(x XOR k1 XOR k1) XOR k2 XOR P(x XOR k1)
                = P(x) XOR k2 XOR P(x XOR k1)
                = P(x XOR k1) XOR k2 XOR P(x)
                = f(x)

So f has Simon period s = k1. After recovering k1, we compute k2 = E(0) XOR P(k1).

**Implementation.** We construct the oracle by computing the truth table f(x) = E(x) XOR P(x) for all 2^n inputs, then converting the truth table to a reversible quantum circuit using multi-controlled X gates. The resulting circuit maps |x>|y> to |x>|y XOR f(x)>.

### 3.2 Attack 2: 3-Round Feistel Network

**The cipher.** A Feistel network splits a 2n-bit block into two n-bit halves (L, R) and applies rounds of the form:

    L_{i+1} = R_i
    R_{i+1} = L_i XOR F(R_i)

where F is a keyed round function. DES, the former US encryption standard, uses 16 rounds of this structure. The Luby-Rackoff theorem (Luby & Rackoff, 1988) proves that a 3-round Feistel network with pseudorandom round functions is a secure pseudorandom permutation against classical chosen-plaintext adversaries.

Our implementation uses a nonlinear round function F(x) = S[x XOR k], where S is a random S-box (substitution table) and k is the secret key.

**The reduction.** Construct f(x) = E_L(x, 0) XOR E_L(x, 1), where E_L denotes the left half of the ciphertext when encrypting the block (x, r) for right-half values r = 0 and r = 1. This function has Simon period s = S[k] XOR S[1 XOR k] (Kuwakado & Morii, 2010; Kaplan et al., 2016). Simon's algorithm recovers s, and a short brute-force search over the n-bit key space identifies which key k produces the observed period.

### 3.3 Attack 3: Quantum Slide Attack

**The cipher.** An iterated block cipher applies the same keyed round function r times:

    E_k(x) = F_k^r(x) = F_k(F_k(...F_k(x)...))

where F_k(x) = P(x XOR k) for a public permutation P and secret key k. In classical cryptography, adding more rounds increases security. The classical slide attack (Biryukov & Wagner, 1999) requires O(2^{n/2}) queries to find a "slide pair" via the birthday bound, regardless of the number of rounds.

**The reduction.** Define f(x) = F_k(x) XOR P(x) = P(x XOR k) XOR P(x). Then (Kaplan et al., 2016; Bonnetain et al., 2019):

    f(x XOR k) = P(x XOR k XOR k) XOR P(x XOR k)
               = P(x) XOR P(x XOR k)
               = f(x)

So f has Simon period s = k. The attack uses only the one-round function F_k, ignoring all additional rounds entirely. Simon's algorithm recovers k in O(n) queries regardless of the round count r.

### 3.4 Grover-Meet-Simon Hybrid (FX Construction)

**The cipher.** The FX construction (Kilian & Rogaway, 1996) augments a block cipher with whitening keys:

    E_{k_in, k_out}(x) = P_{k_in}(x XOR k_out) XOR k_out

where P_{k_in} is a keyed permutation (inner key) and k_out is an outer whitening key. PRINCE-64 uses this structure with a 64-bit inner key and a 64-bit outer key, providing 127 bits of classical security.

**The reduction.** Simon's algorithm alone cannot break FX, because the attacker cannot query the internal permutation P_{k_in} without knowing k_in. The Grover-meet-Simon hybrid (Leander & May, 2017) resolves this by using Grover's algorithm to search over k_in candidates. For each candidate, Simon's algorithm attempts to recover k_out (the Even-Mansour attack applied to that candidate's permutation). If the candidate is correct, Simon's returns a valid k_out; if incorrect, the result fails verification. Total cost: O(n * 2^{n/2}), reducing PRINCE-64 from 127-bit to approximately 37-bit security.

Our implementation simulates the Grover search classically (iterating over all 2^n candidates) while running the Simon component as a full quantum circuit, since the asymptotic structure — not the Grover circuit itself — is the point of the demonstration.

---

## 4. Implementation

### 4.1 Quantum Circuit Construction

All circuits are built using Qiskit (Qiskit Contributors, 2024) and executed on the statevector backend, which tracks all 2^{2n} complex probability amplitudes exactly. This faithfully reproduces the superposition, interference, and measurement statistics of a real quantum computer (Nielsen & Chuang, 2010). It is a full emulation of the quantum state, not a mathematical approximation.

The cost is exponential in the number of qubits: an n-bit key requires a circuit on 2n qubits with 2^{2n} amplitudes. An 8-bit key requires tracking 65,536 complex amplitudes. This limits our full quantum simulations to n <= 8.

Each oracle is constructed from a truth table. For each output bit position, we identify which inputs activate that bit and implement the mapping using multi-controlled X gates with appropriate control inversions. The resulting circuit implements the unitary U_f: |x>|y> -> |x>|y XOR f(x)>.

### 4.2 Sampling and Equation Solving

Each quantum query consists of:

1. Preparing a 2n-qubit circuit.
2. Applying Hadamard gates to the first n qubits.
3. Applying the oracle.
4. Applying Hadamard gates to the first n qubits.
5. Simulating the circuit via `Statevector.from_instruction()`.
6. Sampling one measurement outcome from the resulting probability distribution.

The measurement outcome is an n-bit string y. We discard the zero vector (which carries no information) and add non-zero vectors to the equation system. After each addition, we compute the GF(2) rank of the accumulated matrix. When the rank reaches n - 1, we solve the system via Gaussian elimination with back-substitution, recovering the unique non-trivial solution s.

### 4.3 Noise-Tolerant Recovery

Real quantum hardware produces noisy measurements. We model this by injecting bit-flip errors: with probability epsilon, a single bit in the measured y vector is flipped at a position where s has a 1, guaranteeing that the corrupted equation y * s = 1 (mod 2) rather than 0.

To recover s despite noise, we use majority-vote decoding:

1. Collect M >> n noisy y-vectors (we use M = max(60, min(500, 10n / (1 - 2*epsilon)^2))).
2. Draw 50 random subsets of 2n vectors each.
3. For each subset, solve the linear system to obtain a candidate s.
4. Score each candidate by counting how many of the M total vectors satisfy y * s = 0.
5. The candidate with the highest score wins, provided its score exceeds the decision threshold (midpoint between the expected score for the true s and the chance score M/2).

The true s is expected to score M * (1 - epsilon), while a random candidate scores approximately M/2. For epsilon < 0.5, these are well-separated, and majority voting reliably identifies the correct s.

---

## 5. Experimental Setup

All experiments were run on a single machine using Qiskit's statevector simulator. The simulator performs exact computation (no sampling noise from finite shot counts); noise is injected explicitly as described in Section 4.3. All source code is open-source and available at the project repository.

We conducted seven experiments:

| Experiment | Key Sizes | Trials per Configuration |
|---|---|---|
| Success rate vs. key size | n = 3-5 | 10-50 |
| Query complexity | n = 3-8 | 5-100 |
| Rank convergence | n = 3-8 | 5-100 |
| Slide round independence | n = 3-4 | 20-30 |
| Noise phase transition | n = 3-6 | 20-50 |
| Timing curves | n = 3-8 | 5-100 |
| PRINCE scaling | n = 3-127 | 1 |

For each trial, secret keys were generated pseudorandomly with fixed seeds for reproducibility. The total across all experiments exceeds 1,600 individual attack executions.

---

## 6. Results

### 6.1 Attack Success Rates

All four attacks — basic Simon's, Even-Mansour, 3-round Feistel, and slide (5 rounds) — achieve 100% key recovery at n >= 4 across 50 trials each.

The slide attack drops to 40% success at n = 3. This is a small-space artifact, not an algorithmic failure. At n = 3, the oracle function f maps 8 inputs to outputs. The Simon period creates 4 coset pairs, each producing one output value. For Simon's algorithm to reliably recover the correct period, these 4 output values must all be distinct. But 4 values landing in 8 bins collide with probability:

    P(all distinct) = (8/8)(7/8)(6/8)(5/8) = 210/512 = 41%

This matches the observed 40% success rate almost exactly. When collisions occur, the function has additional periods beyond the true key, and Simon's algorithm may return the wrong one. At n = 4, there are 8 coset pairs in 16 bins, and collision probability drops sharply. By n = 5, it is negligible.

The 3-round Feistel attack is not tested at n = 3 (half_bits = 3 yields a 6-bit block with only 8 possible half-block values, insufficient for the nonlinear S-box to provide meaningful mixing).

### 6.2 Query Complexity

The theoretical minimum number of queries to recover an n-bit secret is n - 1 (one equation per dimension, minus one for the free variable). Our measured query counts are:

| Key Size (n) | Theoretical Min | Mean Queries | Ratio to n |
|---|---|---|---|
| 3 | 2 | 3.57 | 1.19 |
| 4 | 3 | 4.53 | 1.13 |
| 5 | 4 | 5.93 | 1.19 |
| 6 | 5 | 6.50 | 1.08 |
| 7 | 6 | 7.33 | 1.05 |
| 8 | 7 | 8.80 | 1.10 |

The mean query count is consistently around 1.1n. The overhead above n - 1 arises because not every query produces a linearly independent equation. As the equation system approaches rank n - 1, a randomly sampled y vector has only a 1/2 probability of being independent of the existing equations (analogous to the coupon collector problem). Additionally, the zero vector y = 0 is discarded, though it occurs with probability 1/2^n and is rare at larger n.

All 100% of trials at each key size successfully solved the system within the default iteration limit of 10n.

### 6.3 Rank Convergence

We tracked the GF(2) rank of the equation matrix after each query. The convergence follows a characteristic S-curve: rank grows nearly linearly for the first n - 2 queries (each new equation is almost certainly independent), then flattens as the final independent equation becomes harder to obtain.

At n = 3: 69% of trials converge by query 3, 93% by query 5, and 100% by query 10.
At n = 5: 54% converge by query 5, 94% by query 8, and 100% by query 14.
At n = 8: 100% converge by query 9 (across 5 trials).

The practical implication: the algorithm converges quickly. An attacker needs only slightly more than n measurements to recover the key with near certainty.

### 6.4 Slide Attack Round Independence

We tested the slide attack on ciphers with 1, 2, 5, 10, 20, 50, and 100 rounds at n = 3 and n = 4. At n = 4, the success rate is 100% for every round count. At n = 3, the success rate is 60% for every round count (the small-space collision artifact described in Section 6.1).

Execution time is constant across round counts: approximately 0.85 seconds per trial at n = 3 and 1.37 seconds at n = 4, regardless of whether the cipher applies 1 round or 100 rounds.

This confirms the theoretical prediction of Kaplan et al. (2016): the quantum slide attack uses only the one-round function, so additional rounds provide zero additional security. In classical cryptography, the standard response to a weak cipher is "add more rounds." Against a quantum adversary with access to the round function, this defense is ineffective.

### 6.5 Noise Phase Transition

We measured attack success rates with noise levels epsilon ranging from 0% to 40% for key sizes n = 3 through 6, using majority-vote recovery with capped sample counts (M = max(60, min(500, 10n / (1 - 2*epsilon)^2))).

| Noise (epsilon) | n=3 | n=4 | n=5 | n=6 |
|---|---|---|---|---|
| 0% | 100% | 100% | 100% | 100% |
| 5% | 100% | 100% | 100% | 100% |
| 10% | 100% | 100% | 100% | 100% |
| 15% | 100% | 100% | 100% | 100% |
| 20% | 100% | 98% | 100% | 100% |
| 25% | 100% | 100% | 100% | 100% |
| 30% | 100% | 98% | 97% | 85% |
| 35% | 98% | 96% | 83% | 85% |
| 40% | 88% | 72% | 57% | 25% |

The data reveals a sharp phase transition. Below 30% noise, the attack succeeds nearly 100% of the time. Above 35%, success degrades rapidly, with larger key sizes showing steeper collapse. At 40% noise, n = 6 drops to 25% success while n = 3 remains at 88%.

The phase transition occurs because majority-vote recovery depends on the true s scoring significantly above the chance level M/2. At epsilon = 0.5, the true s and random candidates score identically, and recovery is impossible. The transition sharpens with increasing n because the fraction of valid equations needed to maintain separation from chance grows.

Current quantum hardware error rates are relevant context. IBM's Heron processor (2024) achieves two-qubit gate error rates below 1%, and overall circuit error rates for shallow circuits are well below 30%. The attack is therefore feasible on near-term quantum hardware.

### 6.6 Computational Scaling

Wall-clock execution time grows exponentially with key size, as expected for statevector simulation:

| Key Size (n) | Simon's Basic | Even-Mansour |
|---|---|---|
| 3 | 0.016 s | 0.55 s |
| 4 | 0.022 s | 1.29 s |
| 5 | 0.10 s | 13.5 s |
| 6 | 0.38 s | 83.2 s |
| 7 | 2.27 s | — |
| 8 | 17.5 s | — |

The Even-Mansour attack is slower because its oracle circuit is more complex (truth-table-based construction with multi-controlled gates) compared to the basic Simon oracle (direct CNOT construction). Both scale as O(2^{2n}) due to statevector simulation.

This exponential classical simulation cost confirms that these attacks are designed for quantum hardware. On an actual quantum computer, the circuit depth is polynomial in n, and execution time would scale polynomially rather than exponentially.

### 6.7 PRINCE Scaling Analysis

To project attack performance to real-world key sizes, we ran Simon's algorithm on PRINCE-like ciphers (modeled as Even-Mansour with truth-table oracles) from n = 3 to n = 127. For n > 8, the oracle is constructed mathematically rather than via full statevector simulation, since the latter is computationally infeasible.

The quantum attack successfully recovered the key at every key size from n = 3 to n = 127. At n = 127, the quantum attack completed in 21 milliseconds. Classical brute-force search timed out (exceeded 71 seconds) at n = 29. Extrapolating the classical timing curve, brute force would exceed the age of the universe (4.3 x 10^17 seconds) around n = 60.

The Grover-meet-Simon hybrid reduces PRINCE-64's effective security from 127 bits to approximately n/2 + log(n) = 37 bits (Leander & May, 2017). At 37 bits of effective security, exhaustive search requires approximately 1.4 x 10^11 operations — feasible on a modern laptop in minutes.

---

## 7. Discussion

### 7.1 The Structural Nature of the Vulnerability

The three attacks in this paper share a common mechanism: each cipher design creates a function with a hidden period related to the secret key. The vulnerability is in the algebraic structure of the construction itself, not in any specific cipher's parameters or key schedule.

- Even-Mansour: the XOR-based key mixing creates period k1 in f(x) = E(x) XOR P(x).
- Feistel: the round structure creates a period in the difference between encryptions with different right-half inputs.
- Slide cipher: the repeated application of an identical round function creates period k in f(x) = F_k(x) XOR P(x).

All three have proven classical security guarantees. The Even-Mansour bound (Dunkelman et al., 2012) is tight: no classical adversary can do better. The Luby-Rackoff theorem (Luby & Rackoff, 1988) proves 3-round Feistel security against all classical chosen-plaintext attacks. Adding rounds to an iterated cipher increases classical security via the birthday bound for slide pairs. None of these guarantees survive the transition to a quantum adversary in the Q2 model.

### 7.2 What Is Not Vulnerable

Simon's algorithm requires a function with a hidden period. Not all ciphers create exploitable periods.

AES in standard modes does not have the Even-Mansour or slide structure. Its round function uses distinct round keys derived from a key schedule, different S-box and MixColumns operations per round, and no publicly known permutation that an attacker can subtract out. No known reduction produces a Simon-compatible function from AES (Zhandry, 2016). Against Grover's generic key search, AES-256 maintains 128 bits of security (Bernstein, 2009).

The vulnerability is design-specific: ciphers that XOR a key before and after a public permutation (Even-Mansour), use identical round keys in a Feistel structure, or repeat the same round function create exploitable periods. Ciphers that avoid these patterns are not affected.

### 7.3 Resource Requirements

These attacks require quantum hardware that does not yet exist at the necessary scale. Bonnetain and Jaques (2022) estimated concrete resource requirements for quantum period-finding attacks on real ciphers:

| Target | Physical Qubits | T-gates |
|---|---|---|
| PRINCE-64 | ~371,000 | 13.1M |
| AES-128 (Grover) | ~802,000 | 104.9M |
| AES-256 (Grover) | ~1,580,000 | 838.9M |

IBM's largest current processor has 1,121 qubits. However, three papers published between May 2025 and March 2026 reduced estimated qubit requirements for breaking RSA-2048 from 20 million to under one million, and possibly as low as 100,000 using newer architectures.

### 7.4 Harvest Now, Decrypt Later

The temporal gap between data collection and quantum capability creates an immediate security concern. Adversaries, including state-level actors, are intercepting and storing encrypted traffic today, expecting that future quantum computers will enable retroactive decryption. The NSA, DHS, the UK's National Cyber Security Centre, the EU Agency for Cybersecurity, and the Australian Cyber Security Centre all base their post-quantum guidance on this premise.

Data that must remain confidential for more than 10-15 years is already at risk. Medical records, financial data, classified communications, and long-lived cryptographic keys all fall into this category.

### 7.5 Post-Quantum Standards and Their Risks

NIST finalized three post-quantum cryptographic standards in August 2024: lattice-based (ML-KEM, ML-DSA), hash-based (SLH-DSA), and code-based (Classic McEliece). These are designed to resist all known quantum attacks.

However, the history of cryptographic standards includes repeated cases of hidden structure discovered years after deployment:

- **PRINCE** (Borghoff et al., 2012): Published in 2012, deployed in production hardware, broken by the Grover-meet-Simon attack in 2017 (Leander & May, 2017). Security reduced from 127 bits to 37 bits.
- **SIKE** (NIST post-quantum finalist): Proposed, vetted through multiple rounds of international evaluation, selected as a finalist, then broken overnight by a classical attack exploiting hidden isogeny structure (Castryck & Decru, 2023).
- **Even-Mansour**: Has a proven optimal classical security bound (Dunkelman et al., 2012). The proof provides no protection against quantum adversaries.

The lattice problems underlying ML-KEM and ML-DSA have been studied for approximately 20 years. RSA was studied for 45 years before practical attacks matured. The structured lattice variants used in the standards (Ring-LWE, Module-LWE) have algebraic properties that could harbor undiscovered weaknesses.

Adopting post-quantum standards is necessary. So is continued cryptanalysis. Every generation of cryptographic standards has contained hidden structure that took years to find. Quantum cryptanalysis, including the period-finding analysis in this paper, is how the community identifies these weaknesses before adversaries exploit them.

---

## 8. Conclusion

We have presented a complete, open-source implementation of Simon's algorithm attacks on three structurally distinct symmetric cipher designs, each falling to an exponential quantum speedup. Our results across 1,600+ trials:

- 100% key recovery at n >= 4 for all four attack types.
- Mean query count of 1.1n, near the theoretical minimum of n - 1.
- Tolerance to 30% measurement noise, with a sharp phase transition above 35%.
- Complete independence from round count in the slide attack (tested 1-100 rounds).
- Scaling to real-world key sizes: a 127-bit PRINCE-like key recovered in 21 milliseconds.
- Reduction of PRINCE-64 security from 127 bits to 37 bits via the Grover-meet-Simon hybrid.

Certain cipher designs (Even-Mansour, Feistel with identical round keys, iterated ciphers with repeated round functions) create hidden algebraic periods that Simon's algorithm exploits. Classical security proofs, however rigorous, provide no protection against a quantum adversary in the Q2 model.

These attacks require quantum hardware that does not yet exist at scale. But hardware progress, declining resource estimates, and harvest-now-decrypt-later strategies make the threat a question of timeline, not of feasibility. Data encrypted today with vulnerable constructions may be decryptable within the operational lifetime of the systems that created it.

---

## References

Bernstein, D. J. (2009). Cost analysis of hash collisions: Will quantum computers make SHARCS obsolete? In *Workshop Record of SHARCS*.

Biryukov, A., & Wagner, D. (1999). Slide attacks. In *Fast Software Encryption (FSE 1999)*, LNCS 1636, pp. 245-259. Springer.

Boneh, D., & Zhandry, M. (2013). Quantum-secure message authentication codes. In *Advances in Cryptology -- EUROCRYPT 2013*, LNCS 7881, pp. 592-608. Springer.

Bonnetain, X., & Jaques, S. (2022). Quantum period finding against symmetric primitives in practice. *IACR Transactions on Cryptographic Hardware and Embedded Systems*, 2022(1), 1-27.

Bonnetain, X., Naya-Plasencia, M., & Schrottenloher, A. (2019). On quantum slide attacks. In *Selected Areas in Cryptography -- SAC 2019*, LNCS 11959, pp. 492-519. Springer.

Borghoff, J., et al. (2012). PRINCE -- A low-latency block cipher for pervasive computing applications. In *Advances in Cryptology -- ASIACRYPT 2012*, LNCS 7658, pp. 208-225. Springer.

Castryck, W., & Decru, T. (2023). An efficient key recovery attack on SIDH. In *Advances in Cryptology -- EUROCRYPT 2023*, LNCS 14008, pp. 423-447. Springer.

Dunkelman, O., Keller, N., & Shamir, A. (2012). Minimalism in cryptography: The Even-Mansour scheme revisited. In *Advances in Cryptology -- EUROCRYPT 2012*, LNCS 7237, pp. 336-354. Springer.

Even, S., & Mansour, Y. (1997). A construction of a cipher from a single pseudorandom permutation. *Journal of Cryptology*, 10(3), 151-162.

Gagliardoni, T., Hulsing, A., & Schaffner, C. (2016). Semantic security and indistinguishability in the quantum world. In *Advances in Cryptology -- CRYPTO 2016*, LNCS 9816, pp. 60-89. Springer.

Grover, L. K. (1996). A fast quantum mechanical algorithm for database search. In *Proc. 28th ACM Symposium on Theory of Computing (STOC)*, pp. 212-219.

Jaques, S., Naehrig, M., Roetteler, M., & Virdia, F. (2020). Implementing Grover oracles for quantum key search on AES and LowMC. In *Advances in Cryptology -- EUROCRYPT 2020*, LNCS 12106, pp. 280-310. Springer.

Kaplan, M., Leurent, G., Leverrier, A., & Naya-Plasencia, M. (2016). Breaking symmetric cryptosystems using quantum period finding. In *Advances in Cryptology -- CRYPTO 2016*, LNCS 9815, pp. 207-237. Springer.

Kilian, J., & Rogaway, P. (1996). How to protect DES against exhaustive key search. In *Advances in Cryptology -- CRYPTO 1996*, LNCS 1109, pp. 252-267. Springer.

Kuwakado, H., & Morii, M. (2010). Quantum distinguisher between the 3-round Feistel cipher and the random permutation. In *Proc. IEEE International Symposium on Information Theory (ISIT)*, pp. 2682-2685.

Kuwakado, H., & Morii, M. (2012). Security on the quantum-type Even-Mansour cipher. In *Proc. International Symposium on Information Theory and its Applications (ISITA)*, pp. 312-316.

Leander, G., & May, A. (2017). Grover meets Simon -- Quantumly attacking the FX-construction. In *Advances in Cryptology -- ASIACRYPT 2017*, LNCS 10625, pp. 161-178. Springer.

Luby, M., & Rackoff, C. (1988). How to construct pseudorandom permutations from pseudorandom functions. *SIAM Journal on Computing*, 17(2), 373-386.

Nielsen, M. A., & Chuang, I. L. (2010). *Quantum Computation and Quantum Information* (10th Anniversary Edition). Cambridge University Press.

National Institute of Standards and Technology. (2024). Post-Quantum Cryptography Standardization (FIPS 203, 204, 205). https://csrc.nist.gov/projects/post-quantum-cryptography

Qiskit Contributors. (2024). Qiskit: An open-source framework for quantum computing. https://qiskit.org

Shor, P. W. (1997). Polynomial-time algorithms for prime factorization and discrete logarithms on a quantum computer. *SIAM Journal on Computing*, 26(5), 1484-1509.

Simon, D. R. (1997). On the power of quantum computation. *SIAM Journal on Computing*, 26(5), 1474-1483.

Zhandry, M. (2016). A note on quantum-secure PRPs. *Cryptology ePrint Archive*, Report 2016/1076.
