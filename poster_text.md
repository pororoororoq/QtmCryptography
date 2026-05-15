# Poster Text: Quantum Period-Finding Attacks on Symmetric Ciphers

---

## INTRODUCTION

**[Place Fig 7: Simon vs Grover]**

- Quantum computers don't just threaten public-key crypto (Shor's algorithm) -- they also break symmetric ciphers that were thought to be safe
- Grover's algorithm gives a quadratic speedup (halves key security), but Simon's algorithm gives an **exponential** speedup against certain cipher structures
- Simon's algorithm solves the hidden period problem -- given a function f(x) = f(x XOR s), it finds the secret s in O(n) queries, compared to O(2^(n/2)) classically
- We implemented Simon's algorithm to attack three real cipher constructions (Even-Mansour, Feistel, Slide) and ran 1,600+ trials to measure performance

**[Place Fig 10: Attack Overview]**

- Our framework reduces each cipher to a hidden-period function, then applies Simon's algorithm to recover the key
- All three attacks recover the full secret key in O(n) quantum queries -- exponentially faster than any classical method

---

## METHODOLOGY

### How Simon's Algorithm Works

**[Place Fig 11: Simon's Circuit]**

- The circuit uses 2n qubits: n input qubits and n output qubits
- Step 1: Apply Hadamard gates to create a superposition of all possible inputs
- Step 2: Apply the oracle, which computes f(x) into the output register
- Step 3: Apply Hadamard gates again and measure the input register
- Each measurement yields a vector y satisfying y * s = 0 (mod 2)
- After n-1 independent measurements, solve a linear system over GF(2) to recover s

**[Place Fig 12: Worked Example]**

- Example with n=3 and secret s=101: the function f(x) maps each input to the same output as x XOR 101 (e.g., f(000)=f(101), f(001)=f(100), etc.)
- Three measurements produce equations: 0*s1 + 1*s2 + 0*s3 = 0, etc.
- Gaussian elimination mod 2 reduces the system and reveals s = 101

### Attack 1: Even-Mansour Cipher

**[Place Fig 13: Even-Mansour Attack]**

- Even-Mansour encrypts as E(x) = P(x XOR k1) XOR k2, where P is a public permutation and k1, k2 are secret keys
- Attack: define f(x) = E(x) XOR P(x) = P(x XOR k1) XOR k2 XOR P(x)
- Key insight: f(x XOR k1) = P(x) XOR k2 XOR P(x XOR k1) = f(x), so f has period s = k1
- Simon's algorithm recovers k1 in O(n) queries; k2 is then computed as k2 = E(0) XOR P(k1)

### Attack 2: 3-Round Feistel Network

**[Place Fig 14: Feistel Attack]**

- A Feistel network splits the input into left (L) and right (R) halves and applies round function F(x) = S[x XOR k] three times, where S is a public S-box
- Attack: define f(x) = E_L(x, 0) XOR E_L(x, 1), encrypting with right half = 0 and 1, then XORing the left halves
- After algebraic analysis, f(x) has period s = S[k] XOR S[1 XOR k]
- Simon's algorithm recovers s, then a small brute-force search over all k values finds the key

### Attack 3: Quantum Slide Attack

**[Place Fig 15: Slide Attack]**

- An iterated cipher applies the same round function Fk(x) = P(x XOR k) repeatedly for r rounds, where P is public
- Attack: define f(x) = Fk(x) XOR P(x) = P(x XOR k) XOR P(x), which has period s = k
- The attack only uses ONE round of the cipher -- it completely ignores all additional rounds
- Simon's algorithm recovers the key directly in O(n) queries, no matter if the cipher uses 1, 10, or 100 rounds

---

## RESULTS

**[Place Fig 6: Success Rates]**

- All four attacks achieve 100% key recovery success for key sizes n >= 4 (50 trials each)
- At n=3, the slide attack drops to 40% due to small search space effects; all others remain at 100%

**[Place Fig 3: Query Complexity]**

- Measured query count averages approximately 1.1n, closely matching the theoretical minimum of n-1
- Consistent across key sizes n=3 through n=8, confirming O(n) scaling

**[Place Fig 5: Rank Convergence]**

- S-shaped convergence curves show how rapidly the GF(2) linear system becomes solvable
- Larger key sizes need proportionally more queries but still follow the same O(n) pattern

**[Place Fig 1: Noise Phase Transition]**

- Simon's algorithm tolerates up to ~30% measurement noise with near-perfect success
- A sharp phase transition occurs at 35-40% noise: success drops off a cliff
- Larger key sizes are more sensitive -- n=5 degrades faster than n=3 under the same noise level

**[Place Fig 2: Slide Round-Independence]**

- The slide attack maintains constant success rate and constant execution time from 1 to 100 rounds
- This proves that "just adding more rounds" provides zero additional security against a quantum adversary

**[Place Fig 4: Timing Curves]**

- Simulation time scales exponentially with key size (expected for statevector simulation on a classical computer)
- Even-Mansour (truth-table oracle) is significantly more expensive than Simon's basic oracle due to the exponential gate count in the truth-table construction

---

## CONCLUSIONS

**[Place Fig 9: PRINCE Security Reduction]**

- The Grover-meet-Simon hybrid attack reduces PRINCE-64 security from 127 bits (classical) to just 37 bits (quantum) -- a 90-bit reduction
- This demonstrates that even well-designed, widely-analyzed ciphers are vulnerable when quantum superposition queries are possible

**[Place Fig 8: Resource Estimates]**

- Real-world attacks require significant but finite quantum resources: PRINCE needs ~371K physical qubits and 13.1M T-gates; AES-128 needs ~802K qubits and 104.9M T-gates; AES-256 needs ~1.58M qubits and 838.9M T-gates
- These estimates use surface code error correction at physical error rate 10^-3

### Key Takeaways

- Simon's algorithm provides an exponential speedup (O(n) vs O(2^(n/2))) for attacking structured symmetric ciphers
- All attacks achieve 100% success with approximately 1.1n quantum queries
- Noise tolerance is strong up to ~30% error rate, then collapses sharply
- Round count is irrelevant against the quantum slide attack
- Real ciphers like PRINCE-64 see catastrophic security reduction (127 -> 37 bits)
- These attacks require a Q2 adversary (quantum superposition access to the cipher), which is not yet practical but motivates proactive cryptographic design

---

## ACKNOWLEDGEMENTS

- Built on foundational work by Kuwakado and Morii (2010, 2012) who first applied Simon's algorithm to Even-Mansour and Feistel ciphers
- Grover-meet-Simon hybrid by Leander and May (2017) for FX/PRINCE attacks
- Quantum slide attack framework by Kaplan et al. (2016)
- Implemented using IBM's Qiskit framework for quantum circuit simulation
- Resource estimation methodology based on Jaques et al. (2020) for AES quantum cost analysis
