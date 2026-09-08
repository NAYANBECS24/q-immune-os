"""Authenticated classical channel simulation for QDS teleportation correction communication."""

from __future__ import annotations
import hmac
import hashlib
import time
import uuid
from typing import Tuple, Dict, Any, Optional


class ClassicalMessage:
    """Authenticated classical payload carrying BSM outcomes and session metadata."""

    def __init__(
        self,
        message_id: str,
        session_id: str,
        signature_id: str,
        index: int,
        bsm_bits: Tuple[int, int],
        timestamp: float,
        hmac_tag: str,
    ):
        self.message_id = message_id
        self.session_id = session_id
        self.signature_id = signature_id
        self.index = index
        self.bsm_bits = bsm_bits
        self.timestamp = timestamp
        self.hmac_tag = hmac_tag

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "session_id": self.session_id,
            "signature_id": self.signature_id,
            "index": self.index,
            "bsm_bits": list(self.bsm_bits),
            "timestamp": self.timestamp,
            "hmac_tag": self.hmac_tag,
        }


class AuthenticatedClassicalChannel:
    """Models authenticated classical transmission of Pauli correction bits between Alice and Bob."""

    def __init__(self, shared_secret_key: bytes = b"Q_IMMUNE_QDS_CLASSICAL_AUTH_KEY_2026"):
        self.shared_key = shared_secret_key

    def send_bsm_outcome(
        self,
        session_id: str,
        signature_id: str,
        index: int,
        bsm_bits: Tuple[int, int],
    ) -> ClassicalMessage:
        """Packages BSM outcome into an authenticated classical message with HMAC-SHA256."""
        msg_id = f"cmsg_{uuid.uuid4().hex[:8]}"
        t = time.time()
        b1, b2 = bsm_bits
        payload = f"{msg_id}:{session_id}:{signature_id}:{index}:{b1}:{b2}:{t}".encode("utf-8")
        tag = hmac.new(self.shared_key, payload, hashlib.sha256).hexdigest()
        return ClassicalMessage(
            message_id=msg_id,
            session_id=session_id,
            signature_id=signature_id,
            index=index,
            bsm_bits=bsm_bits,
            timestamp=t,
            hmac_tag=tag,
        )

    def verify_and_receive(
        self,
        message: ClassicalMessage,
    ) -> Tuple[bool, Optional[Tuple[int, int]], str]:
        """Verifies classical channel integrity tag and extracts (b1, b2)."""
        b1, b2 = message.bsm_bits
        payload = f"{message.message_id}:{message.session_id}:{message.signature_id}:{message.index}:{b1}:{b2}:{message.timestamp}".encode("utf-8")
        expected_tag = hmac.new(self.shared_key, payload, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(message.hmac_tag, expected_tag):
            return False, None, "ERR_CLASSICAL_CHANNEL_INTEGRITY_TAMPERED"

        return True, (b1, b2), "SUCCESS"
