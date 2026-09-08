"""Provenance metadata record formatting."""

from typing import Dict, Any
import time


class ProvenanceTracker:
    """Formats provenance metadata for compliance records."""

    @classmethod
    def create_provenance_record(
        cls,
        session_id: str,
        signature_id: str,
        signer_id: str,
        verifier_id: str,
        message_digest: str,
        guardian_action: str,
    ) -> Dict[str, Any]:
        return {
            "session_id": session_id,
            "signature_id": signature_id,
            "signer_id": signer_id,
            "verifier_id": verifier_id,
            "message_digest": message_digest,
            "guardian_action": guardian_action,
            "recorded_at": time.time(),
            "software_version": "Q-IMMUNE-QDS-2.0",
        }
