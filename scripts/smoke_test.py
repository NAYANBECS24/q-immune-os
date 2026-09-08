import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qds.protocol import QDSProtocolOrchestrator
from twin.runner import DigitalTwinRunner
from twin.scenarios import AttackType
from ledger.verify import LedgerVerifier
from ledger.block import GLOBAL_LEDGER


def main():
    print("=" * 60)
    print("Q-IMMUNE QDS // SMOKE TEST PIPELINE")
    print("=" * 60)

    start_time = time.time()
    runner = DigitalTwinRunner()

    # 1. Clean Run
    print("[1/3] Executing Clean Baseline Session...")
    clean_sess = runner.run_clean_baseline("SMOKE_TEST_MESSAGE_001")
    assert clean_sess.guardian_decision is not None
    assert clean_sess.guardian_decision.action.value == "ACCEPT", f"Expected ACCEPT, got {clean_sess.guardian_decision.action.value}"
    print(f"      Status: {clean_sess.guardian_decision.action.value} | VER: {clean_sess.verification_report.error_metrics.ver*100:.2f}% | Hash: {clean_sess.audit_block_hash[:12]}...")

    # 2. Attack Run (Forgery)
    print("[2/3] Executing Attack Run (State Substitution Forgery)...")
    forgery_sess = runner.inject_attack(AttackType.FORGERY)
    assert forgery_sess.guardian_decision is not None
    assert forgery_sess.guardian_decision.action.value == "REJECT", f"Expected REJECT, got {forgery_sess.guardian_decision.action.value}"
    print(f"      Status: {forgery_sess.guardian_decision.action.value} | Active Threats: {forgery_sess.guardian_decision.threat_assessment.active_threats}")

    # 3. Ledger Integrity Check
    print("[3/3] Verifying Hash-Linked Blockchain Audit Ledger...")
    is_valid, errors, report = LedgerVerifier.verify_chain(GLOBAL_LEDGER)
    assert is_valid, f"Ledger integrity failed: {errors}"
    print(f"      Ledger Valid: {is_valid} | Total Blocks: {report['total_blocks']} | Latest Block: {report['latest_block_hash'][:12]}...")

    elapsed = time.time() - start_time
    print("=" * 60)
    print(f"ALL SMOKE TESTS PASSED IN {elapsed:.3f} SECONDS (100% SUCCESS)!")
    print("=" * 60)


if __name__ == "__main__":
    main()
