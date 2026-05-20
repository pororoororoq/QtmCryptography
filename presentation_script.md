# PRESENTATION SCRIPT: Breaking Encryption with Quantum Computers
### ~17 minutes | Jake Kim | TJHSST Quantum & Optics Lab

---

## SLIDE 1: Title Slide
**[Your name, title, TJHSST Quantum & Optics Lab logo]**

"Hey everyone. So — quick poll. Raise your hand if you've sent an iMessage today. Opened Instagram. Tapped your credit card somewhere. Used school Wi-Fi."

*[Wait for hands]*

"Cool. Every single one of those things was protected by encryption. Your messages, your DMs, your Venmo transactions — all scrambled by a secret key so nobody in the middle can read them."

"My project is about breaking that."

"Specifically, I built quantum algorithms that crack certain encryption schemes — not in billions of years, not in thousands of years — in about 128 steps. And I'm going to explain how, why that matters for you personally, and why the fix isn't as simple as people think."

---

## SLIDE 2: Why Should You Care?
**[Show: iMessage lock icon, Instagram DM screen, Venmo payment — all have a lock/encryption symbol]**

"So every time you send a Snap, that message is encrypted. Your bank app, your passwords, your health data — all protected by keys that would take longer than the age of the universe to crack."

"But there's a thing called 'harvest now, decrypt later.' Intelligence agencies — including China's — are intercepting and *storing* encrypted internet traffic right now. They can't read it. But they're saving it, because the moment a quantum computer gets powerful enough, they can go back and decrypt everything they collected."

"This isn't speculative. The NSA acknowledges it. DHS acknowledges it. The Federal Reserve published a paper on it. The data you send today could be readable in 10-15 years."

---

## SLIDE 3: What Is Encryption, Actually?
**[Show: simple diagram — plaintext -> key -> ciphertext -> key -> plaintext]**

"Quick background — a block cipher takes a chunk of data and a secret key, scrambles it into unreadable output. Same input, same key, same output every time. Reverse it with the key to decrypt. AES, DES, PRINCE — all block ciphers. Every credit card tap, every HTTPS connection."

"Security comes down to one thing: nobody can find the key fast enough. A 128-bit key has 2^128 possibilities. Every computer on Earth working together couldn't try them all before the sun burns out."

---

## SLIDE 4: The Grover's Algorithm Approach (And Why This Project Is Different)
**[Show: Fig 7 — Simon vs Grover comparison chart]**

"Some of you have done the Grover's lab in electrodynamics. So you already know: Grover's is quantum brute-force. It tries every key in superposition, gets a quadratic speedup — 2^128 drops to 2^64. Still huge. Fix: double the key length. AES-256 is fine. Done."

"My project is about a different algorithm that makes Grover's look like a rounding error."

"Simon's algorithm doesn't try keys. It finds hidden *patterns* in the cipher's math and extracts the key directly. O(n) — linear in the key length. 128-bit key? About 128 measurements."

"And doubling the key length does nothing. 64-bit to 128-bit just means Simon's goes from 64 queries to 128. The vulnerability isn't the key size. It's the structure."

---

## SLIDE 5: How Simon's Algorithm Works
**[Show: Fig 11 — quantum circuit diagram, then Fig 12 — worked example]**

"Okay so how does this actually work? Let me give you an analogy."

"Imagine you have a giant phone book — except every person has a secret twin. Different name, same phone number. You want to figure out the rule that connects each person to their twin."

"Classically? You flip through the phone book one name at a time, comparing phone numbers, hoping to find a match. That takes roughly the square root of the total entries."

"Simon's algorithm reads *every entry simultaneously* — quantum superposition — and when the results interfere with each other, information about the twin-pairing rule leaks out. Each quantum measurement gives you one equation the rule must satisfy. Collect enough equations — about n of them — solve the system, done. Key recovered."

"Here's the circuit. 2n qubits — n for input, n for output. Hadamard gates put inputs into superposition. The cipher, built as a quantum gate — that's the oracle in the middle — computes the output. Second layer of Hadamards creates interference. Measure. You get a vector y where y dot s equals zero mod 2. Each measurement is one equation. After n-1 independent equations, Gaussian elimination gives you the secret."

"One detail I'm kind of proud of: we couldn't use numpy for the linear algebra because numpy does floating-point math, and we needed modular arithmetic over GF(2) — that's just binary math where 1+1=0. So we wrote custom Gaussian elimination from scratch."

---

## SLIDE 6: The Catch — You Need a Hidden Period
**[Show: Fig 10 — attack overview showing three cipher structures]**

"Now, Simon's doesn't break *everything*. It needs the cipher to have a specific mathematical property: a hidden period. That means there's some secret value s where f(x) = f(x XOR s) for all inputs x. The function repeats with period s, and s is related to the key."

"Not every cipher has this. AES in standard modes? No hidden period. Safe from Simon's."

"But a surprising number of real cipher designs *do* create hidden periods — by accident. We attacked three completely different cipher architectures to show the vulnerability is structural, not a fluke."

---

## SLIDE 7: Attack 1 — Even-Mansour
**[Show: Fig 13 — Even-Mansour circuit diagram]**

"First: Even-Mansour. The simplest possible block cipher. Take a public permutation P, XOR the key in before, XOR another key after. E(x) = P(x XOR k1) XOR k2. PRINCE, a cipher used in smart cards and IoT devices, uses this exact structure."

"The attack: define f(x) = E(x) XOR P(x). Because of how Even-Mansour works, this function has a hidden period equal to k1. Simon's algorithm pulls it right out. Then k2 falls out with one more computation."

"Even-Mansour has a *proven* classical security bound — a formal mathematical proof that no classical attacker can beat a certain threshold. That proof assumes a classical adversary. It says nothing about a quantum one. Our attack just... ignores it."

---

## SLIDE 8: Attack 2 — 3-Round Feistel
**[Show: Fig 14 — Feistel network diagram]**

"Second: the Feistel network. This is the architecture behind DES, which was the US encryption standard for 20 years. Split the data in half, run rounds where one half gets scrambled with a function of the other half and the key, swap, repeat."

"There's a famous theorem — Luby-Rackoff, 1988 — that *proves* three rounds with good round functions is secure against all classical chosen-plaintext attacks. It's a foundational result in cryptography."

"We break it in O(n) queries. We construct a function from two chosen encryptions, extract a Simon period, and recover the key. Thirty-six years of security guarantee, and Simon's algorithm doesn't care."

---

## SLIDE 9: Attack 3 — Quantum Slide Attack
**[Show: Fig 15 — Slide attack, then Fig 2 — round independence flat lines]**

"Third, and this one's my favorite: the slide attack. This targets ciphers that repeat the same round function multiple times. In classical crypto, adding more rounds always makes a cipher stronger. That's the whole idea — stack enough rounds and the cipher becomes unbreakable."

"The quantum slide attack uses *one* round and ignores every other round entirely. We tested 1 round through 100 rounds. Look at this graph — perfectly flat lines. Same success rate. Same execution time. Whether the cipher does 1 round or 100 rounds, the quantum attack doesn't notice."

"Imagine someone builds a vault with 100 steel doors. And you walk through the wall."

---

## SLIDE 10: Results — Does It Actually Work?
**[Show: Fig 6 — success rates bar chart]**

"So — does it work? Yes. All four attacks recover the key 100% of the time at n=4 and above, across 50 trials each."

"The slide attack dips to 40% at n=3. At n=3 you only have 8 possible inputs, and the output space is so small that values match by coincidence beyond the actual Simon period. The probability of avoiding these extra collisions is about 41% — almost exactly matching our 40%. By n=4, the space is big enough and this goes away."

---

## SLIDE 11: Results — Efficiency and Convergence
**[Show: Fig 3 — query complexity, Fig 5 — rank convergence S-curve]**

"How efficient is it? The average query count is 1.1n — barely above the theoretical minimum of n-1. Why n-1? Each query gives one equation in n-dimensional binary space. You need n-1 independent equations to pin down the secret. You slightly overshoot because not every query gives a *new* independent equation — same coupon collector problem you see in probability."

"After n queries, over 99% of trials have converged — meaning the equation system reached full rank and the key is uniquely determined. You can see the S-curve here — steep climb, then it saturates."

---

## SLIDE 12: Results — Noise Tolerance
**[Show: Fig 1 — noise phase transition with n=3 through n=6]**

"What about noise? Real quantum computers aren't perfect. So we deliberately corrupted measurements with random bit-flip noise, from 0% to 40%."

"Below 30% noise: near-perfect success. Above 35%: sharp collapse. And larger key sizes show a steeper cliff — you can see n=6 drops to 25% success at 40% noise while n=3 is still at 88%."

"The important thing: current quantum hardware already achieves error rates under 30%. This attack doesn't need a perfect quantum computer. It works with the noisy ones we're already building."

---

## SLIDE 13: What This Means for Real Encryption
**[Show: Fig 16 — PRINCE timing curves, Fig 9 — PRINCE security reduction]**

"Everything so far used 3-8 bit keys. Real ciphers use 64 to 128-bit keys. Does the attack scale?"

"We ran Simon's on PRINCE-like ciphers up to n=127. The quantum attack cracked a 127-bit key in 21 milliseconds. Classical brute force timed out at n=29, and the extrapolated classical curve crosses *the age of the universe* around n=60."

"PRINCE-64 is a real cipher. Deployed in IoT devices, smart cards, embedded systems — maybe in your building's access cards right now. Classical security: 127 bits. After combining Simon's with Grover's search — the Grover-meet-Simon hybrid — that drops to 37 bits. 37 bits is crackable on a laptop."

---

## SLIDE 14: The Timeline
**[Show: Fig 8 — resource estimates, IBM roadmap]**

"Now — these attacks need quantum computers that don't exist yet. Breaking PRINCE requires about 371,000 physical qubits. IBM's biggest chip right now has 1,121."

"But three papers published between May 2025 and March 2026 dropped the estimated qubits needed to break RSA-2048 from 20 million to under one million — possibly 100,000. The hardware requirements are shrinking fast."

"And remember harvest now, decrypt later. The data doesn't need to be cracked today. It just has to still matter in 10 years. Medical records, financial data, classified communications — all of that is still sensitive a decade from now."

---

## SLIDE 15: Defenses
**[Show: bullet points of defenses]**

"So what do we do?"

"First, not all ciphers are vulnerable. Simon's needs a hidden period in the cipher's structure. AES doesn't have the Even-Mansour, Feistel, or slide structure that our attacks exploit. AES with a 256-bit key is currently safe from both Grover and Simon's."

"Second, these attacks assume the Q2 threat model — the attacker can query the cipher with quantum superpositions, not just normal inputs. Whether that's realistic depends on the deployment. A smart card where the attacker has physical access to the hardware? They might be able to feed quantum inputs in. A network protocol like TLS where everything goes through a classical internet connection? Probably not. The cipher has to run *inside* the quantum computer as a quantum gate."

"Third, NIST published post-quantum cryptographic standards in 2024 — lattice-based, hash-based, and code-based schemes designed to resist all known quantum attacks. But we thought SIKE was safe too. SIKE was a NIST post-quantum finalist, reviewed by the best cryptographers in the world for years. In 2022, two researchers found hidden structure nobody knew existed, and it was broken overnight. The lattice math behind the new standards has about 20 years of study. RSA had 45 before real attacks showed up."

---

## SLIDE 16: The Big Picture
**[Show: timeline — PRINCE published 2012, believed secure, broken 2017 | SIKE proposed, NIST finalist, broken 2022 | current standards... ?]**

"PRINCE was peer-reviewed for years before the quantum attack. Even-Mansour has a mathematical proof of security that doesn't survive a quantum adversary. SIKE was vetted by the entire international community and still had a fatal flaw."

"The pattern is: every generation of cryptography has hidden structure that takes years to find. Quantum cryptanalysis — the kind of period-finding in this project — is how you find it before someone else does."

---

## SLIDE 17: Conclusion / Thank You
**[Show: key takeaways + QR code to your GitHub repo]**

"We built a complete open-source framework — 1,600+ trials — showing Simon's algorithm breaks three cipher designs in linear time. 100% success rate, tolerates 30% noise, scales to real-world keys. PRINCE-64 drops from 127-bit to 37-bit security."

"All the code is on GitHub. Thank you."
