"""NetworkX-based evidence graph and cryptographic provenance tracker."""

from __future__ import annotations
from typing import Dict, Any, List, Optional
import networkx as nx

from qds.signer import SignaturePacket
from detection.evidence_bundle import EvidenceBundle
from guardian.state_machine import GuardianDecision


class EvidenceGraphBuilder:
    """Constructs a Directed Acyclic Graph (DAG) tracing lineage from Signer to Guardian Decision."""

    @classmethod
    def build_graph(
        cls,
        signature_packet: SignaturePacket,
        evidence: EvidenceBundle,
        decision: GuardianDecision,
        audit_hash: Optional[str] = None,
    ) -> nx.DiGraph:
        """Builds a NetworkX DiGraph representing end-to-end event lineage."""
        G = nx.DiGraph()

        # 1. Signer Node
        G.add_node("Signer", label=f"Signer: {signature_packet.signer_id}", node_type="ACTOR", status="INFO")

        # 2. Message & Digest
        G.add_node("Message", label="Input Document / Message", node_type="DATA", status="INFO")
        G.add_node("Digest", label=f"SHA-256: {signature_packet.message_digest[:12]}...", node_type="CRYPTO", status="INFO")
        G.add_edge("Signer", "Message")
        G.add_edge("Message", "Digest")

        # 3. Quantum State Manifest
        G.add_node("StateManifest", label=f"Manifest ({signature_packet.manifest.length} Qubits)", node_type="QUANTUM", status="INFO")
        G.add_edge("Digest", "StateManifest")

        # 4. Bell Pairs Resource
        G.add_node("BellResource", label="EPR Pairs (|Phi+>)", node_type="QUANTUM", status="INFO")
        G.add_edge("StateManifest", "BellResource")

        # 5. Teleportation & BSM
        G.add_node("Teleportation", label="BSM (qM, qA)", node_type="QUANTUM", status="INFO")
        G.add_edge("BellResource", "Teleportation")

        # 6. Authenticated Classical Channel
        c_status = "PASS" if evidence.classical_channel_authenticated else "FAIL"
        G.add_node("ClassicalAuth", label="Classical HMAC Auth", node_type="SECURITY", status=c_status)
        G.add_edge("Teleportation", "ClassicalAuth")

        # 7. Pauli Correction
        G.add_node("PauliCorrection", label="Pauli U(b1,b2)", node_type="QUANTUM", status="INFO")
        G.add_edge("ClassicalAuth", "PauliCorrection")

        # 8. Projective Measurements
        G.add_node("MeasurementBatch", label=f"Projective Meas (N={evidence.sample_size})", node_type="QUANTUM", status="INFO")
        G.add_edge("PauliCorrection", "MeasurementBatch")

        # 9. Statistical Security Engine
        s_status = "PASS" if (evidence.binomial_result and evidence.binomial_result.null_hypothesis_accepted) else "FAIL"
        G.add_node(
            "StatisticalReport",
            label=f"Stats (VER={evidence.verification_error_rate:.3f}, QBER={evidence.qber:.3f})",
            node_type="MATH",
            status=s_status,
        )
        G.add_edge("MeasurementBatch", "StatisticalReport")

        # 10. Threat Assessment
        t_status = "PASS" if not decision.threat_assessment.active_threats else "FAIL"
        t_label = f"Threats: {', '.join(decision.threat_assessment.active_threats) if decision.threat_assessment.active_threats else 'None (Clean)'}"
        G.add_node("ThreatEvent", label=t_label, node_type="THREAT", status=t_status)
        G.add_edge("StatisticalReport", "ThreatEvent")

        # 11. Guardian Decision
        g_status = "PASS" if decision.action.value == "ACCEPT" else "FAIL"
        G.add_node("GuardianDecision", label=f"Decision: {decision.action.value}", node_type="POLICY", status=g_status)
        G.add_edge("ThreatEvent", "GuardianDecision")

        # 12. Blockchain Audit Block
        if audit_hash:
            G.add_node("AuditLedger", label=f"Ledger Root: {audit_hash[:12]}...", node_type="BLOCKCHAIN", status="PASS")
            G.add_edge("GuardianDecision", "AuditLedger")

        return G

    @classmethod
    def export_graph_dict(cls, G: nx.DiGraph) -> Dict[str, Any]:
        """Serializes graph nodes and edges for UI visualization."""
        nodes = []
        for n, d in G.nodes(data=True):
            nodes.append({
                "id": n,
                "label": d.get("label", n),
                "type": d.get("node_type", "DEFAULT"),
                "status": d.get("status", "INFO"),
            })
        edges = []
        for u, v in G.edges():
            edges.append({"source": u, "target": v})

        return {"nodes": nodes, "edges": edges}
