"""Seed demo database with pre-computed clean and adversarial transactions for instant presentation."""

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from twin.runner import DigitalTwinRunner
from twin.scenarios import AttackType
from storage.db import GLOBAL_DB


def seed_database():
    print("[*] Seeding Q-IMMUNE QDS database with realistic demonstration scenarios...")
    runner = DigitalTwinRunner()

    # 1. Seed Clean Sessions
    clean_messages = [
        "DEFENCE_PROCUREMENT_CONTRACT_QDS_AUTHORIZATION_001",
        "INTERBANK_RTGS_SETTLEMENT_INR_500_CRORE_TOKEN_4491",
        "SCADA_GRID_SWITCH_ROUTING_SUBSTATION_7A_DISPATCH",
        "CRITICAL_HEALTHCARE_TELEMEDICINE_CONSULT_SIGNATURE_99",
        "SOVEREIGN_QUANTUM_KEY_DISTRIBUTION_CERTIFICATE_ALPHA",
    ]

    for idx, msg in enumerate(clean_messages, 1):
        print(f"  -> Generating Clean Session {idx}/{len(clean_messages)}: {msg[:35]}...")
        runner.run_clean_baseline(msg)

    # 2. Seed Attack Scenarios
    attacks = [
        AttackType.FORGERY,
        AttackType.IMPERSONATION,
        AttackType.REPLAY,
        AttackType.DEPOLARIZING_NOISE,
        AttackType.PHASE_ROTATION,
        AttackType.CORRECTION_TAMPERING,
    ]

    for idx, atk in enumerate(attacks, 1):
        print(f"  -> Generating Adversarial Attack Session {idx}/{len(attacks)}: {atk.value}...")
        runner.inject_attack(atk, message=f"MALICIOUS_INTERCEPT_TARGET_{idx}")

    recent_sessions = GLOBAL_DB.get_recent_sessions(20)
    recent_decisions = GLOBAL_DB.get_recent_decisions(20)
    print(f"[+] Successfully seeded! Total Sessions: {len(recent_sessions)}, Decisions: {len(recent_decisions)}.")


if __name__ == "__main__":
    seed_database()
