"""Cryptographic compliance audit report generator."""

from __future__ import annotations
import json
import time
from typing import Dict, Any, Optional

from qds.protocol import QDSSession


class ComplianceReportGenerator:
    """Generates standalone HTML and JSON compliance evidence reports."""

    @classmethod
    def generate_html_report(cls, session: QDSSession) -> str:
        """Renders an executive-ready HTML forensic audit report."""
        rep = session.verification_report
        dec = session.guardian_decision
        pkt = session.signature_packet

        action_color = "#00ff88" if (dec and dec.action.value == "ACCEPT") else "#ff0055"
        action_text = dec.action.value if dec else "UNKNOWN"
        ver_text = f"{rep.error_metrics.ver * 100:.2f}%" if rep else "N/A"
        qber_text = f"{rep.error_metrics.qber * 100:.2f}%" if rep else "N/A"
        p_val_text = f"{rep.evidence_bundle.binomial_result.p_value:.6f}" if (rep and rep.evidence_bundle.binomial_result) else "N/A"
        reasons_html = "".join(f"<li><code>{r}</code></li>" for r in (dec.reason_codes if dec else []))
        threats_html = "".join(f"<span class='badge threat'>{t}</span>" for t in (dec.threat_assessment.active_threats if dec else []))

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Q-IMMUNE QDS Forensic Audit Report - {session.session_id}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0c101d; color: #e2e8f0; margin: 0; padding: 40px; }}
        .card {{ background-color: #161e31; border: 1px solid #2d3748; border-radius: 12px; padding: 25px; margin-bottom: 25px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #00f2fe; padding-bottom: 15px; margin-bottom: 20px; }}
        .logo {{ font-size: 24px; font-weight: bold; color: #00f2fe; letter-spacing: 1px; }}
        .badge {{ padding: 6px 14px; border-radius: 20px; font-weight: bold; font-size: 14px; display: inline-block; }}
        .badge.action {{ background-color: {action_color}22; color: {action_color}; border: 1px solid {action_color}; font-size: 18px; }}
        .badge.threat {{ background-color: #ff005522; color: #ff0055; border: 1px solid #ff0055; margin-right: 6px; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }}
        .metric-box {{ background-color: #1e293b; padding: 15px; border-radius: 8px; text-align: center; border-left: 3px solid #00f2fe; }}
        .metric-val {{ font-size: 22px; font-weight: bold; color: #38bdf8; }}
        .metric-label {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ background-color: #1e293b; color: #38bdf8; font-size: 13px; }}
        code {{ background-color: #0f172a; padding: 3px 8px; border-radius: 4px; color: #38bdf8; font-size: 13px; }}
        .footer {{ font-size: 12px; color: #64748b; text-align: center; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div>
                <div class="logo">Q-IMMUNE QDS // FORENSIC AUDIT EVIDENCE</div>
                <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">SIH 2026 Problem Statement 26141 | Egreen Quanta</div>
            </div>
            <div>
                <span class="badge action">{action_text}</span>
            </div>
        </div>

        <div class="metric-grid">
            <div class="metric-box">
                <div class="metric-val">{ver_text}</div>
                <div class="metric-label">Verification Error (VER)</div>
            </div>
            <div class="metric-box">
                <div class="metric-val">{qber_text}</div>
                <div class="metric-label">Channel Error (QBER)</div>
            </div>
            <div class="metric-box">
                <div class="metric-val">{p_val_text}</div>
                <div class="metric-label">Binomial p-value</div>
            </div>
            <div class="metric-box">
                <div class="metric-val">{session.status.value}</div>
                <div class="metric-label">Pipeline Status</div>
            </div>
        </div>

        <h3>1. Session & Cryptographic Provenance</h3>
        <table>
            <tr><th>Session Identifier</th><td><code>{session.session_id}</code></td></tr>
            <tr><th>Signer Node ID</th><td><code>{session.signer_id}</code></td></tr>
            <tr><th>Verifier Node ID</th><td><code>{session.verifier_id}</code></td></tr>
            <tr><th>Message Digest</th><td><code>{pkt.message_digest if pkt else 'N/A'}</code></td></tr>
            <tr><th>Transcript Hash</th><td><code>{pkt.transcript.transcript_hash if pkt else 'N/A'}</code></td></tr>
            <tr><th>Blockchain Audit Hash</th><td><code>{session.audit_block_hash or 'N/A'}</code></td></tr>
            <tr><th>Merkle Root</th><td><code>{session.merkle_root or 'N/A'}</code></td></tr>
        </table>

        <h3>2. Threat Assessment & Guardian Precedence</h3>
        <div>Active Threats: {threats_html if threats_html else '<span style=\"color:#00ff88;\">None Detected (Clean)</span>'}</div>
        <p><strong>Primary Decision Reason:</strong> {dec.primary_reason if dec else 'N/A'}</p>
        <ul>{reasons_html}</ul>

        <h3>3. Scientific Defensibility & Protocol Model</h3>
        <p style="font-size: 13px; color: #94a3b8;">
            Protocol: <code>{session.profile.protocol_id} (v{session.profile.protocol_version})</code><br>
            Verification was performed using deterministic exact binomial hypothesis testing and Wald Sequential Probability Ratio Testing over basis-matched projective measurements.
            This report represents mathematically reproducible evidence under the stated local channel and protocol model.
        </p>

        <div class="footer">
            Generated by Q-IMMUNE QDS v2.0 &bull; Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(session.created_at))} &bull; Offline Deterministic Security OS
        </div>
    </div>
</body>
</html>"""
        return html
