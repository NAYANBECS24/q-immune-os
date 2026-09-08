"""Hybrid QDS vs Post-Quantum Cryptography (ML-DSA / Dilithium) benchmark matrix."""

from typing import Dict, Any, List


class PQCComparisonMatrix:
    """Provides technical and operational comparison data between QDS and classical PQC algorithms."""

    @classmethod
    def get_comparison_data(cls) -> List[Dict[str, Any]]:
        return [
            {
                "dimension": "Security Foundation",
                "qds_teleportation": "Information-Theoretic Physics (No-Cloning, Bell Entanglement)",
                "pqc_mldsa": "Computational Complexity (Module Learning With Errors / LWE)",
            },
            {
                "dimension": "Verification Mechanism",
                "qds_teleportation": "Projective Quantum Measurements + Exact Binomial / SPRT Statistics",
                "pqc_mldsa": "Deterministic Classical Algebraic Polynomial Verification",
            },
            {
                "dimension": "Channel Health Forensics",
                "qds_teleportation": "Real-Time QBER, Quantum Canary Decoy Probes & State Tomography",
                "pqc_mldsa": "None (Channel agnostic; assumes classical uncorrupted transmission)",
            },
            {
                "dimension": "Replay Defense",
                "qds_teleportation": "Cryptographic Nonce + Session Context + Freshness State Machine",
                "pqc_mldsa": "Protocol-level Nonce / Counter in wrapping protocol (e.g. TLS)",
            },
            {
                "dimension": "Quantum Hardware Requirement",
                "qds_teleportation": "Requires Quantum Channels / EPR Source or Quantum Simulator",
                "pqc_mldsa": "Runs on standard classical CPUs / microcontrollers",
            },
            {
                "dimension": "Primary Role in Defense-in-Depth",
                "qds_teleportation": "High-value quantum network digital signature verification & threat detection",
                "pqc_mldsa": "Wide-area classical network post-quantum authentication fallback",
            },
        ]
