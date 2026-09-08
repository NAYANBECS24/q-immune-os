"""Q-Guardian deterministic policy state machine with strict security precedence."""

from __future__ import annotations
import time
import uuid
from typing import List, Dict, Any, Optional

from .reason_codes import GuardianAction, ReasonCode
from .policy import GuardianPolicy, DEFAULT_GUARDIAN_POLICY
from detection.evidence_bundle import EvidenceBundle
from detection.fusion import ThreatAssessment, ThreatFusionEngine
from statistics.sprt import SPRTDecision


class GuardianDecision:
    """The authoritative security decision output from Q-Guardian."""

    def __init__(
        self,
        decision_id: str,
        session_id: str,
        action: GuardianAction,
        primary_reason: str,
        reason_codes: List[str],
        threat_assessment: ThreatAssessment,
        policy_id: str,
        timestamp: Optional[float] = None,
    ):
        self.decision_id = decision_id
        self.session_id = session_id
        self.action = action
        self.primary_reason = primary_reason
        self.reason_codes = reason_codes
        self.threat_assessment = threat_assessment
        self.policy_id = policy_id
        self.timestamp = timestamp or time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "session_id": self.session_id,
            "action": self.action.value,
            "primary_reason": self.primary_reason,
            "reason_codes": self.reason_codes,
            "active_threats": self.threat_assessment.active_threats,
            "composite_threat_score": self.threat_assessment.composite_score,
            "threat_level": self.threat_assessment.threat_level,
            "policy_id": self.policy_id,
            "timestamp": self.timestamp,
        }


class GuardianEngine:
    """Evaluates evidence bundles through deterministic policy rules with hard security precedence."""

    @classmethod
    def evaluate(
        cls,
        evidence: EvidenceBundle,
        policy: GuardianPolicy = DEFAULT_GUARDIAN_POLICY,
        expected_signer_id: str = "Alice_Signer_Primary",
        authorized_verifier_id: str = "Bob_Verifier_Primary",
    ) -> GuardianDecision:
        did = f"dec_{uuid.uuid4().hex[:8]}"

        # Step 0: Run deterministic threat fusion
        assessment = ThreatFusionEngine.evaluate(
            evidence=evidence,
            ver_threshold=policy.max_ver,
            max_qber_threshold=policy.max_qber,
            expected_signer_id=expected_signer_id,
            authorized_verifier_id=authorized_verifier_id,
        )

        active_threats = set(assessment.active_threats)
        reason_codes = assessment.all_reason_codes.copy()

        # Hard Precedence 1: Replay Attack -> BLOCK
        if "REPLAY" in active_threats and policy.auto_block_on_replay:
            return GuardianDecision(
                decision_id=did,
                session_id=evidence.session_id,
                action=GuardianAction.BLOCK,
                primary_reason="Freshness validation failed: Replay attack detected (nonce reuse or stale transcript).",
                reason_codes=reason_codes,
                threat_assessment=assessment,
                policy_id=policy.policy_id,
            )

        # Hard Precedence 2: Impersonation / Unauthorized -> BLOCK
        if "IMPERSONATION" in active_threats or "UNAUTHORIZED_VERIFICATION" in active_threats:
            return GuardianDecision(
                decision_id=did,
                session_id=evidence.session_id,
                action=GuardianAction.BLOCK,
                primary_reason="Authorization failed: Identity mismatch or unauthorized verifier access.",
                reason_codes=reason_codes,
                threat_assessment=assessment,
                policy_id=policy.policy_id,
            )

        # Hard Precedence 3: Quantum Canary / Channel Compromise -> QUARANTINE
        if evidence.canary_health == "COMPROMISED" and policy.auto_quarantine_on_compromised_canary:
            return GuardianDecision(
                decision_id=did,
                session_id=evidence.session_id,
                action=GuardianAction.QUARANTINE,
                primary_reason="Quantum link compromised: Preflight canary probe failed baseline integrity.",
                reason_codes=reason_codes,
                threat_assessment=assessment,
                policy_id=policy.policy_id,
            )

        # Hard Precedence 4: Statistical / Forgery Failure -> REJECT
        if "FORGERY" in active_threats:
            return GuardianDecision(
                decision_id=did,
                session_id=evidence.session_id,
                action=GuardianAction.REJECT,
                primary_reason="Statistical verification failed: Measurement distribution inconsistent with legitimate signer state.",
                reason_codes=reason_codes,
                threat_assessment=assessment,
                policy_id=policy.policy_id,
            )

        # Hard Precedence 5: Channel Manipulation (elevated QBER/fidelity) -> QUARANTINE
        if "CHANNEL_MANIPULATION" in active_threats:
            return GuardianDecision(
                decision_id=did,
                session_id=evidence.session_id,
                action=GuardianAction.QUARANTINE,
                primary_reason="Channel anomaly detected: Physical link QBER elevated or fidelity degraded.",
                reason_codes=reason_codes,
                threat_assessment=assessment,
                policy_id=policy.policy_id,
            )

        # Hard Precedence 6: Inconclusive SPRT -> ESCALATE
        if evidence.sprt_result and evidence.sprt_result.decision == SPRTDecision.CONTINUE and evidence.sample_size < 32:
            return GuardianDecision(
                decision_id=did,
                session_id=evidence.session_id,
                action=GuardianAction.ESCALATE,
                primary_reason="Insufficient statistical evidence: SPRT boundaries not reached. Extended sampling required.",
                reason_codes=[ReasonCode.WARN_TOMOGRAPHY_FORENSIC_ESCALATION.value],
                threat_assessment=assessment,
                policy_id=policy.policy_id,
            )

        # Hard Precedence 7: All mandatory conditions passed -> ACCEPT
        return GuardianDecision(
            decision_id=did,
            session_id=evidence.session_id,
            action=GuardianAction.ACCEPT,
            primary_reason="All quantum, statistical, freshness, and cryptographic policy checks passed successfully.",
            reason_codes=[ReasonCode.SUCCESS_ALL_CHECKS_PASSED.value],
            threat_assessment=assessment,
            policy_id=policy.policy_id,
        )
