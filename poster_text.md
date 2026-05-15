# Poster Text: Breaking Encryption with Quantum Computers

---

## INTRODUCTION

Every time you send a text, log into your bank, or tap your credit card, your data is scrambled by an encryption algorithm — a digital lock that turns your message into gibberish that only the right key can unscramble. The security of these locks rests on one assumption: that finding the key is so hard, no computer could do it in a reasonable amount of time.

Quantum computers break that assumption.

**[Place Fig 7: Simon vs Grover]**

- Most people know quantum computers threaten public-key crypto (the locks used for websites and email). The standard fix for symmetric crypto (the locks used for everything else) is "just use a longer key" — because the best known quantum attack (Grover's algorithm) only cuts security in half
- But there is a much more powerful quantum algorithm that almost nobody talks about: **Simon's algorithm**. It doesn't just cut security in half — it **destroys it entirely** for certain cipher designs
- The graph shows the difference: to crack a 128-bit key, a classical computer needs 10^38 attempts, Grover's needs 10^19, but Simon's needs only **128**. That's not a speedup — it's a collapse

**So what?** Three widely-studied cipher designs used in textbooks and real-world systems are all vulnerable. We built every attack from scratch, ran 1,600+ experiments, and measured exactly how fast and reliable they are.

---

## HOW DOES SIMON'S ALGORITHM WORK?

Think of encryption like a combination lock. A classical computer has to try every combination one by one. Simon's algorithm exploits a hidden shortcut: if the encryption function has a **repeating pattern** (a "period"), the quantum computer can find that pattern — and the pattern reveals the key.

**[Place Fig 11: Simon's Circuit]**

- A quantum computer can test all possible inputs simultaneously using superposition (the quantum trick where a qubit is 0 and 1 at the same time)
- The circuit puts all inputs into superposition, runs them through the encryption function, then interferes the results to extract information about the hidden pattern
- Each run of the circuit produces one equation. After enough equations, you solve a simple system of equations to find the key

**[Place Fig 12: Worked Example]**

- Here's a concrete example with a 3-bit key (s = 101). The function maps 8 inputs to 4 outputs — every input shares its output with exactly one partner (e.g., 000 and 101 both map to 010). The "distance" between partners is always 101 — that's the hidden period
- Three measurements give three equations. Solving them (just like solving simultaneous equations in algebra, but with mod-2 arithmetic) reveals s = 101 — key recovered

---

## THREE CIPHERS, THREE ATTACKS

The power of Simon's algorithm is that many different cipher designs accidentally create these repeating patterns. We attacked three fundamentally different designs to show this isn't a fluke — it's a structural vulnerability.

### Attack 1: Even-Mansour — The Simplest Real Cipher

**[Place Fig 13: Even-Mansour Attack]**

- **What it is:** The most basic "real" cipher — XOR a secret key, scramble with a public permutation, XOR another secret key. Despite its simplicity, it's the building block of many practical ciphers including PRINCE (used in IoT devices)
- **The trick:** If you XOR the cipher's output with the public permutation's output, the result has a repeating pattern with period = the first secret key. One key reveals the other
- **Why it matters:** This is the foundational attack. If even the simplest cipher falls, what about more complex ones?

### Attack 2: Feistel Network — The Design Behind DES

**[Place Fig 14: Feistel Attack]**

- **What it is:** A Feistel network splits data in half and mixes the halves through multiple rounds — the same architecture used in DES (the former U.S. encryption standard) and many other ciphers
- **The trick:** Encrypt two slightly different messages and compare the results. The difference has a repeating pattern that depends on the key. Simon's algorithm finds it
- **Why it matters:** This shows the attack generalizes beyond simple ciphers to complex, multi-round designs that the cryptography community has studied for decades

### Attack 3: Slide Cipher — "Just Add More Rounds"

**[Place Fig 15: Slide Attack]**

- **What it is:** A cipher that applies the same round function over and over — the intuition being that more rounds = more security. Many real ciphers rely on this principle
- **The trick:** The attack only looks at ONE round. It completely ignores every other round, no matter how many there are
- **Why it matters:** This is the most surprising result. The common defense of "make the cipher more complex by adding rounds" is **completely useless** against a quantum adversary. 1 round or 100 rounds — same attack, same speed, same success rate

---

## RESULTS

### Does it actually work?

**[Place Fig 6: Success Rates]**

- All four attacks achieve **100% key recovery** for key sizes n >= 4, across 50 trials each — every single attempt successfully cracked the key
- The slide attack dips to 40% at n=3 (too few qubits to reliably distinguish the pattern), but hits 100% at n=4+

### How efficient is it?

**[Place Fig 3: Query Complexity]**

- The algorithm needs approximately **1.1n queries** to find an n-bit key — almost exactly the theoretical minimum of n-1
- For context: a 128-bit key needs ~141 quantum measurements. A classical computer would need around 10^19 attempts

**[Place Fig 5: Rank Convergence]**

- This graph shows how quickly the algorithm "locks in" on the answer. After just n queries, over 99% of trials have already solved the key — the convergence is extremely sharp

### Does adding more rounds help? (No.)

**[Place Fig 2: Slide Round-Independence]**

- We tested the slide attack on ciphers with 1, 2, 5, 10, 20, 50, and 100 rounds. The result: **perfectly flat lines** — identical success rate and identical speed regardless of round count
- This directly disproves the "just add more rounds" defense. The quantum attack sidesteps all additional complexity

### What about noise and errors?

**[Place Fig 1: Noise Phase Transition]**

- Real quantum computers make mistakes. We tested what happens when up to 40% of measurements are corrupted by noise
- The algorithm is remarkably resilient: **near-perfect success up to ~30% noise**. Then it hits a cliff — a sharp phase transition where performance collapses
- This tells us the attack will work on real (noisy) quantum hardware as long as error rates stay below ~30%, which is already achievable on current devices

**[Place Fig 4: Timing Curves]**

- Simulation time on a classical computer grows exponentially with key size (because simulating quantum mechanics is hard for classical computers), confirming that these attacks genuinely require quantum hardware to scale

---

## SO WHAT DOES THIS MEAN FOR REAL ENCRYPTION?

Everything above used small toy ciphers (3-8 bit keys) to prove the attacks work. But real ciphers use 64-128+ bit keys. Does the threat scale?

**[Place Fig 9: PRINCE Security Reduction]**

- PRINCE-64 is a real cipher deployed in IoT devices, smart cards, and embedded systems. It uses the **same Even-Mansour structure** we broke in Attack 1
- Classically, PRINCE has 127 bits of security — meaning you'd need ~10^38 operations to crack it. Using a Grover-meet-Simon hybrid (combining our Attack 1 with Grover search), security drops to **just 37 bits** — crackable in ~10^11 operations
- That's a **90-bit reduction** — the equivalent of downgrading a bank vault to a bicycle lock

**[Place Fig 8: Resource Estimates]**

- These attacks aren't free — they require large quantum computers that don't exist yet:
  - PRINCE: ~371,000 physical qubits
  - AES-128: ~802,000 physical qubits
  - AES-256: ~1.58 million physical qubits
- For comparison, IBM's current largest chip has 1,121 qubits. But quantum hardware is scaling rapidly — these numbers may be reachable within 10-15 years

### Key Takeaways

- **The threat is real but not yet practical.** These attacks require quantum computers ~1000x larger than today's, but the math works and the attacks are proven
- **"Just double the key" is not always enough.** Simon's algorithm doesn't care about key length — it scales linearly, not exponentially
- **Cipher design matters more than key size.** The vulnerability isn't in short keys; it's in the mathematical structure of the cipher itself
- **The time to act is now.** Encrypted data stolen today could be decrypted by future quantum computers ("harvest now, decrypt later"). Ciphers need to be redesigned before quantum hardware catches up

---

## ACKNOWLEDGEMENTS

- Attacks based on foundational work by Kuwakado & Morii (2010, 2012) and Kaplan et al. (2016)
- PRINCE/FX hybrid attack by Leander & May (2017)
- Implemented using IBM Qiskit for quantum circuit simulation
- Resource estimates based on Jaques et al. (2020)
