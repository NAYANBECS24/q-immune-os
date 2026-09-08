# Q-IMMUNE QDS: Information-Theoretic Threat Detection for Teleportation-Based Quantum Digital Signatures

> **Problem Statement 26141** | **Organization:** Egreen Quanta | **Category:** Software | **Theme:** Blockchain & Cybersecurity  
> **Protocol Profile:** `QIMMUNE-QDS-TB-001` (v1.0)

---

## 🌟 Executive Summary

**Q-IMMUNE QDS** is a deterministic, offline-first, zero-AI/ML quantum-inspired cybersecurity operating system and protocol laboratory designed for teleportation-based Quantum Digital Signatures (QDS).

```
PREPARE → SIGN → TELEPORT → CANARY → VERIFY → MEASURE → ANALYZE → DETECT → GUARDIAN → AUDIT → REMEMBER
```

---

## 🚀 Key Architectural Innovations

1. **Deterministic Quantum Protocol Core**:
   - Bell pair entanglement ($|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}$).
   - Bell-state measurement (BSM) & authenticated classical channel transmission (HMAC-SHA256).
   - Pauli corrections ($I, X, Z, XZ$) & state reconstruction.
   - Projective measurements across computational ($Z$), Hadamard ($X$), and circular ($Y$) bases.

2. **Zero-AI / Zero-ML Information-Theoretic Security Engine**:
   - Separate **QBER** (Channel Error) and **VER** (Signature Verification Error Rate).
   - Primary **Exact Binomial Hypothesis Testing** against calibrated legitimate noise.
   - Secondary **Guarded $\chi^2$ Goodness-of-Fit** with sparse-count safety protections.
   - **Wald's Sequential Probability Ratio Test (SPRT)** with live log-likelihood ratio ($LLR$) trajectory.
   - **Hoeffding / Serfling Finite-Sample Bounds** with confidence $(1 - \beta)$.
   - **Shannon Binary Entropy** $H_2(p)$ & uncertainty diagnostics.

3. **Multi-Vector Threat Detection & Digital Twin**:
   - 9 attack models across Identity, Quantum, and Composite categories (Forgery, Impersonation, Nonce Replay, Intercept-Resend, Depolarizing Noise, Phase Rotation, Classical Correction Bit Tampering, Unauthorized Verifier, Multi-Vector).

4. **Quantum Canary & Channel Forensics**:
   - Preflight decoy-state channel health monitor (`HEALTHY`, `DEGRADED`, `COMPROMISED`).
   - CHSH Bell-inequality witness ($S \le 2\sqrt{2}$).
   - Slow-path **Quantum State Tomography (QST)** density matrix reconstruction ($\hat{\rho}$) and 3D Bloch sphere visualization.

5. **Q-Guardian Policy Gate**:
   - Deterministic policy state machine with strict hard security precedence:
     `Replay / Impersonation (BLOCK) → Canary / Channel Compromise (QUARANTINE) → Statistical Forgery (REJECT) → Inconclusive Evidence (ESCALATE) → Valid Proofs (ACCEPT)`.

6. **Blockchain-Anchored Tamper-Evident Audit Ledger**:
   - SHA-256 hash-linked audit block chain ($H_n = \text{SHA256}(H_{n-1} + \text{Payload})$).
   - Merkle tree root batch anchoring.
   - Cryptographic chain verification & simulated tamper attack detector.

7. **Interactive Command Center UI & Benchmarks**:
   - 12-page Streamlit + Plotly application with high-tech cyber-quantum dark mode theme.
   - Continuous parameter sweeps (ROC detection curves vs noise/rotation).
   - Hybrid QDS vs NIST PQC (ML-DSA / Dilithium) trade-off matrix.
   - One-click printable HTML compliance report generator.

---

## 💻 Quick Start with `run.py`

You can run the entire system directly using `run.py`:

```bash
# 1. Launch the Cyber-Quantum Command Center UI
python run.py

# 2. Run the complete automated test suite (26 tests)
python run.py --test

# 3. Run fast smoke test verification (< 1 sec)
python run.py --smoke

# 4. Seed the database with demo transactions
python run.py --seed

# 5. Run 100% deterministic offline reproducibility benchmark
python run.py --reproduce
```

---

## 🐳 Docker Deployment

```bash
docker compose up --build
```
Access the application at `http://localhost:8501`.

---

## 📜 Scientific Defensibility & Scope Note

Q-IMMUNE QDS is a reproducible software prototype and cyber-defense platform for teleportation-based quantum digital signatures. Results apply strictly to the stated local protocol model, noise calibration, and finite measurement sample. This platform provides mathematically explainable evidence and zero-AI decision support; it is not presented as an unconditional formal security proof for all physical hardware implementations.
