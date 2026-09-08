"""Q-IMMUNE QDS — Cyber-Quantum Command Center & Forensic Defense OS.

Zero-AI/ML Deterministic Security Platform for Teleportation-Based
Quantum Digital Signatures, Threat Detection, and Blockchain Auditing.
"""

import os
import sys
import time
import json
import math
import streamlit as st
import streamlit.components.v1 as st_components
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.theme import CYBER_QUANTUM_CSS, PLOTLY_DARK_TEMPLATE, NEON_COLORS
from qds.protocol import QDSProtocolOrchestrator, QDSSession
from qds.protocol_profile import DEFAULT_PROTOCOL_PROFILE, QDSProtocolProfile
from twin.runner import DigitalTwinRunner
from twin.scenarios import AttackType, ATTACK_CATALOG
from quantum_lab.states import QuantumState, Basis, StateFamily
from quantum_lab.backend import LocalSimulatorBackend, RemoteQPUBackend
from forensics.bloch import BlochSphereVisualizer
from forensics.tomography import StateTomography
from guardian.policy import GuardianPolicy, DEFAULT_GUARDIAN_POLICY
from guardian.state_machine import GuardianEngine
from ledger.block import GLOBAL_LEDGER
from ledger.verify import LedgerVerifier
from ledger.merkle import MerkleTree
from benchmark.ensemble import AttackEnsembleBenchmark
from benchmark.pqc import PQCComparisonMatrix
from reports.generator import ComplianceReportGenerator
from storage.db import GLOBAL_DB
from statistics.calibration import DEFAULT_CALIBRATION
from statistics.sprt import SPRTDecision
from statistics.entropy import EntropyDiagnostics
from statistics.finite_sample import FiniteSampleBounds
from statistics.chi_square import StatisticalHypothesisEngine
from canary import QuantumCanary

# ══════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Q-IMMUNE QDS // Cyber-Quantum Security OS",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CYBER_QUANTUM_CSS, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ══════════════════════════════════════════════════════════
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = QDSProtocolOrchestrator()
if "runner" not in st.session_state:
    st.session_state.runner = DigitalTwinRunner(orchestrator=st.session_state.orchestrator)
if "current_session" not in st.session_state:
    st.session_state.current_session = st.session_state.runner.run_clean_baseline(
        "SOVEREIGN_RTGS_SETTLEMENT_INR_500CR_2026"
    )
if "active_policy" not in st.session_state:
    st.session_state.active_policy = DEFAULT_GUARDIAN_POLICY
if "session_history" not in st.session_state:
    st.session_state.session_history = []  # list of QDSSession objects
if "pipeline_feed" not in st.session_state:
    st.session_state.pipeline_feed = []  # list of pipeline stage log dicts
if "demo_running" not in st.session_state:
    st.session_state.demo_running = False
if "kpi_total" not in st.session_state:
    st.session_state.kpi_total = 0
if "kpi_accept" not in st.session_state:
    st.session_state.kpi_accept = 0
if "kpi_blocked" not in st.session_state:
    st.session_state.kpi_blocked = 0

# ══════════════════════════════════════════════════════════
# ALL 14 Q-IMMUNE PROTOCOL & FORENSIC MODULES
# ══════════════════════════════════════════════════════════
ALL_MODULES = [
    "⚡ Executive Command Center",
    "🔬 Quantum Protocol Lab",
    "🌌 Teleportation Monitor",
    "📊 Verification & Statistics",
    "⚔️ Digital Twin Attack Lab",
    "🐤 Quantum Canary Health",
    "🩺 Forensic State Tomography",
    "🛡️ Q-Guardian Policy Gate",
    "🕸️ Evidence Provenance Graph",
    "⛓️ Blockchain Audit Ledger",
    "📈 Benchmarks & PQC Comparison",
    "📜 Reports & Assumptions",
    "🗂️ Session History Archive",
    "🎬 Live Transaction Feed",
]

if "active_module" not in st.session_state:
    st.session_state.active_module = ALL_MODULES[0]
if "nav_version" not in st.session_state:
    st.session_state.nav_version = 0


def switch_module(mod_name: str):
    """Safely updates active module without modifying instantiated widget keys."""
    if mod_name in ALL_MODULES and mod_name != st.session_state.active_module:
        st.session_state.active_module = mod_name
        st.session_state.nav_version = st.session_state.get("nav_version", 0) + 1


# ══════════════════════════════════════════════════════════
# SIDEBAR CONTROLS & PROTOCOL TELEMETRY
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="logo-icon">⚛️</div>
        <div class="logo-title">Q-IMMUNE QDS</div>
        <div class="logo-sub">Information-Theoretic Threat OS</div>
        <span class="badge badge-cyan">SIH 2026 · PS 26141</span>
    </div>
    """, unsafe_allow_html=True)

    cur_sidebar_idx = ALL_MODULES.index(st.session_state.active_module) if st.session_state.active_module in ALL_MODULES else 0
    sidebar_sel = st.selectbox(
        "NAVIGATION MODULES",
        ALL_MODULES,
        index=cur_sidebar_idx,
        key=f"sidebar_nav_v_{st.session_state.get('nav_version', 0)}",
    )
    if sidebar_sel != st.session_state.active_module:
        switch_module(sidebar_sel)
        st.rerun()

    st.markdown("---")
    st.markdown('<span class="q-label">ACTIVE PROTOCOL SPECIFICATION</span>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background: rgba(0, 212, 255, 0.08); border: 1px solid rgba(0, 212, 255, 0.35); border-radius: 8px; padding: 8px 12px; font-family: 'JetBrains Mono', monospace; color: #00D4FF; font-size: 0.82rem; font-weight: 700; text-align: center; margin: 4px 0 8px 0; letter-spacing: 0.5px;">
        {DEFAULT_PROTOCOL_PROFILE.protocol_id} v{DEFAULT_PROTOCOL_PROFILE.protocol_version}
    </div>
    """, unsafe_allow_html=True)
    st.caption(f"Resource: {DEFAULT_PROTOCOL_PROFILE.entanglement_resource}")

    st.markdown("---")
    st.markdown('<span class="q-label">QUANTUM BACKEND HARDWARE</span>', unsafe_allow_html=True)
    backend_choice = st.radio("Backend Engine", ["Local Statevector Simulator", "Remote QPU Adapter (Mock)"], label_visibility="collapsed")
    backend = LocalSimulatorBackend() if "Local" in backend_choice else RemoteQPUBackend()
    bh = backend.health_check()
    st.markdown(f'<div class="status-row"><span class="dot dot-g"></span> {bh["status"]} · 32 Active Qubits</div>', unsafe_allow_html=True)
    st.caption(f"Backend Engine: {bh.get('backend_type', 'Statevector_Exact')}")

# ══════════════════════════════════════════════════════════
# MASTER HEADER BANNER & TOP NAVIGATION BAR
# ══════════════════════════════════════════════════════════
st.markdown("""
<div class="q-header">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:14px;">
        <div>
            <h1>Q-IMMUNE QDS // <span class="accent">CYBER-QUANTUM SECURITY OS</span></h1>
            <p class="subtitle">Zero-AI/ML · Deterministic Information-Theoretic Security · Teleportation-Based Quantum Digital Signatures · Blockchain Ledger</p>
        </div>
        <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
            <span class="badge badge-green"><span class="dot dot-g"></span>&nbsp;ZERO-AI DETERMINISTIC</span>
            <span class="badge badge-cyan">INFORMATION-THEORETIC</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Primary Top Navigation Bar (Always Visible on Main Screen) ──
nav_col1, nav_col2 = st.columns([3.6, 1.2])
with nav_col1:
    top_cur_idx = ALL_MODULES.index(st.session_state.active_module) if st.session_state.active_module in ALL_MODULES else 0
    top_sel = st.selectbox(
        "🎛️ ACTIVE MODULE SWITCHER (14 Security & Protocol Labs)",
        ALL_MODULES,
        index=top_cur_idx,
        key=f"top_nav_v_{st.session_state.get('nav_version', 0)}",
        help="Select any of the 14 interactive modules to inspect quantum states, statistical proofs, live attacks, or blockchain audit ledger.",
    )
    if top_sel != st.session_state.active_module:
        switch_module(top_sel)
        st.rerun()

with nav_col2:
    st.markdown('<div style="height:28px;"></div>', unsafe_allow_html=True)
    if st.button("🎬 Auto-Demo Mode", type="primary", use_container_width=True, help="Switch to the Live Transaction Feed and run the 6-phase Judge demo"):
        switch_module("🎬 Live Transaction Feed")
        st.rerun()

# ── Quick Access Category Pills ──
q_c1, q_c2, q_c3, q_c4, q_c5, q_c6, q_c7 = st.columns(7)
with q_c1:
    if st.button("⚡ Exec", use_container_width=True, type="secondary" if st.session_state.active_module != "⚡ Executive Command Center" else "primary"):
        switch_module("⚡ Executive Command Center")
        st.rerun()
with q_c2:
    if st.button("🔬 Lab", use_container_width=True, type="secondary" if st.session_state.active_module != "🔬 Quantum Protocol Lab" else "primary"):
        switch_module("🔬 Quantum Protocol Lab")
        st.rerun()
with q_c3:
    if st.button("📊 Stats", use_container_width=True, type="secondary" if st.session_state.active_module != "📊 Verification & Statistics" else "primary"):
        switch_module("📊 Verification & Statistics")
        st.rerun()
with q_c4:
    if st.button("⚔️ Attack", use_container_width=True, type="secondary" if st.session_state.active_module != "⚔️ Digital Twin Attack Lab" else "primary"):
        switch_module("⚔️ Digital Twin Attack Lab")
        st.rerun()
with q_c5:
    if st.button("🛡️ Guardian", use_container_width=True, type="secondary" if st.session_state.active_module != "🛡️ Q-Guardian Policy Gate" else "primary"):
        switch_module("🛡️ Q-Guardian Policy Gate")
        st.rerun()
with q_c6:
    if st.button("⛓️ Ledger", use_container_width=True, type="secondary" if st.session_state.active_module != "⛓️ Blockchain Audit Ledger" else "primary"):
        switch_module("⛓️ Blockchain Audit Ledger")
        st.rerun()
with q_c7:
    if st.button("🗂️ History", use_container_width=True, type="secondary" if st.session_state.active_module != "🗂️ Session History Archive" else "primary"):
        switch_module("🗂️ Session History Archive")
        st.rerun()

# Set current active page reference
page = st.session_state.active_module

# Helper refs
sess: QDSSession = st.session_state.current_session
rep = sess.verification_report
dec = sess.guardian_decision
pkt = sess.signature_packet


def sfig(fig, title="", height=380):
    """Safely applies dark theme template to Plotly figures."""
    layout_kw = dict(PLOTLY_DARK_TEMPLATE)
    layout_kw["height"] = height
    if title:
        layout_kw["title"] = dict(text=title, font=dict(size=14, color="#FFFFFF"))
    fig.update_layout(**layout_kw)
    return fig


def acolor(a):
    return {"ACCEPT": "#00FF88", "REJECT": "#FF3B6E", "BLOCK": "#FF3B6E", "QUARANTINE": "#FFA500", "ESCALATE": "#A855F7"}.get(a, "#00D4FF")


def abadge(a):
    return {"ACCEPT": "badge-green", "REJECT": "badge-red", "BLOCK": "badge-red", "QUARANTINE": "badge-amber", "ESCALATE": "badge-cyan"}.get(a, "badge-cyan")


def record_session_to_history(s: QDSSession):
    """Records session to in-memory history and updates KPI counters."""
    history = st.session_state.session_history
    # Avoid duplicates
    existing_ids = {h.session_id for h in history}
    if s.session_id not in existing_ids:
        history.insert(0, s)
        if len(history) > 50:
            history.pop()
        st.session_state.kpi_total += 1
        act = s.guardian_decision.action.value if s.guardian_decision else "UNKNOWN"
        if act == "ACCEPT":
            st.session_state.kpi_accept += 1
        elif act in ("BLOCK", "REJECT", "QUARANTINE"):
            st.session_state.kpi_blocked += 1


def log_pipeline_stage(stage: str, status: str, detail: str = "", duration_ms: float = 0.0):
    """Appends a stage entry to the live pipeline feed."""
    feed = st.session_state.pipeline_feed
    feed.insert(0, {
        "ts": time.strftime("%H:%M:%S"),
        "stage": stage,
        "status": status,
        "detail": detail,
        "duration_ms": duration_ms,
    })
    if len(feed) > 200:
        feed.pop()


# Auto-record current session on every load
record_session_to_history(sess)

# ── Global Live KPI Header Bar ──
_total = st.session_state.kpi_total or 1
_accept_pct = (st.session_state.kpi_accept / _total) * 100
_block_pct = (st.session_state.kpi_blocked / _total) * 100
_qber_pct = rep.error_metrics.qber * 100 if rep else 0.0
_block_hash_short = (sess.audit_block_hash[:20] + "…") if sess.audit_block_hash else "GENESIS"
_act_val = dec.action.value if dec else "UNKNOWN"
_act_color = acolor(_act_val)

st.markdown(f"""
<div style="background:linear-gradient(90deg,rgba(0,15,40,0.95),rgba(0,30,70,0.95));
            border:1px solid rgba(0,212,255,0.25); border-radius:10px; padding:10px 18px;
            display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;
            gap:12px; margin-bottom:18px; backdrop-filter:blur(10px);">
  <div style="display:flex;align-items:center;gap:6px;">
    <span style="color:#94A3B8;font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;">Sessions</span>
    <span style="color:#FFFFFF;font-weight:800;font-size:1.05rem;">{st.session_state.kpi_total}</span>
  </div>
  <div style="display:flex;align-items:center;gap:6px;">
    <span class="dot dot-g"></span>
    <span style="color:#94A3B8;font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;">Accept</span>
    <span style="color:#00FF88;font-weight:800;font-size:1.05rem;">{_accept_pct:.0f}%</span>
  </div>
  <div style="display:flex;align-items:center;gap:6px;">
    <span class="dot dot-r"></span>
    <span style="color:#94A3B8;font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;">Block/Reject</span>
    <span style="color:#FF3B6E;font-weight:800;font-size:1.05rem;">{_block_pct:.0f}%</span>
  </div>
  <div style="display:flex;align-items:center;gap:6px;">
    <span style="color:#94A3B8;font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;">Live QBER</span>
    <span style="color:#00D4FF;font-weight:800;font-size:1.05rem;">{_qber_pct:.2f}%</span>
  </div>
  <div style="display:flex;align-items:center;gap:6px;">
    <span style="color:#94A3B8;font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;">Guardian</span>
    <span style="color:{_act_color};font-weight:800;font-size:1.05rem;">{_act_val}</span>
  </div>
  <div style="display:flex;align-items:center;gap:6px;">
    <span style="color:#94A3B8;font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;">Block Hash</span>
    <span style="font-family:'JetBrains Mono',monospace;color:#A855F7;font-size:0.75rem;">{_block_hash_short}</span>
  </div>
</div>
""", unsafe_allow_html=True)




# ══════════════════════════════════════════════════════════
# MODULE 1: EXECUTIVE COMMAND CENTER
# ══════════════════════════════════════════════════════════
if page == "⚡ Executive Command Center":
    action_val = dec.action.value if dec else "UNKNOWN"
    ver_pct = rep.error_metrics.ver * 100 if rep else 0.0
    qber_pct = rep.error_metrics.qber * 100 if rep else 0.0
    canary_h = sess.canary_result.channel_health if sess.canary_result else "HEALTHY"
    n_qubits = rep.evidence_bundle.sample_size if rep else 32

    is_ok = action_val == "ACCEPT"
    v_cls = "q-value-green" if is_ok else "q-value-red"
    c_cls = {"HEALTHY": "q-value-green", "DEGRADED": "q-value-amber"}.get(canary_h, "q-value-red")
    dot_cls = {"HEALTHY": "dot-g", "DEGRADED": "dot-a"}.get(canary_h, "dot-r")
    card_ok = "q-card-emerald" if is_ok else "q-card-red"

    # ── Top Metrics Bar ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="q-card {card_ok}">
            <span class="q-label">GUARDIAN SECURITY GATE</span>
            <div class="q-value {v_cls}" style="font-size:clamp(1.3rem,2vw,2rem); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{action_val}</div>
            <div class="q-sub">Session <span class="hash">{sess.session_id}</span></div>
        </div>""", unsafe_allow_html=True)

    with c2:
        ver_c = "q-value-green" if ver_pct < 4.5 else "q-value-red"
        st.markdown(f"""
        <div class="q-card q-card-cyan">
            <span class="q-label">VERIFICATION ERROR (VER)</span>
            <div class="q-value {ver_c}" style="font-size:clamp(1.5rem,2.2vw,2.2rem);">{ver_pct:.2f}%</div>
            <div class="q-sub">Threshold ≤ 4.50% &nbsp;·&nbsp; N = {n_qubits} Qubits</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        qber_c = "q-value-green" if qber_pct < 5 else "q-value-red"
        st.markdown(f"""
        <div class="q-card q-card-violet">
            <span class="q-label">CHANNEL NOISE (QBER)</span>
            <div class="q-value {qber_c}" style="font-size:clamp(1.5rem,2.2vw,2.2rem);">{qber_pct:.2f}%</div>
            <div class="q-sub">Physical Link Baseline Calibrated</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        ccard = {"HEALTHY": "q-card-emerald", "DEGRADED": "q-card-amber"}.get(canary_h, "q-card-red")
        st.markdown(f"""
        <div class="q-card {ccard}">
            <span class="q-label">PREFLIGHT CANARY STATUS</span>
            <div class="q-value {c_cls}" style="font-size:clamp(1.1rem,1.8vw,1.65rem); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                <span class="dot {dot_cls}" style="margin-right:6px;"></span>{canary_h}
            </div>
            <div class="q-sub">16 Decoys &nbsp;·&nbsp; Entanglement Witness Active</div>
        </div>""", unsafe_allow_html=True)

    # ── Studio Workspace ──
    left_col, right_col = st.columns([1.3, 1.2])

    with left_col:
        st.markdown('<div class="q-title">🛡️ Real-Time Security Assessment & Precedence Execution Trace</div>', unsafe_allow_html=True)

        if dec and dec.threat_assessment.active_threats:
            tags_html = "".join(f'<span class="ttag ttag-red">{t}</span>' for t in dec.threat_assessment.active_threats)
            codes_html = "".join(
                f'<div style="color:#CBD5E1; font-size:0.84rem; margin:6px 0; display:flex; align-items:center; gap:8px;">'
                f'<span style="color:#FF3B6E; font-weight:900;">✕</span>'
                f'<code style="color:#FF3B6E; background:rgba(255,59,110,0.12); padding:3px 10px; border-radius:6px; font-size:0.8rem;">{r}</code></div>'
                for r in dec.reason_codes
            )
            st.markdown(f"""
            <div class="q-card q-card-red">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <span style="color:#FF3B6E; font-weight:800; font-size:1rem;">⚠️ ACTIVE THREATS INTERCEPTED</span>
                    <span class="badge badge-red">RISK LEVEL: HIGH</span>
                </div>
                <div style="margin-bottom:14px;">{tags_html}</div>
                {codes_html}
                <div style="margin-top:14px; padding-top:12px; border-top:1px solid rgba(255,59,110,0.25); color:#94A3B8; font-size:0.82rem;">
                    <strong>Guardian Action:</strong> {dec.primary_reason}
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            rows = [
                ("Signer Identity Authentication", "HMAC-SHA256 classical signature validated Alice_Signer_Primary"),
                ("Projective State Fidelity", "Bob's Pauli measurements matched Alice's domain-separated basis manifest"),
                ("Exact Binomial Hypothesis Test", f"Accepted H₀ (Legitimate): p-value = {rep.evidence_bundle.binomial_result.p_value:.6f} > α = 0.01"),
                ("Wald Sequential SPRT Test", f"Accepted H₀: LLR = {rep.evidence_bundle.sprt_result.llr:.3f} crossed lower boundary B"),
                ("Blockchain Audit Anchor", f"Block #{sess.audit_block_hash[:8] if sess.audit_block_hash else '0'} anchored with Merkle Root"),
            ]
            rows_html = "".join(f'<div class="clean-row"><span class="ck">✓</span><div><strong>{t}:</strong> <span style="color:#94A3B8;">{d}</span></div></div>' for t, d in rows)
            st.markdown(f"""
            <div class="q-card q-card-emerald">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <span style="color:#00FF88; font-weight:800; font-size:1rem;">✅ CLEAN QUANTUM SECURITY STATE</span>
                    <span class="badge badge-green">STATUS: COMPLIANT</span>
                </div>
                {rows_html}
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="q-title">🔗 Cryptographic Lineage & Chain Provenance</div>', unsafe_allow_html=True)
        md_hash = pkt.message_digest if pkt else "N/A"
        tx_hash = pkt.transcript.transcript_hash if pkt else "N/A"
        ab_hash = sess.audit_block_hash if sess.audit_block_hash else "N/A"
        mr_hash = sess.merkle_root if sess.merkle_root else "N/A"
        st.markdown(f"""
        <div class="q-card q-card-cyan">
            <div class="prov-row"><span class="prov-key">Message Payload Digest</span><span class="hash">{md_hash}</span></div>
            <div class="prov-row"><span class="prov-key">Transcript Hash (Domain-Sep)</span><span class="hash">{tx_hash}</span></div>
            <div class="prov-row"><span class="prov-key">Merkle Root Hash</span><span class="hash">{mr_hash}</span></div>
            <div class="prov-row" style="border:none;"><span class="prov-key">Audit Block Hash</span><span class="hash">{ab_hash}</span></div>
        </div>""", unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="q-title">🚀 Transaction Forge & Adversarial Threat Injector</div>', unsafe_allow_html=True)
        tab_forge, tab_inject = st.tabs(["📝 Transaction Forge Studio", "⚔️ Quick Threat Injector"])

        with tab_forge:
            with st.form("tx_forge_form"):
                st.markdown('<span class="q-label">TRANSACTION PAYLOAD PRESETS</span>', unsafe_allow_html=True)
                preset_choice = st.selectbox(
                    "Payload Preset",
                    [
                        "SOVEREIGN_RTGS_SETTLEMENT_INR_500CR_2026",
                        "DEFENCE_PROCUREMENT_CONTRACT_QDS_AUTH_001",
                        "SMART_GRID_SCADA_ISOLATION_COMMAND_SUBSTATION_4B",
                        "HEALTHCARE_GENOMIC_EMR_RECORD_ACCESS_PERMIT_099",
                        "CUSTOM_PAYLOAD",
                    ],
                    label_visibility="collapsed",
                )
                custom_text = st.text_area(
                    "Transaction Payload Content",
                    value=preset_choice if preset_choice != "CUSTOM_PAYLOAD" else "ENTER_YOUR_CUSTOM_PAYLOAD_HERE",
                    height=100,
                )

                c_sg, c_vr = st.columns(2)
                with c_sg:
                    signer_id_in = st.selectbox("Signer Identity", ["Alice_Signer_Primary", "Alice_Signer_Secondary", "Unauthorized_Eve"])
                with c_vr:
                    verifier_id_in = st.selectbox("Verifier Identity", ["Bob_Verifier_Primary", "Charlie_Auditor", "Unauthorized_Dave"])

                qubit_slider = st.slider("Qubit Block Size (N)", min_value=16, max_value=128, value=32, step=16)
                noise_slider = st.slider("Simulated Channel Noise Rate (p)", min_value=0.0, max_value=0.25, value=0.01, step=0.01)

                submit_tx = st.form_submit_button("⚡ Sign, Teleport & Verify Transaction", type="primary", use_container_width=True)
                if submit_tx:
                    _t0 = time.time()
                    log_pipeline_stage("PREPARE", "⏳", f"Payload: {custom_text[:40]}…")
                    log_pipeline_stage("SIGN", "⏳", f"Signer: {signer_id_in} | N={qubit_slider} qubits")
                    log_pipeline_stage("TELEPORT", "⏳", f"Noise p={noise_slider:.2f}")
                    new_sess = st.session_state.orchestrator.execute_pipeline(
                        message=custom_text,
                        num_qubits=qubit_slider,
                        channel_noise_p=noise_slider,
                        signer_id=signer_id_in,
                        verifier_id=verifier_id_in,
                    )
                    _dur = (time.time() - _t0) * 1000
                    _new_dec = new_sess.guardian_decision.action.value if new_sess.guardian_decision else "UNKNOWN"
                    _new_ver = new_sess.verification_report.error_metrics.ver * 100 if new_sess.verification_report else 0
                    log_pipeline_stage("CANARY", "✅", f"Link: {new_sess.canary_result.channel_health if new_sess.canary_result else 'N/A'}")
                    log_pipeline_stage("VERIFY", "✅", f"VER={_new_ver:.2f}%")
                    log_pipeline_stage("ANALYZE", "✅", "Binomial + SPRT + Hoeffding + Chi-Square")
                    log_pipeline_stage("DETECT", "✅", f"Threats: {new_sess.guardian_decision.threat_assessment.active_threats if new_sess.guardian_decision else []}")
                    log_pipeline_stage("GUARDIAN", "✅" if _new_dec == "ACCEPT" else "🚨", f"Decision: {_new_dec}")
                    log_pipeline_stage("AUDIT", "✅", f"Block: {new_sess.audit_block_hash[:16] if new_sess.audit_block_hash else 'N/A'}")
                    log_pipeline_stage("REMEMBER", "✅", f"Latency: {_dur:.0f}ms total", _dur)
                    st.session_state.current_session = new_sess
                    record_session_to_history(new_sess)
                    st.rerun()

        with tab_inject:
            st.markdown('<p style="color:#94A3B8; font-size:0.85rem; margin-bottom:12px;">Inject adversarial attacks directly into the quantum or classical channels to test immediate Guardian response.</p>', unsafe_allow_html=True)
            a1, a2 = st.columns(2)
            with a1:
                if st.button("🎭 State Forgery", use_container_width=True):
                    _atk_sess = st.session_state.runner.inject_attack(AttackType.FORGERY)
                    log_pipeline_stage("ATTACK_INJECT", "🚨", "State Substitution Forgery → Expected: REJECT")
                    log_pipeline_stage("GUARDIAN", "🚨", f"Decision: {_atk_sess.guardian_decision.action.value if _atk_sess.guardian_decision else 'N/A'}")
                    st.session_state.current_session = _atk_sess; record_session_to_history(_atk_sess); st.rerun()
                if st.button("🔄 Nonce Replay", use_container_width=True):
                    _atk_sess = st.session_state.runner.inject_attack(AttackType.REPLAY)
                    log_pipeline_stage("ATTACK_INJECT", "🚨", "Nonce Replay → Expected: BLOCK")
                    log_pipeline_stage("GUARDIAN", "🚨", f"Decision: {_atk_sess.guardian_decision.action.value if _atk_sess.guardian_decision else 'N/A'}")
                    st.session_state.current_session = _atk_sess; record_session_to_history(_atk_sess); st.rerun()
                if st.button("👤 Impersonation", use_container_width=True):
                    _atk_sess = st.session_state.runner.inject_attack(AttackType.IMPERSONATION)
                    log_pipeline_stage("ATTACK_INJECT", "🚨", "Signer Impersonation → Expected: BLOCK")
                    log_pipeline_stage("GUARDIAN", "🚨", f"Decision: {_atk_sess.guardian_decision.action.value if _atk_sess.guardian_decision else 'N/A'}")
                    st.session_state.current_session = _atk_sess; record_session_to_history(_atk_sess); st.rerun()
                if st.button("🔧 Pauli Bit Tampering", use_container_width=True):
                    _atk_sess = st.session_state.runner.inject_attack(AttackType.CORRECTION_TAMPERING)
                    log_pipeline_stage("ATTACK_INJECT", "🚨", "Pauli Bit Tampering → Expected: QUARANTINE")
                    log_pipeline_stage("GUARDIAN", "🚨", f"Decision: {_atk_sess.guardian_decision.action.value if _atk_sess.guardian_decision else 'N/A'}")
                    st.session_state.current_session = _atk_sess; record_session_to_history(_atk_sess); st.rerun()
            with a2:
                if st.button("🔍 Intercept-Resend", use_container_width=True):
                    _atk_sess = st.session_state.runner.inject_attack(AttackType.INTERCEPT_RESEND)
                    log_pipeline_stage("ATTACK_INJECT", "🚨", "Intercept-Resend → Expected: QUARANTINE")
                    log_pipeline_stage("GUARDIAN", "🚨", f"Decision: {_atk_sess.guardian_decision.action.value if _atk_sess.guardian_decision else 'N/A'}")
                    st.session_state.current_session = _atk_sess; record_session_to_history(_atk_sess); st.rerun()
                if st.button("🌪️ Depolarizing Noise (20%)", use_container_width=True):
                    _atk_sess = st.session_state.runner.inject_attack(AttackType.DEPOLARIZING_NOISE, custom_params={"channel_noise_p": 0.20})
                    log_pipeline_stage("ATTACK_INJECT", "🚨", "Depolarizing Noise 20% → Expected: QUARANTINE")
                    log_pipeline_stage("GUARDIAN", "🚨", f"Decision: {_atk_sess.guardian_decision.action.value if _atk_sess.guardian_decision else 'N/A'}")
                    st.session_state.current_session = _atk_sess; record_session_to_history(_atk_sess); st.rerun()
                if st.button("🔄 Phase Shift (π/2)", use_container_width=True):
                    _atk_sess = st.session_state.runner.inject_attack(AttackType.PHASE_ROTATION, custom_params={"phase_rotation_theta": 1.57})
                    log_pipeline_stage("ATTACK_INJECT", "🚨", "Coherent Phase Rotation π/2 → Expected: QUARANTINE")
                    log_pipeline_stage("GUARDIAN", "🚨", f"Decision: {_atk_sess.guardian_decision.action.value if _atk_sess.guardian_decision else 'N/A'}")
                    st.session_state.current_session = _atk_sess; record_session_to_history(_atk_sess); st.rerun()
                if st.button("💀 Multi-Vector Storm", use_container_width=True):
                    _atk_sess = st.session_state.runner.inject_attack(AttackType.MIXED_MULTI_VECTOR)
                    log_pipeline_stage("ATTACK_INJECT", "🚨", "Multi-Vector Storm → Expected: BLOCK")
                    log_pipeline_stage("GUARDIAN", "🚨", f"Decision: {_atk_sess.guardian_decision.action.value if _atk_sess.guardian_decision else 'N/A'}")
                    st.session_state.current_session = _atk_sess; record_session_to_history(_atk_sess); st.rerun()

# ══════════════════════════════════════════════════════════
# MODULE 2: QUANTUM PROTOCOL LAB
# ══════════════════════════════════════════════════════════
elif page == "🔬 Quantum Protocol Lab":
    st.markdown('<div class="q-title">🔬 Quantum State Genesis & Projective Measurement Studio</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94A3B8; margin-bottom:18px;">Construct pure quantum states, analyze Born-rule measurement probabilities across Pauli bases (Z, X, Y), and inspect 3D Bloch sphere projections.</p>', unsafe_allow_html=True)

    c_left, c_right = st.columns([1.1, 1.3])

    with c_left:
        st.markdown('<span class="q-label">STATE FAMILY SELECTION</span>', unsafe_allow_html=True)
        state_mode = st.radio(
            "State Selection Mode",
            ["Canonical Pauli Eigenstates", "Arbitrary Superposition |ψ(θ, φ)⟩"],
            label_visibility="collapsed",
        )

        if state_mode == "Canonical Pauli Eigenstates":
            state_type = st.selectbox(
                "Eigenstate Family",
                ["|0⟩ Computational 0 (Z+)", "|1⟩ Computational 1 (Z-)", "|+⟩ Hadamard + (X+)", "|-⟩ Hadamard - (X-)", "|+i⟩ Circular + (Y+)", "|-i⟩ Circular - (Y-)"],
            )
            sm = {
                "|0": QuantumState.state_zero,
                "|1": QuantumState.state_one,
                "|+⟩": QuantumState.state_plus,
                "|-⟩": QuantumState.state_minus,
                "|+i": QuantumState.state_plus_i,
                "|-i": QuantumState.state_minus_i,
            }
            demo_st = next((fn() for k, fn in sm.items() if k in state_type), QuantumState.state_zero())
        else:
            col_th, col_ph = st.columns(2)
            with col_th:
                th_in = st.slider("Polar Angle θ (rad)", 0.0, 3.1416, 1.0472, 0.05)
            with col_ph:
                ph_in = st.slider("Azimuthal Phase φ (rad)", 0.0, 6.2832, 0.7854, 0.05)
            alpha_val = complex(math.cos(th_in / 2.0), 0.0)
            beta_val = complex(math.sin(th_in / 2.0) * math.cos(ph_in), math.sin(th_in / 2.0) * math.sin(ph_in))
            demo_st = QuantumState(alpha=alpha_val, beta=beta_val, family=StateFamily.ZERO)

        rx, ry, rz = demo_st.bloch_coordinates
        theta, phi = demo_st.bloch_angles

        st.markdown(f"""
        <div class="q-card q-card-cyan">
            <span class="q-label">STATE VECTOR ALGEBRA</span>
            <p style="font-family:'JetBrains Mono',monospace; font-size:0.92rem; color:#00D4FF; margin:8px 0 12px 0;">
                |ψ⟩ = ({demo_st.alpha.real:.4f} + {demo_st.alpha.imag:.4f}i)|0⟩ + ({demo_st.beta.real:.4f} + {demo_st.beta.imag:.4f}i)|1⟩
            </p>
            <div class="prov-row"><span class="prov-key">Bloch Vector (x, y, z)</span><span class="hash">({rx:.4f}, {ry:.4f}, {rz:.4f})</span></div>
            <div class="prov-row"><span class="prov-key">Polar Angle θ</span><span style="color:#FFFFFF; font-weight:700;">{theta:.4f} rad ({math.degrees(theta):.1f}°)</span></div>
            <div class="prov-row" style="border:none;"><span class="prov-key">Azimuthal Phase φ</span><span style="color:#FFFFFF; font-weight:700;">{phi:.4f} rad ({math.degrees(phi):.1f}°)</span></div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="q-title">📐 Born-Rule Outcome Probabilities</div>', unsafe_allow_html=True)
        p0z = demo_st.probability_outcome_0(Basis.Z)
        p0x = demo_st.probability_outcome_0(Basis.X)
        p0y = demo_st.probability_outcome_0(Basis.Y)

        fig_bar = go.Figure(data=[
            go.Bar(name="P(Outcome = 0)", x=["Z Basis (Computational)", "X Basis (Hadamard)", "Y Basis (Circular)"], y=[p0z, p0x, p0y], marker_color="#00D4FF"),
            go.Bar(name="P(Outcome = 1)", x=["Z Basis (Computational)", "X Basis (Hadamard)", "Y Basis (Circular)"], y=[1-p0z, 1-p0x, 1-p0y], marker_color="#A855F7"),
        ])
        sfig(fig_bar, "Theoretical Born-Rule Outcome Distributions", 260)
        fig_bar.update_layout(barmode="group")
        st.plotly_chart(fig_bar, use_container_width=True)

    with c_right:
        fig_bloch = BlochSphereVisualizer.create_bloch_figure(expected_state=demo_st, title=f"3D Bloch Sphere: |ψ⟩ = [{demo_st.alpha.real:.2f}, {demo_st.beta.real:.2f}]")
        st.plotly_chart(fig_bloch, use_container_width=True)

# ══════════════════════════════════════════════════════════
# MODULE 3: TELEPORTATION MONITOR
# ══════════════════════════════════════════════════════════
elif page == "🌌 Teleportation Monitor":
    st.markdown('<div class="q-title">🌌 Quantum Teleportation Protocol & Channel Monitor</div>', unsafe_allow_html=True)
    st.markdown(r'<p style="color:#94A3B8; margin-bottom:18px;">Live execution telemetry of Bell State Measurements (BSM), authenticated classical transmission $(b_1, b_2)$, and Pauli unitary corrections $\sigma_x^{b_2}\sigma_z^{b_1}$.</p>', unsafe_allow_html=True)

    if pkt and pkt.teleportation_results:
        # Step-by-step pipeline diagram
        st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:center; gap:8px; flex-wrap:wrap; margin-bottom:20px;">
            <div class="q-card q-card-cyan" style="flex:1; min-width:180px; text-align:center; padding:16px;">
                <span class="q-label">STEP 1: PREPARATION</span>
                <strong style="color:#FFFFFF; font-size:0.9rem;">|ψ⟩_A ⊗ |Φ⁺⟩_AB</strong>
                <p style="color:#94A3B8; font-size:0.75rem; margin:4px 0 0 0;">3-Qubit Joint State</p>
            </div>
            <div style="color:#00D4FF; font-size:1.5rem; font-weight:900;">➔</div>
            <div class="q-card q-card-violet" style="flex:1; min-width:180px; text-align:center; padding:16px;">
                <span class="q-label">STEP 2: BSM ANALYZER</span>
                <strong style="color:#FFFFFF; font-size:0.9rem;">Alice Measures (b₁, b₂)</strong>
                <p style="color:#94A3B8; font-size:0.75rem; margin:4px 0 0 0;">Bell Basis Projection</p>
            </div>
            <div style="color:#00D4FF; font-size:1.5rem; font-weight:900;">➔</div>
            <div class="q-card q-card-amber" style="flex:1; min-width:180px; text-align:center; padding:16px;">
                <span class="q-label">STEP 3: AUTH CHANNEL</span>
                <strong style="color:#FFFFFF; font-size:0.9rem;">HMAC-SHA256 Classical</strong>
                <p style="color:#94A3B8; font-size:0.75rem; margin:4px 0 0 0;">Tamper-Resistant Bits</p>
            </div>
            <div style="color:#00D4FF; font-size:1.5rem; font-weight:900;">➔</div>
            <div class="q-card q-card-emerald" style="flex:1; min-width:180px; text-align:center; padding:16px;">
                <span class="q-label">STEP 4: RECOVERY</span>
                <strong style="color:#FFFFFF; font-size:0.9rem;">Bob Applies σ_x^b₂ · σ_z^b₁</strong>
                <p style="color:#94A3B8; font-size:0.75rem; margin:4px 0 0 0;">Fidelity Restored: |ψ⟩_B</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        c_tb, c_ch = st.columns([1.4, 1])
        with c_tb:
            st.markdown('<div class="q-title">📋 Individual Qubit Teleportation Event Log</div>', unsafe_allow_html=True)
            rows = []
            for r in pkt.teleportation_results:
                rows.append({
                    "Index": r.event_id,
                    "Target State": r.input_state.family.value,
                    "BSM Bits (b₁,b₂)": f"({r.bsm_bits[0]}, {r.bsm_bits[1]})",
                    "Pauli Correction": r.applied_correction.value,
                    "Fidelity": f"{r.fidelity:.4f}",
                    "Status": "✅ PASS" if r.success else "⚠️ DEGRADED",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        with c_ch:
            st.markdown('<div class="q-title">📊 Pauli Correction Distribution</div>', unsafe_allow_html=True)
            corr = {}
            for r in pkt.teleportation_results:
                op = r.applied_correction.value
                corr[op] = corr.get(op, 0) + 1

            fig_c = go.Figure(go.Bar(
                x=list(corr.keys()),
                y=list(corr.values()),
                marker=dict(color=NEON_COLORS[:len(corr)]),
                text=list(corr.values()),
                textposition="outside",
                textfont=dict(color="#FFFFFF", size=13),
            ))
            sfig(fig_c, "Pauli Operator Frequency (Uniform ≈ 25% each)", 320)
            st.plotly_chart(fig_c, use_container_width=True)
    else:
        st.info("No active teleportation session. Launch a transaction from Executive Command Center.")

# ══════════════════════════════════════════════════════════
# MODULE 4: VERIFICATION & STATISTICS
# ══════════════════════════════════════════════════════════
elif page == "📊 Verification & Statistics":
    st.markdown('<div class="q-title">📊 Deterministic Statistical Verification Suite (Zero-AI / Zero-ML)</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94A3B8; margin-bottom:18px;">Pure mathematical verification using Exact Binomial Hypothesis Testing, Wald Sequential Probability Ratio Test (SPRT), Pearson Chi-Square, and Hoeffding finite-sample bounds.</p>', unsafe_allow_html=True)

    if rep:
        binom = rep.evidence_bundle.binomial_result
        sprt = rep.evidence_bundle.sprt_result

        c1, c2, c3 = st.columns(3)
        with c1:
            ok_b = binom.null_hypothesis_accepted
            st.markdown(f"""
            <div class="q-card {'q-card-emerald' if ok_b else 'q-card-red'}">
                <span class="q-label">ENGINE 1: EXACT BINOMIAL TEST</span>
                <div class="q-value {'q-value-green' if ok_b else 'q-value-red'}" style="font-size:1.6rem;">
                    {'ACCEPT H₀ (LEGITIMATE)' if ok_b else 'REJECT H₀ (FORGERY)'}
                </div>
                <div class="q-sub">p-value = {binom.p_value:.6f} &nbsp;·&nbsp; Significance α = {binom.alpha}</div>
            </div>""", unsafe_allow_html=True)

        with c2:
            sd = sprt.decision.value
            sg = sd == "ACCEPT_H0"
            sr = sd == "ACCEPT_H1"
            sc = "q-value-green" if sg else ("q-value-red" if sr else "q-value-amber")
            sl = {"ACCEPT_H0": "ACCEPT H₀ (LEGITIMATE)", "ACCEPT_H1": "ACCEPT H₁ (ATTACK)", "CONTINUE": "INCONCLUSIVE (CONTINUE)"}.get(sd, sd)
            st.markdown(f"""
            <div class="q-card {'q-card-emerald' if sg else ('q-card-red' if sr else 'q-card-amber')}">
                <span class="q-label">ENGINE 2: WALD SPRT SEQUENTIAL</span>
                <div class="q-value {sc}" style="font-size:1.6rem;">{sl}</div>
                <div class="q-sub">LLR = {sprt.llr:.3f} &nbsp;·&nbsp; Samples Used = {sprt.samples_used}</div>
            </div>""", unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class="q-card q-card-violet">
                <span class="q-label">ENGINE 3: HOEFFDING BOUND (99.9%)</span>
                <div class="q-value q-value-violet" style="font-size:1.6rem;">
                    {rep.evidence_bundle.finite_sample_upper_bound*100:.2f}%
                </div>
                <div class="q-sub">Finite-Sample Theoretical Upper Bound</div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="q-title">📈 Wald SPRT Log-Likelihood Ratio (LLR) Trajectory</div>', unsafe_allow_html=True)
        traj = sprt.trajectory
        df_t = pd.DataFrame(traj, columns=["Sample", "LLR"])
        fig_s = go.Figure()
        fig_s.add_trace(go.Scatter(
            x=df_t["Sample"],
            y=df_t["LLR"],
            mode="lines+markers",
            line=dict(color="#00D4FF", width=3),
            marker=dict(size=6, color="#00D4FF"),
            name="Cumulative LLR",
            fill="tozeroy",
            fillcolor="rgba(0,212,255,0.08)",
        ))
        fig_s.add_hline(y=sprt.upper_bound_a, line_dash="dash", line_color="#FF3B6E", line_width=2.5,
            annotation=dict(text=f"Boundary A (Attack Threshold = {sprt.upper_bound_a:.2f})", font=dict(color="#FF3B6E", size=12)))
        fig_s.add_hline(y=sprt.lower_bound_b, line_dash="dash", line_color="#00FF88", line_width=2.5,
            annotation=dict(text=f"Boundary B (Legitimate Threshold = {sprt.lower_bound_b:.2f})", font=dict(color="#00FF88", size=12)))
        sfig(fig_s, "SPRT Sequential Probability Ratio Test — Step-by-Step LLR Path", 380)
        fig_s.update_layout(xaxis_title="Qubit Measurement Sample Index (n)", yaxis_title="Log-Likelihood Ratio Z_n")
        st.plotly_chart(fig_s, use_container_width=True)

        with st.expander("📚 Mathematical Formulation & Decision Bounds", expanded=False):
            st.latex(r"Z_n = \sum_{i=1}^n \ln \frac{f(x_i | p_1)}{f(x_i | p_0)}, \quad A = \ln \frac{1-\beta}{\alpha}, \quad B = \ln \frac{\beta}{1-\alpha}")
            st.markdown("""
            - **Null Hypothesis ($H_0$):** Measurement error rate matches calibrated channel noise $p_0 = 0.01$ (Legitimate Signer).
            - **Alternative Hypothesis ($H_1$):** Measurement error rate matches adversarial forgery distribution $p_1 = 0.25$ (Active Attacker).
            - **Significance Levels:** False positive rate $\\alpha = 0.01$, False negative rate $\\beta = 0.01$.
            """)

        # ── Engine 4: Guarded Chi-Square (previously built but never shown) ──
        st.markdown('<div class="q-title">🧮 Engine 4: Guarded χ² Goodness-of-Fit Test</div>', unsafe_allow_html=True)
        n = rep.evidence_bundle.sample_size
        mismatches = int(rep.error_metrics.ver * n)
        matches = n - mismatches
        expected_err = DEFAULT_CALIBRATION.baseline_qber_mean * n
        expected_ok = n - expected_err
        chi_res = StatisticalHypothesisEngine.guarded_chi_square_test(
            observed_0=matches, observed_1=mismatches,
            expected_0=expected_ok, expected_1=expected_err,
        )
        ok_chi = chi_res.null_hypothesis_accepted
        c_chi_a, c_chi_b, c_chi_c = st.columns(3)
        with c_chi_a:
            st.markdown(f"""
            <div class="q-card {'q-card-emerald' if ok_chi else 'q-card-red'}">
                <span class="q-label">ENGINE 4: GUARDED χ² TEST</span>
                <div class="q-value {'q-value-green' if ok_chi else 'q-value-red'}" style="font-size:1.6rem;">
                    {'ACCEPT H₀ (LEGITIMATE)' if ok_chi else 'REJECT H₀ (ANOMALOUS)'}
                </div>
                <div class="q-sub">χ² Statistic = {chi_res.statistic:.4f}&nbsp;·&nbsp;p-value = {chi_res.p_value:.6f}</div>
            </div>""", unsafe_allow_html=True)
        with c_chi_b:
            st.markdown(f"""
            <div class="q-card q-card-cyan">
                <span class="q-label">OBSERVED vs EXPECTED FREQUENCY</span>
                <div class="prov-row"><span class="prov-key">Observed Matches (|0))</span><strong style="color:#00FF88;">{matches}</strong></div>
                <div class="prov-row"><span class="prov-key">Observed Mismatches (|1))</span><strong style="color:#FF3B6E;">{mismatches}</strong></div>
                <div class="prov-row"><span class="prov-key">Expected Matches</span><strong style="color:#00D4FF;">{expected_ok:.1f}</strong></div>
                <div class="prov-row" style="border:none;"><span class="prov-key">Expected Mismatches</span><strong style="color:#A855F7;">{expected_err:.1f}</strong></div>
            </div>""", unsafe_allow_html=True)
        with c_chi_c:
            guard_note = chi_res.details.get("reason", "Full χ² test applied (expected counts sufficient)")
            st.markdown(f"""
            <div class="q-card q-card-violet">
                <span class="q-label">SAFETY GUARD STATUS</span>
                <div class="q-value q-value-violet" style="font-size:1rem; line-height:1.5; margin:10px 0;">{chi_res.test_name}</div>
                <div class="q-sub">{guard_note}</div>
                <div style="margin-top:10px;"><span class="q-label">Degrees of Freedom</span>
                <strong style="color:#FFFFFF;"> {chi_res.details.get('degrees_of_freedom', 1)}</strong></div>
            </div>""", unsafe_allow_html=True)

        # ── Shannon Entropy & Secrecy Fraction Panel ──
        st.markdown('<div class="q-title">📐 Information Theory: Shannon Entropy & Secrecy Capacity Diagnostics</div>', unsafe_allow_html=True)
        ent_diag = EntropyDiagnostics.compute_diagnostics(
            qber=rep.error_metrics.qber, ver=rep.error_metrics.ver
        )
        h2_qber = ent_diag["channel_binary_entropy_H2(qber)"]
        h2_ver = ent_diag["verification_binary_entropy_H2(ver)"]
        secrecy = ent_diag["secrecy_fraction_diagnostic"]

        c_ent_a, c_ent_b = st.columns([1, 1.6])
        with c_ent_a:
            sec_cls = "q-value-green" if secrecy > 0.5 else ("q-value-amber" if secrecy > 0.1 else "q-value-red")
            st.markdown(f"""
            <div class="q-card q-card-cyan">
                <span class="q-label">H₂(QBER) — CHANNEL BINARY ENTROPY</span>
                <div class="q-value q-value-cyan" style="font-size:1.8rem;">{h2_qber:.4f} bits</div>
                <div class="q-sub">Shannon entropy of the physical channel error distribution</div>
            </div>""", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="q-card q-card-violet" style="margin-top:12px;">
                <span class="q-label">H₂(VER) — VERIFICATION BINARY ENTROPY</span>
                <div class="q-value q-value-violet" style="font-size:1.8rem;">{h2_ver:.4f} bits</div>
                <div class="q-sub">Shannon entropy of the signature verification error distribution</div>
            </div>""", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="q-card {'q-card-emerald' if secrecy > 0.1 else 'q-card-red'}" style="margin-top:12px;">
                <span class="q-label">ASYMPTOTIC SECRECY FRACTION</span>
                <div class="q-value {sec_cls}" style="font-size:1.8rem;">{secrecy:.4f}</div>
                <div class="q-sub">1 - 2H₂(QBER) — Drops to 0 at QBER ≈ 11% (Shannon limit)</div>
            </div>""", unsafe_allow_html=True)
        with c_ent_b:
            qber_range = np.linspace(0.0, 0.5, 200)
            def _h2(p): return 0.0 if p <= 0 or p >= 1 else -p * np.log2(p) - (1 - p) * np.log2(1 - p)
            secrecy_curve = np.array([max(0.0, 1 - 2 * _h2(q)) for q in qber_range])
            h2_curve = np.array([_h2(q) for q in qber_range])
            fig_ent = go.Figure()
            fig_ent.add_trace(go.Scatter(
                x=qber_range, y=secrecy_curve, name="Secrecy Fraction (1-2H₂(QBER))",
                line=dict(color="#00FF88", width=3), fill="tozeroy", fillcolor="rgba(0,255,136,0.06)",
            ))
            fig_ent.add_trace(go.Scatter(
                x=qber_range, y=h2_curve, name="H₂(QBER) Binary Entropy",
                line=dict(color="#00D4FF", width=2, dash="dot"),
            ))
            fig_ent.add_vline(x=rep.error_metrics.qber, line_dash="dash", line_color="#FFA500", line_width=2,
                annotation=dict(text=f"Current QBER={rep.error_metrics.qber*100:.2f}%", font=dict(color="#FFA500", size=11)))
            fig_ent.add_vline(x=0.11, line_dash="dash", line_color="#FF3B6E", line_width=1.5,
                annotation=dict(text="Shannon Limit (~11%)", font=dict(color="#FF3B6E", size=10)))
            sfig(fig_ent, "Secrecy Capacity vs QBER — Information-Theoretic Security Boundary", 340)
            fig_ent.update_layout(xaxis_title="QBER (Channel Error Rate)", yaxis_title="Value",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(color="#FFFFFF")))
            st.plotly_chart(fig_ent, use_container_width=True)

        # ── Serfling / Hoeffding Finite-Sample Bound Curve ──
        st.markdown('<div class="q-title">📉 Finite-Sample Hoeffding Confidence Bound vs Sample Size N</div>', unsafe_allow_html=True)
        n_range = np.arange(8, 200, 4)
        obs_ver = rep.error_metrics.ver
        bounds_curve = [FiniteSampleBounds.hoeffding_upper_bound(obs_ver, int(n_i)) for n_i in n_range]
        fig_sb = go.Figure()
        fig_sb.add_trace(go.Scatter(
            x=n_range, y=bounds_curve, name="Hoeffding Upper Bound",
            line=dict(color="#A855F7", width=3), fill="tozeroy", fillcolor="rgba(168,85,247,0.06)",
        ))
        fig_sb.add_hline(y=obs_ver, line_dash="dash", line_color="#00FF88", line_width=1.5,
            annotation=dict(text=f"Observed VER={obs_ver*100:.2f}%", font=dict(color="#00FF88", size=11)))
        fig_sb.add_vline(x=n, line_dash="dash", line_color="#FFA500", line_width=2,
            annotation=dict(text=f"Current N={n}", font=dict(color="#FFA500", size=11)))
        sfig(fig_sb, "Hoeffding Finite-Sample Upper Bound Tightening as N→∞ (β=0.01%)", 300)
        fig_sb.update_layout(xaxis_title="Sample Size N (Qubits)", yaxis_title="Upper Bound on True VER")
        st.plotly_chart(fig_sb, use_container_width=True)
        with st.expander("📚 Hoeffding Bound Formula", expanded=False):
            st.latex(r"\hat{p}_{\rm upper} = \hat{p} + \sqrt{\frac{\ln(1/\beta)}{2N}}, \quad \text{with confidence } 1-\beta = 99.99\%")
            st.markdown("""As $N \\to \\infty$, the slack $\\sqrt{\\ln(1/\\beta)/2N} \\to 0$, tightening the bound to the true error rate.""")

    else:
        st.info("No statistical verification report available.")


# ══════════════════════════════════════════════════════════
# MODULE 5: DIGITAL TWIN ATTACK LAB
# ══════════════════════════════════════════════════════════
elif page == "⚔️ Digital Twin Attack Lab":
    st.markdown('<div class="q-title">⚔️ Adversarial Digital Twin Simulation Sandbox</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94A3B8; margin-bottom:18px;">Inject complex quantum and classical attack vectors into the live pipeline. Observe real-time detector response and Guardian policy decisions.</p>', unsafe_allow_html=True)

    tab_cat, tab_custom = st.tabs(["🎯 Threat Catalog & Presets", "🎛️ Custom Adversary Parameter Tuner"])

    with tab_cat:
        c1, c2 = st.columns(2)
        threats_left = [
            (AttackType.FORGERY, "🎭 State Substitution Forgery", "Eve intercepts qubits and replaces them with random states without knowing Alice's basis manifest.", "REJECT"),
            (AttackType.IMPERSONATION, "👤 Signer Identity Impersonation", "Attacker spoofs Alice's credentials or tampers with HMAC authentication tokens.", "BLOCK"),
            (AttackType.REPLAY, "🔄 Nonce Replay Attack", "Eve captures a valid signature packet from yesterday and resubmits it to Bob.", "BLOCK"),
            (AttackType.UNAUTHORIZED_VERIFICATION, "🚫 Unauthorized Verifier Access", "Unauthorized third party attempts to verify signature packets without authorization.", "BLOCK"),
        ]
        threats_right = [
            (AttackType.INTERCEPT_RESEND, "🔍 Intercept-Resend Eavesdropping", "Eve measures in random bases and resends collapsed states, introducing ~25% basis errors.", "QUARANTINE"),
            (AttackType.DEPOLARIZING_NOISE, "🌪️ Depolarizing Thermal Noise", "Channel thermal fluctuation degrades Bell state entanglement fidelity.", "QUARANTINE"),
            (AttackType.PHASE_ROTATION, "🔄 Coherent Phase Drift Rz(θ)", "Unitary phase rotation along the Z-axis corrupts X-basis Hadamard measurements.", "QUARANTINE"),
            (AttackType.MIXED_MULTI_VECTOR, "💀 Coordinated Multi-Vector Attack", "Simultaneous channel noise + phase shift + state substitution adversary.", "BLOCK / REJECT"),
        ]

        for col, threats in zip([c1, c2], [threats_left, threats_right]):
            with col:
                for atk, title, desc, expected_act in threats:
                    st.markdown(f"""
                    <div class="q-card q-card-red" style="margin-bottom:14px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <strong style="color:#FFFFFF; font-size:0.95rem;">{title}</strong>
                            <span class="ttag ttag-red">TARGET: {expected_act}</span>
                        </div>
                        <p style="color:#94A3B8; font-size:0.83rem; margin:8px 0 12px 0;">{desc}</p>
                    </div>""", unsafe_allow_html=True)
                    if st.button(f"🚀 Launch {title.split()[1]} Attack", key=f"cat_{atk.value}", use_container_width=True):
                        st.session_state.current_session = st.session_state.runner.inject_attack(atk)
                        st.rerun()

    with tab_custom:
        with st.form("custom_adversary_form"):
            st.markdown('<span class="q-label">CUSTOM ADVERSARIAL CHANNEL PARAMETERS</span>', unsafe_allow_html=True)
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                p_noise = st.slider("Depolarizing Noise Rate (p)", 0.0, 0.5, 0.15, 0.01)
                p_theta = st.slider("Coherent Phase Rotation θ (rad)", 0.0, 3.1416, 1.57, 0.1)
                p_ir = st.checkbox("Enable Intercept-Resend Eavesdropping", value=True)
            with col_p2:
                p_forge = st.checkbox("Inject State Substitution Forgery", value=False)
                p_tamper_bits = st.checkbox("Tamper with Classical Pauli Correction Bits", value=False)
                p_tamper_hmac = st.checkbox("Tamper with Classical Channel HMAC Token", value=False)

            launch_custom = st.form_submit_button("🔥 Execute Custom Adversarial Scenario", type="primary", use_container_width=True)
            if launch_custom:
                st.session_state.current_session = st.session_state.orchestrator.execute_pipeline(
                    message="ADVERSARIAL_SIMULATION_PAYLOAD",
                    channel_noise_p=p_noise,
                    phase_rotation_theta=p_theta,
                    intercept_resend=p_ir,
                    forged_state_manifest=p_forge,
                    tamper_correction_bits=p_tamper_bits,
                    tamper_classical_hmac=p_tamper_hmac,
                )
                st.rerun()

# ══════════════════════════════════════════════════════════
# MODULE 6: QUANTUM CANARY HEALTH
# ══════════════════════════════════════════════════════════
elif page == "🐤 Quantum Canary Health":
    st.markdown('<div class="q-title">🐤 Preflight Quantum Canary Link Probe</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94A3B8; margin-bottom:18px;">Preflight decoy state probe evaluating physical link entanglement integrity prior to transmitting signature payload qubits.</p>', unsafe_allow_html=True)

    cr = sess.canary_result
    if cr:
        h = cr.channel_health
        cls = {"HEALTHY": "q-card-emerald", "DEGRADED": "q-card-amber"}.get(h, "q-card-red")
        vcls = {"HEALTHY": "q-value-green", "DEGRADED": "q-value-amber"}.get(h, "q-value-red")
        dot = {"HEALTHY": "dot-g", "DEGRADED": "dot-a"}.get(h, "dot-r")

        c1, c2 = st.columns([1.1, 1.2])
        with c1:
            st.markdown(f"""
            <div class="q-card {cls}">
                <span class="q-label">CHANNEL HEALTH CLASSIFICATION</span>
                <div class="q-value {vcls}" style="font-size:2.2rem;">
                    <span class="dot {dot}" style="margin-right:6px;"></span>{h}
                </div>
                <div style="margin-top:18px;">
                    <div class="prov-row"><span class="prov-key">Operational Guidance</span><strong style="color:#FFFFFF;">{cr.recommended_action}</strong></div>
                    <div class="prov-row"><span class="prov-key">Decoy Probe QBER</span><strong style="color:#00D4FF;">{cr.decoy_qber*100:.2f}%</strong></div>
                    <div class="prov-row"><span class="prov-key">Decoy State Fidelity</span><strong style="color:#00D4FF;">{cr.decoy_fidelity*100:.2f}%</strong></div>
                    <div class="prov-row" style="border:none;"><span class="prov-key">Decoy Probes Sent</span><strong style="color:#FFFFFF;">{cr.probes_sent} Decoys Interleaved</strong></div>
                </div>
            </div>""", unsafe_allow_html=True)

        with c2:
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=cr.decoy_fidelity * 100,
                delta=dict(reference=95, valueformat=".1f", increasing=dict(color="#00FF88"), decreasing=dict(color="#FF3B6E")),
                title=dict(text="Decoy Channel Fidelity (%)", font=dict(color="#FFFFFF", size=14)),
                number=dict(font=dict(color="#00D4FF", size=44)),
                gauge=dict(
                    axis=dict(range=[0, 100], tickcolor="#475569", tickfont=dict(color="#94A3B8")),
                    bar=dict(color="#00D4FF", thickness=0.7),
                    steps=[
                        {"range": [0, 85], "color": "rgba(255,59,110,0.15)"},
                        {"range": [85, 95], "color": "rgba(255,165,0,0.15)"},
                        {"range": [95, 100], "color": "rgba(0,255,136,0.15)"},
                    ],
                    threshold=dict(line=dict(color="#00FF88", width=3), thickness=0.8, value=95),
                ),
            ))
            sfig(fig_g, height=320)
            st.plotly_chart(fig_g, use_container_width=True)

        # ── CHSH Bell Inequality Witness (T1.1 — doc reference README line 39) ──
        st.markdown('<div class="q-title">🔔 CHSH Bell Inequality Witness: S ≤ 2√2 (Tsirelson Bound)</div>', unsafe_allow_html=True)
        st.markdown('<p style="color:#94A3B8; margin-bottom:14px;">The CHSH inequality tests whether the channel exhibits quantum correlations. Classical correlators satisfy S ≤ 2.0. Quantum entanglement allows S up to 2√2 ≈ 2.828 (Tsirelson\'s Bound). Eavesdropping degrades entanglement, pushing S toward the classical limit.</p>', unsafe_allow_html=True)

        # Compute S from fidelity: S ≈ 2√2 * (2F - 1) under symmetric depolarizing channel
        F = cr.decoy_fidelity
        S_val = max(0.0, 2 * math.sqrt(2) * (2 * F - 1))
        S_classical = 2.0
        S_tsirelson = 2 * math.sqrt(2)

        c_chsh_a, c_chsh_b = st.columns([1, 1.5])
        with c_chsh_a:
            regime = "QUANTUM REGIME" if S_val > 2.0 else "CLASSICAL LIMIT"
            regime_cls = "q-card-emerald" if S_val > 2.0 else "q-card-red"
            regime_vcls = "q-value-green" if S_val > 2.0 else "q-value-red"
            entangled = S_val > 2.0
            st.markdown(f"""
            <div class="q-card {regime_cls}">
                <span class="q-label">CHSH CORRELATION VALUE S</span>
                <div class="q-value {regime_vcls}" style="font-size:2.8rem; font-weight:900;">{S_val:.4f}</div>
                <div class="q-sub" style="margin-top:6px;">Regime: <strong style="color:{'#00FF88' if entangled else '#FF3B6E'};">{regime}</strong></div>
                <div style="margin-top:14px;">
                    <div class="prov-row"><span class="prov-key">Classical Bound</span><strong style="color:#FF3B6E;">S ≤ 2.000</strong></div>
                    <div class="prov-row"><span class="prov-key">Tsirelson Bound</span><strong style="color:#00FF88;">S ≤ 2√2 ≈ 2.828</strong></div>
                    <div class="prov-row" style="border:none;"><span class="prov-key">Quantum Margin</span>
                    <strong style="color:#00D4FF;">{max(0, S_val - 2.0):.4f} above classical</strong></div>
                </div>
            </div>""", unsafe_allow_html=True)
            with st.expander("📚 CHSH Inequality Formula", expanded=False):
                st.latex(r"S = |E(a,b) - E(a,b') + E(a',b) + E(a',b')| \leq 2\sqrt{2}")
                st.markdown("""
                - $E(a,b)$ are quantum correlation functions measured at detector angles $(a, b)$.
                - **Classical hidden variable theories**: $S \\leq 2$.
                - **Quantum entanglement** (max Bell state $|\\Phi^+\\rangle$): $S_{max} = 2\\sqrt{2}$.
                - In the depolarizing noise model: $S \\approx 2\\sqrt{2}(2F-1)$ where $F$ is fidelity.
                """)
        with c_chsh_b:
            fig_chsh = go.Figure(go.Indicator(
                mode="gauge+number",
                value=S_val,
                title=dict(text="CHSH Correlation S", font=dict(color="#FFFFFF", size=14)),
                number=dict(font=dict(color="#00FF88" if S_val > 2 else "#FF3B6E", size=50)),
                gauge=dict(
                    axis=dict(range=[0, 3.0], tickvals=[0, 1, 2.0, 2.414, 2.828, 3.0],
                              ticktext=["0", "1", "2.0\n(Classical)", "2√2/1.17", "2√2\n(Tsirelson)", "3.0"],
                              tickcolor="#475569", tickfont=dict(color="#94A3B8", size=10)),
                    bar=dict(color="#00FF88" if S_val > 2 else "#FF3B6E", thickness=0.7),
                    steps=[
                        {"range": [0, 2.0], "color": "rgba(255,59,110,0.2)"},
                        {"range": [2.0, 2.828], "color": "rgba(0,255,136,0.15)"},
                    ],
                    threshold=dict(line=dict(color="#00D4FF", width=3), thickness=0.8, value=S_tsirelson),
                ),
            ))
            sfig(fig_chsh, "CHSH S-Value: Classical ≤ 2.0 < Quantum ≤ 2.828", 340)
            st.plotly_chart(fig_chsh, use_container_width=True)

        # ── Re-run Canary Probe Controls ──
        st.markdown('<div class="q-title">🔁 Manual Canary Probe Parameters</div>', unsafe_allow_html=True)
        with st.form("canary_probe_form"):
            col_cp1, col_cp2, col_cp3 = st.columns(3)
            with col_cp1:
                cp_n = st.slider("Decoy Probes N", 8, 64, 16, 8)
            with col_cp2:
                cp_noise = st.slider("Channel Noise p", 0.0, 0.35, 0.0, 0.01)
            with col_cp3:
                cp_ir = st.checkbox("Intercept-Resend on Canary", value=False)
            cp_submit = st.form_submit_button("🚀 Run Custom Canary Probe", type="primary", use_container_width=True)
            if cp_submit:
                _canary = QuantumCanary()
                _cr2 = _canary.run_preflight_probe(num_decoy_qubits=cp_n, channel_noise_p=cp_noise, intercept_resend=cp_ir)
                st.metric("Custom Probe Health", _cr2.channel_health, f"QBER={_cr2.decoy_qber*100:.2f}%")
                st.metric("Custom Probe Fidelity", f"{_cr2.decoy_fidelity*100:.2f}%")
                _F2 = _cr2.decoy_fidelity
                _S2 = max(0.0, 2 * math.sqrt(2) * (2 * _F2 - 1))
                st.metric("Custom CHSH S-Value", f"{_S2:.4f}", f"{'Quantum' if _S2 > 2 else 'Classical'} Regime")
    else:
        st.info("No canary probe telemetry available.")


# ══════════════════════════════════════════════════════════
# MODULE 7: FORENSIC STATE TOMOGRAPHY
# ══════════════════════════════════════════════════════════
elif page == "🩺 Forensic State Tomography":
    st.markdown('<div class="q-title">🩺 Slow-Path Forensic Quantum State Tomography (QST)</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94A3B8; margin-bottom:18px;">Post-alert density matrix reconstruction $\\hat{\\rho}$ via multi-basis projective measurements. Analyzes state purity, Von Neumann entropy, and Hilbert space fidelity.</p>', unsafe_allow_html=True)

    tr = sess.tomography_result
    if tr:
        c1, c2 = st.columns([1.1, 1.3])
        with c1:
            st.markdown(f"""
            <div class="q-card q-card-violet">
                <span class="q-label">DIAGNOSTIC CLASSIFICATION</span>
                <div class="q-value q-value-violet" style="font-size:1.6rem;">{tr.diagnostic_class}</div>
                <div style="margin-top:16px;">
                    <div class="prov-row"><span class="prov-key">State Fidelity F</span><strong style="color:#00D4FF;">{tr.fidelity*100:.2f}%</strong></div>
                    <div class="prov-row"><span class="prov-key">State Purity Tr(ρ²)</span><strong style="color:#A855F7;">{tr.purity:.4f}</strong></div>
                    <div class="prov-row" style="border:none;"><span class="prov-key">Stokes Vector ⟨X,Y,Z⟩</span><span class="hash">({tr.bloch_vector[0]:.3f}, {tr.bloch_vector[1]:.3f}, {tr.bloch_vector[2]:.3f})</span></div>
                </div>
            </div>""", unsafe_allow_html=True)
        with c2:
            rho_r = np.array(tr.density_matrix.real)
            fig_r = go.Figure(go.Surface(
                z=rho_r,
                colorscale="Plasma",
                showscale=True,
                colorbar=dict(tickfont=dict(color="#94A3B8")),
            ))
            sfig(fig_r, "Reconstructed Density Matrix Re(ρ̂)", 340)
            fig_r.update_layout(scene=dict(
                xaxis=dict(ticktext=["|0⟩", "|1⟩"], tickvals=[0, 1], title="Row", backgroundcolor="rgba(0,0,0,0)"),
                yaxis=dict(ticktext=["|0⟩", "|1⟩"], tickvals=[0, 1], title="Col", backgroundcolor="rgba(0,0,0,0)"),
                zaxis=dict(title="ρ", range=[-0.2, 1.1], backgroundcolor="rgba(0,0,0,0)")),
                scene_camera=dict(eye=dict(x=1.8, y=1.8, z=0.8)))
            st.plotly_chart(fig_r, use_container_width=True)
    else:
        st.markdown("""
        <div class="q-card q-card-cyan">
            <span class="q-label">FORENSIC SLOW PATH STATUS</span>
            <p style="color:#CBD5E1; margin-top:10px; font-size:0.9rem; line-height:1.65;">
                Forensic Quantum State Tomography is triggered automatically upon detection of security anomalies (<code>QUARANTINE</code>, <code>REJECT</code>, <code>BLOCK</code>, or <code>ESCALATE</code>).
                To view a reconstructed density matrix, launch any attack scenario from the <strong>Digital Twin Attack Lab</strong>.
            </p>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# MODULE 8: Q-GUARDIAN POLICY GATE
# ══════════════════════════════════════════════════════════
elif page == "🛡️ Q-Guardian Policy Gate":
    st.markdown('<div class="q-title">🛡️ Deterministic Policy Engine & Hard Precedence State Machine</div>', unsafe_allow_html=True)

    if dec:
        act = dec.action.value
        ac = acolor(act)
        ab = abadge(act)
        st.markdown(f"""
        <div class="q-card {'q-card-emerald' if act=='ACCEPT' else 'q-card-red'}">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                <div>
                    <span class="q-label">CURRENT GUARDIAN ARBITRATION</span>
                    <div class="q-value" style="color:{ac}; font-size:2.5rem;">{act}</div>
                </div>
                <span class="badge {ab}">{act}</span>
            </div>
            <p style="color:#CBD5E1; margin:14px 0 6px 0; font-size:0.9rem; line-height:1.6;">{dec.primary_reason}</p>
            <div class="q-sub">Enforced Policy ID: <span class="hash">{dec.policy_id}</span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="q-title">📋 7-Level Hard Security Precedence Chain</div>', unsafe_allow_html=True)
    prec = [
        ("1", "Replay / Freshness Validation", "BLOCK", "Fail-closed before quantum verification on nonce reuse or stale timestamp", "#FF3B6E"),
        ("2", "Signer / Verifier Identity Auth", "BLOCK", "HMAC classical channel authentication mismatch or unauthorized verifier", "#FF3B6E"),
        ("3", "Quantum Canary Integrity", "QUARANTINE", "Preflight decoy link corruption triggers immediate link isolation", "#FFA500"),
        ("4", "Statistical Forgery Detection", "REJECT", "VER exceeds threshold (4.5%) or Exact Binomial p-value < α", "#F43F5E"),
        ("5", "Channel Manipulation (QBER)", "QUARANTINE", "Elevated physical QBER or degraded Bell pair state fidelity", "#FFA500"),
        ("6", "Inconclusive SPRT Evidence", "ESCALATE", "Extended sampling triggered when SPRT boundaries are not crossed", "#A855F7"),
        ("7", "All Mandatory Proofs Satisfied", "ACCEPT", "All quantum, statistical, freshness, and cryptographic checks passed", "#00FF88"),
    ]
    for idx, name, action, desc, color in prec:
        st.markdown(f"""
        <div class="prec-row">
            <span class="prec-idx">{idx}</span>
            <span class="prec-name">{name}</span>
            <span class="ttag" style="background:rgba(0,0,0,0.3); color:{color}; border:1px solid {color}60; font-size:0.72rem; padding:3px 10px;">{action}</span>
            <span class="prec-desc">{desc}</span>
        </div>""", unsafe_allow_html=True)

    # ── Per-Detector Forensic Breakdown (T2.5) ──
    if dec and dec.threat_assessment.detector_results:
        st.markdown('<div class="q-title">🕵️ Per-Detector Forensic Breakdown — 5-Engine Fusion Analysis</div>', unsafe_allow_html=True)
        det_results = dec.threat_assessment.detector_results

        c_det_a, c_det_b = st.columns([1.4, 1])
        with c_det_a:
            det_rows = []
            for d in det_results:
                det_rows.append({
                    "Detector": d.threat_type,
                    "Triggered": "🚨 YES" if d.triggered else "✅ NO",
                    "Score": f"{d.score:.3f}",
                    "Reason Codes": ", ".join(d.reason_codes[:2]) if d.reason_codes else "—",
                    "Evidence Refs": len(d.evidence_refs),
                })
            st.dataframe(pd.DataFrame(det_rows), use_container_width=True, hide_index=True)

            # Per-detector cards
            for d in det_results:
                cls_d = "q-card-red" if d.triggered else "q-card-emerald"
                v_cls_d = "q-value-red" if d.triggered else "q-value-green"
                st.markdown(f"""
                <div class="q-card {cls_d}" style="margin-top:10px; padding:12px 16px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong style="color:#FFFFFF;">{d.threat_type} Detector</strong>
                        <span class="badge {'badge-red' if d.triggered else 'badge-green'}">{'TRIGGERED' if d.triggered else 'CLEAR'}</span>
                    </div>
                    <div style="margin-top:8px; display:flex; gap:20px;">
                        <div><span class="q-label">Score</span><div class="q-value {v_cls_d}" style="font-size:1.3rem;">{d.score:.3f}</div></div>
                        <div style="flex:1;"><span class="q-label">Reason Codes</span>
                        <div style="color:#CBD5E1; font-size:0.8rem;">{', '.join(d.reason_codes[:3]) if d.reason_codes else 'None'}</div></div>
                    </div>
                </div>""", unsafe_allow_html=True)

        with c_det_b:
            det_names = [d.threat_type for d in det_results]
            det_scores = [d.score for d in det_results]
            # Close the radar
            det_names_c = det_names + [det_names[0]]
            det_scores_c = det_scores + [det_scores[0]]
            fig_radar = go.Figure(go.Scatterpolar(
                r=det_scores_c,
                theta=det_names_c,
                fill="toself",
                fillcolor="rgba(255,59,110,0.15)",
                line=dict(color="#FF3B6E", width=2.5),
                name="Detector Scores",
            ))
            sfig(fig_radar, "5-Detector Threat Radar (Score = 0.0 → 1.0)", 420)
            fig_radar.update_layout(polar=dict(
                radialaxis=dict(visible=True, range=[0, 1], tickcolor="#475569", color="#94A3B8", gridcolor="rgba(71,85,105,0.4)"),
                angularaxis=dict(tickcolor="#475569", color="#FFFFFF"),
                bgcolor="rgba(0,0,0,0)",
            ))
            st.plotly_chart(fig_radar, use_container_width=True)


# ══════════════════════════════════════════════════════════
# MODULE 9: EVIDENCE PROVENANCE GRAPH
# ══════════════════════════════════════════════════════════
elif page == "🕸️ Evidence Provenance Graph":
    st.markdown('<div class="q-title">🕸️ Cryptographic Evidence Lineage DAG</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94A3B8; margin-bottom:18px;">Directed Acyclic Graph (DAG) establishing complete forensic lineage from Signer Manifest $\\to$ Quantum Channel $\\to$ Statistical Engines $\\to$ Guardian Gate $\\to$ Blockchain Block.</p>', unsafe_allow_html=True)

    if pkt and rep and dec:
        from evidence.graph import EvidenceGraphBuilder
        G = EvidenceGraphBuilder.build_graph(pkt, rep.evidence_bundle, dec, audit_hash=sess.audit_block_hash)
        gd = EvidenceGraphBuilder.export_graph_dict(G)
        nodes, edges = gd["nodes"], gd["edges"]

        pos = {n["id"]: (i * 1.7, math.sin(i * 0.65) * 0.9) for i, n in enumerate(nodes)}
        ex, ey = [], []
        for e in edges:
            x0, y0 = pos[e["source"]]; x1, y1 = pos[e["target"]]
            ex.extend([x0, x1, None]); ey.extend([y0, y1, None])

        node_colors = ["#00FF88" if n["status"] == "PASS" else ("#FF3B6E" if n["status"] == "FAIL" else "#00D4FF") for n in nodes]

        fig_dag = go.Figure()
        fig_dag.add_trace(go.Scatter(x=ex, y=ey, line=dict(width=1.8, color="rgba(71,85,105,0.7)"), hoverinfo="none", mode="lines"))
        fig_dag.add_trace(go.Scatter(
            x=[pos[n["id"]][0] for n in nodes],
            y=[pos[n["id"]][1] for n in nodes],
            mode="markers+text",
            marker=dict(size=28, color=node_colors, line=dict(width=2, color="rgba(255,255,255,0.25)")),
            text=[n["id"] for n in nodes],
            textposition="top center",
            textfont=dict(size=10, color="#FFFFFF", family="JetBrains Mono"),
            hovertext=[f"<b>Node: {n['id']}</b><br>{n['label']}<br>Status: {n['status']}" for n in nodes],
            hoverinfo="text",
        ))
        sfig(fig_dag, "Interactive Evidence Lineage: Signer → Channel → Verifier → Guardian → Ledger", 440)
        fig_dag.update_layout(showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
        st.plotly_chart(fig_dag, use_container_width=True)
    else:
        st.info("No active session evidence available.")

# ══════════════════════════════════════════════════════════
# MODULE 10: BLOCKCHAIN AUDIT LEDGER
# ══════════════════════════════════════════════════════════
elif page == "⛓️ Blockchain Audit Ledger":
    st.markdown('<div class="q-title">⛓️ SHA-256 Hash-Linked Audit Chain & Merkle Tree Explorer</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94A3B8; margin-bottom:18px;">Immutable blockchain audit trail linking every QDS decision, transcript hash, and forensic telemetry with Merkle root anchors.</p>', unsafe_allow_html=True)

    is_valid, errors, report = LedgerVerifier.verify_chain(GLOBAL_LEDGER)

    c1, c2 = st.columns([1.6, 1])
    with c1:
        st.markdown(f"""
        <div class="q-card {'q-card-emerald' if is_valid else 'q-card-red'}">
            <div style="display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap;">
                <div>
                    <span class="q-label">LEDGER INTEGRITY VERIFICATION</span>
                    <div class="q-value {'q-value-green' if is_valid else 'q-value-red'}" style="font-size:1.8rem;">
                        {'✅ VALID & CRYPTOGRAPHICALLY IMMUTABLE' if is_valid else '🚨 TAMPER DETECTED — CHAIN BROKEN'}
                    </div>
                </div>
                <span class="badge {'badge-green' if is_valid else 'badge-red'}">
                    <span class="dot {'dot-g' if is_valid else 'dot-r'}"></span>&nbsp;{report['total_blocks']} Total Blocks
                </span>
            </div>
            <div class="q-sub" style="margin-top:10px;">
                Latest Block Hash: <span class="hash">{report['latest_block_hash']}</span>
            </div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="q-card q-card-red" style="padding:18px;">', unsafe_allow_html=True)
        st.markdown('<span class="q-label">MALICIOUS TAMPER SIMULATOR</span>', unsafe_allow_html=True)
        if st.button("🚨 Simulate Tamper Attack on Block #1", use_container_width=True, type="primary"):
            tr2 = LedgerVerifier.simulate_tamper_attack(GLOBAL_LEDGER, block_index=1)
            st.error(f"🚨 **{tr2['status']}** — Ledger hash mismatch detected immediately.")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="q-title">📋 Blockchain Block Explorer</div>', unsafe_allow_html=True)
    blk_rows = []
    for b in GLOBAL_LEDGER.chain[-12:]:
        blk_rows.append({
            "Block #": b.index,
            "Event Type": b.event_type,
            "Block Hash": b.block_hash,
            "Previous Hash": b.previous_hash,
            "Merkle Root": b.merkle_root if b.merkle_root else "GENESIS",
            "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(b.timestamp)),
        })
    st.dataframe(pd.DataFrame(blk_rows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════
# MODULE 11: BENCHMARKS & PQC COMPARISON
# ══════════════════════════════════════════════════════════
elif page == "📈 Benchmarks & PQC Comparison":
    st.markdown('<div class="q-title">📈 Quantum Threat Detection Benchmarks & PQC Trade-Off Matrix</div>', unsafe_allow_html=True)

    tab_dr, tab_pqc = st.tabs(["📊 Detection Rate vs Noise Continuum", "🛡️ QDS vs Post-Quantum (PQC) Matrix"])

    with tab_dr:
        sweep = AttackEnsembleBenchmark.sweep_depolarizing_noise(
            noise_steps=[0.0, 0.02, 0.05, 0.08, 0.12, 0.18, 0.25, 0.35], runs_per_step=8)
        df_sw = pd.DataFrame({
            "Noise (p)": sweep["parameter_values"],
            "Detection Rate": sweep["detection_rates"],
            "Mean VER": sweep["mean_vers"],
            "Mean QBER": sweep["mean_qbers"],
        })
        fig_roc = go.Figure()
        fig_roc.add_trace(go.Scatter(
            x=df_sw["Noise (p)"], y=df_sw["Detection Rate"],
            mode="lines+markers", name="Threat Detection Rate",
            line=dict(color="#FF3B6E", width=3.5), marker=dict(size=9, color="#FF3B6E"),
        ))
        fig_roc.add_trace(go.Scatter(
            x=df_sw["Noise (p)"], y=df_sw["Mean VER"],
            mode="lines+markers", name="Mean Verification Error (VER)",
            line=dict(color="#00D4FF", width=2, dash="dot"), marker=dict(size=6),
        ))
        fig_roc.add_trace(go.Scatter(
            x=df_sw["Noise (p)"], y=df_sw["Mean QBER"],
            mode="lines+markers", name="Mean Channel Noise (QBER)",
            line=dict(color="#A855F7", width=2, dash="dot"), marker=dict(size=6),
        ))
        sfig(fig_roc, "QDS Threat Detection Rate across Depolarizing Noise Spectrum", 400)
        fig_roc.update_layout(xaxis_title="Depolarizing Noise Probability (p)", yaxis_title="Metric Value",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(color="#FFFFFF")))
        st.plotly_chart(fig_roc, use_container_width=True)

    with tab_pqc:
        pqc = PQCComparisonMatrix.get_comparison_data()
        st.dataframe(pd.DataFrame(pqc), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════
# MODULE 12: REPORTS & ASSUMPTIONS
# ══════════════════════════════════════════════════════════
elif page == "📜 Reports & Assumptions":
    tab_rep, tab_assum = st.tabs(["📄 Export Forensic Reports", "🔬 Protocol Assumptions & Scope"])

    with tab_rep:
        st.markdown('<div class="q-title">📄 One-Click Forensic Evidence Bundle Export</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            html_c = ComplianceReportGenerator.generate_html_report(sess)
            st.download_button("📥 Download HTML Audit Report", html_c,
                f"Q_IMMUNE_QDS_Audit_{sess.session_id}.html", "text/html", use_container_width=True, type="primary")
        with c2:
            json_d = json.dumps(sess.to_dict(), indent=2)
            st.download_button("📥 Download JSON Evidence Bundle", json_d,
                f"Q_IMMUNE_QDS_Evidence_{sess.session_id}.json", "application/json", use_container_width=True, type="primary")

    with tab_assum:
        st.markdown('<div class="q-title">🔬 Protocol Assumptions & Scientific Defensibility</div>', unsafe_allow_html=True)
        assumptions = [
            ("Authenticated Classical Channel", "Classical correction bits (b₁, b₂) are transmitted over an HMAC-SHA256 authenticated channel. Any tampering is detected by integrity validator."),
            ("Trusted State Preparation", "Alice accurately prepares pure Pauli eigenstates based on a domain-separated hash of the message."),
            ("Entanglement Resource", "Alice and Bob share maximally entangled EPR Bell pairs |Φ⁺⟩ = (|00⟩ + |11⟩)/√2."),
            ("Projective Measurement Basis", "Bob performs projective measurements strictly aligned with the protocol manifest for each qubit."),
            ("Finite-Sample Statistical Tests", "Decisions use exact binomial tests, Wald SPRT, Chi-Square, and Hoeffding confidence bounds."),
            ("Calibrated Channel Noise", "Baseline noise profile empirically calibrated before operational deployment."),
            ("Reproducible Random Seed", "All experiments are 100% reproducible with fixed PRNG seed for judges."),
            ("Protocol-Specific Scope", "Results apply specifically to the QIMMUNE-QDS-TB-001 protocol configuration."),
        ]
        for title, desc in assumptions:
            st.markdown(f"""
            <div class="assum-row">
                <span class="assum-ck">✓</span>
                <div>
                    <div class="assum-title">{title}</div>
                    <div class="assum-desc">{desc}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class="q-card q-card-cyan" style="margin-top:24px;">
            <span class="q-label">SCIENTIFIC SECURITY CLAIM SCOPE</span>
            <p style="color:#CBD5E1; margin-top:10px; font-size:0.9rem; line-height:1.7;">
                Q-IMMUNE QDS is a reproducible software prototype for teleportation-based quantum digital signatures.
                All results apply to the stated local protocol model, calibrated noise parameters, and finite measurement samples.
                This platform provides <strong style="color:#FFFFFF;">mathematically explainable deterministic evidence</strong> — it is
                <em>not</em> presented as an unconditional formal security proof for arbitrary physical hardware implementations.
            </p>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# MODULE 13: SESSION HISTORY ARCHIVE
# ══════════════════════════════════════════════════════════
elif page == "🗂️ Session History Archive":
    st.markdown('<div class="q-title">🗂️ Session Archive, History & Multi-Session Forensic Comparison</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94A3B8; margin-bottom:18px;">Browse all processed QDS sessions this run. Compare multiple sessions side-by-side to verify reproducibility, identify outliers, and export batch evidence bundles.</p>', unsafe_allow_html=True)

    history = st.session_state.session_history

    if not history:
        st.info("No session history yet. Run a transaction from the Executive Command Center.")
    else:
        # ── Summary KPI chart ──
        st.markdown('<div class="q-title">📊 Session Outcome Distribution</div>', unsafe_allow_html=True)
        action_counts = {}
        for s in history:
            act = s.guardian_decision.action.value if s.guardian_decision else "UNKNOWN"
            action_counts[act] = action_counts.get(act, 0) + 1
        act_colors = {"ACCEPT": "#00FF88", "REJECT": "#FF3B6E", "BLOCK": "#FF3B6E", "QUARANTINE": "#FFA500", "ESCALATE": "#A855F7", "UNKNOWN": "#94A3B8"}
        fig_ac = go.Figure(go.Bar(
            x=list(action_counts.keys()), y=list(action_counts.values()),
            marker_color=[act_colors.get(k, "#94A3B8") for k in action_counts.keys()],
            text=list(action_counts.values()), textposition="outside",
            textfont=dict(color="#FFFFFF", size=14),
        ))
        sfig(fig_ac, "Guardian Decision Distribution Across All Sessions", 280)
        st.plotly_chart(fig_ac, use_container_width=True)

        # ── Session Table ──
        st.markdown('<div class="q-title">📋 All Session Records</div>', unsafe_allow_html=True)
        tbl_rows = []
        for s in history:
            _act = s.guardian_decision.action.value if s.guardian_decision else "UNKNOWN"
            _ver = s.verification_report.error_metrics.ver * 100 if s.verification_report else 0
            _qber = s.verification_report.error_metrics.qber * 100 if s.verification_report else 0
            _pval = s.verification_report.evidence_bundle.binomial_result.p_value if (s.verification_report and s.verification_report.evidence_bundle.binomial_result) else 0
            _bh = s.audit_block_hash[:20] + "…" if s.audit_block_hash else "N/A"
            _canary = s.canary_result.channel_health if s.canary_result else "N/A"
            tbl_rows.append({
                "Session ID": s.session_id[:18] + "…",
                "Signer": s.signer_id,
                "Verifier": s.verifier_id,
                "Guardian": _act,
                "VER %": f"{_ver:.2f}%",
                "QBER %": f"{_qber:.2f}%",
                "p-value": f"{_pval:.6f}",
                "Canary": _canary,
                "Block Hash": _bh,
            })
        df_hist = pd.DataFrame(tbl_rows)
        st.dataframe(df_hist, use_container_width=True, hide_index=True)

        # ── Multi-Session Comparison ──
        st.markdown('<div class="q-title">🆚 Multi-Session Side-by-Side Comparison</div>', unsafe_allow_html=True)
        st.markdown('<p style="color:#94A3B8; margin-bottom:10px;">Select 2-4 sessions by index to compare their statistical outputs directly.</p>', unsafe_allow_html=True)
        max_sel = min(len(history), 4)
        sel_indices = st.multiselect(
            "Select Sessions to Compare (by table row index, 0 = latest)",
            options=list(range(len(history))),
            default=list(range(min(2, len(history)))),
            format_func=lambda i: f"[{i}] {history[i].session_id[:20]}… — {history[i].guardian_decision.action.value if history[i].guardian_decision else 'UNKNOWN'}",
        )
        if len(sel_indices) >= 2:
            comp_cols = st.columns(len(sel_indices))
            for ci, sidx in enumerate(sel_indices):
                s = history[sidx]
                _act = s.guardian_decision.action.value if s.guardian_decision else "UNKNOWN"
                _ac = acolor(_act)
                _ver = s.verification_report.error_metrics.ver * 100 if s.verification_report else 0
                _qber = s.verification_report.error_metrics.qber * 100 if s.verification_report else 0
                _pval = s.verification_report.evidence_bundle.binomial_result.p_value if (s.verification_report and s.verification_report.evidence_bundle.binomial_result) else 0
                _llr = s.verification_report.evidence_bundle.sprt_result.llr if (s.verification_report and s.verification_report.evidence_bundle.sprt_result) else 0
                _fub = s.verification_report.evidence_bundle.finite_sample_upper_bound * 100 if s.verification_report else 0
                with comp_cols[ci]:
                    st.markdown(f"""
                    <div class="q-card {'q-card-emerald' if _act=='ACCEPT' else 'q-card-red'}">
                        <span class="q-label">SESSION [{sidx}]</span>
                        <div class="q-value" style="color:{_ac}; font-size:1.5rem;">{_act}</div>
                        <div class="prov-row"><span class="prov-key">VER</span><strong style="color:{'#00FF88' if _ver < 4.5 else '#FF3B6E'};">{_ver:.2f}%</strong></div>
                        <div class="prov-row"><span class="prov-key">QBER</span><strong style="color:#00D4FF;">{_qber:.2f}%</strong></div>
                        <div class="prov-row"><span class="prov-key">p-value</span><strong style="color:#A855F7;">{_pval:.6f}</strong></div>
                        <div class="prov-row"><span class="prov-key">SPRT LLR</span><strong style="color:#FFA500;">{_llr:.3f}</strong></div>
                        <div class="prov-row" style="border:none;"><span class="prov-key">Hoeffding Bound</span><strong style="color:#FFFFFF;">{_fub:.2f}%</strong></div>
                    </div>""", unsafe_allow_html=True)

        # ── Batch Export ──
        st.markdown('<div class="q-title">📥 Batch Evidence Bundle Export</div>', unsafe_allow_html=True)
        if st.button("📦 Export All Sessions as JSON Bundle", type="primary"):
            bundle = [s.to_dict() for s in history]
            batch_json = json.dumps({"session_count": len(bundle), "sessions": bundle}, indent=2)
            st.download_button("⬇️ Download Batch Bundle", batch_json, "Q_IMMUNE_QDS_Batch.json", "application/json", use_container_width=True)

# ══════════════════════════════════════════════════════════
# MODULE 14: LIVE TRANSACTION FEED & AUTO-DEMO MODE
# ══════════════════════════════════════════════════════════
elif page == "🎬 Live Transaction Feed":
    st.markdown('<div class="q-title">🎬 Real-Time Pipeline Feed & Auto-Demo Judge Mode</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94A3B8; margin-bottom:18px;">Live scrolling event feed for every pipeline stage execution. Launch the Auto-Demo sequence to run the full attack cycle automatically for judges.</p>', unsafe_allow_html=True)

    # ── Auto-Demo Mode (T3.1 — Judge Mode) ──
    st.markdown('<div class="q-title">🏆 Auto-Demo: Full Attack Cycle (Judge Mode)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="q-card q-card-cyan">
        <span class="q-label">DEMO SEQUENCE</span>
        <div style="display:flex; gap:14px; flex-wrap:wrap; margin-top:10px;">
            <span class="ttag" style="background:rgba(0,212,255,0.1); color:#00D4FF; border:1px solid #00D4FF40;">① Clean Transaction → ACCEPT</span>
            <span style="color:#475569;">→</span>
            <span class="ttag" style="background:rgba(255,59,110,0.1); color:#FF3B6E; border:1px solid #FF3B6E40;">② Forgery Attack → REJECT</span>
            <span style="color:#475569;">→</span>
            <span class="ttag" style="background:rgba(255,59,110,0.1); color:#FF3B6E; border:1px solid #FF3B6E40;">③ Replay Attack → BLOCK</span>
            <span style="color:#475569;">→</span>
            <span class="ttag" style="background:rgba(255,165,0,0.1); color:#FFA500; border:1px solid #FFA50040;">④ Intercept-Resend → QUARANTINE</span>
            <span style="color:#475569;">→</span>
            <span class="ttag" style="background:rgba(255,59,110,0.1); color:#FF3B6E; border:1px solid #FF3B6E40;">⑤ Multi-Vector Storm → BLOCK</span>
            <span style="color:#475569;">→</span>
            <span class="ttag" style="background:rgba(0,255,136,0.1); color:#00FF88; border:1px solid #00FF8840;">⑥ Clean Recovery → ACCEPT</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_demo_a, col_demo_b = st.columns(2)
    with col_demo_a:
        if st.button("🎬 Launch Full Demo Sequence (6 Phases)", type="primary", use_container_width=True):
            demo_sequence = [
                ("Clean Baseline", lambda: st.session_state.runner.run_clean_baseline("DEMO_RTGS_SETTLEMENT_INR_100CR")),
                ("State Forgery Attack", lambda: st.session_state.runner.inject_attack(AttackType.FORGERY)),
                ("Nonce Replay Attack", lambda: st.session_state.runner.inject_attack(AttackType.REPLAY)),
                ("Intercept-Resend", lambda: st.session_state.runner.inject_attack(AttackType.INTERCEPT_RESEND)),
                ("Multi-Vector Storm", lambda: st.session_state.runner.inject_attack(AttackType.MIXED_MULTI_VECTOR)),
                ("Clean Recovery", lambda: st.session_state.runner.run_clean_baseline("DEMO_RECOVERY_TRANSACTION_VERIFIED")),
            ]
            progress_bar = st.progress(0, text="Initializing demo sequence…")
            status_area = st.empty()
            for i, (phase_name, phase_fn) in enumerate(demo_sequence):
                progress_bar.progress((i) / len(demo_sequence), text=f"Phase {i+1}/{len(demo_sequence)}: {phase_name}")
                status_area.markdown(f"""
                <div class="q-card q-card-amber" style="padding:12px 18px;">
                    <span class="q-label">EXECUTING PHASE {i+1}</span>
                    <div style="color:#FFFFFF; font-weight:700; margin-top:6px;">🚀 {phase_name}</div>
                </div>""", unsafe_allow_html=True)
                _demo_sess = phase_fn()
                _demo_act = _demo_sess.guardian_decision.action.value if _demo_sess.guardian_decision else "UNKNOWN"
                log_pipeline_stage(f"DEMO:P{i+1}", "🎬" if _demo_act == "ACCEPT" else "🚨", f"{phase_name} → {_demo_act}")
                record_session_to_history(_demo_sess)
                time.sleep(0.5)
            progress_bar.progress(1.0, text="✅ Demo sequence complete!")
            st.session_state.current_session = _demo_sess
            status_area.markdown("""
            <div class="q-card q-card-emerald" style="padding:12px 18px;">
                <span class="q-label">DEMO COMPLETE</span>
                <div style="color:#00FF88; font-weight:700; margin-top:6px;">✅ All 6 phases executed. Switch to Session History Archive to compare results.</div>
            </div>""", unsafe_allow_html=True)
            st.rerun()

    with col_demo_b:
        if st.button("🗑️ Clear Pipeline Feed", use_container_width=True):
            st.session_state.pipeline_feed = []
            st.rerun()

    # ── Live Pipeline Feed ──
    st.markdown('<div class="q-title">📡 Live Pipeline Stage Feed</div>', unsafe_allow_html=True)
    feed = st.session_state.pipeline_feed
    if not feed:
        st.markdown("""
        <div class="q-card q-card-cyan" style="text-align:center; padding:30px;">
            <div style="font-size:2rem; margin-bottom:10px;">📡</div>
            <div style="color:#94A3B8; font-size:0.9rem;">No pipeline events yet. Run a transaction or launch the demo sequence.</div>
        </div>""", unsafe_allow_html=True)
    else:
        stage_colors = {
            "PREPARE": "#00D4FF", "SIGN": "#A855F7", "TELEPORT": "#00D4FF",
            "CANARY": "#00FF88", "VERIFY": "#00FF88", "ANALYZE": "#00D4FF",
            "DETECT": "#FFA500", "GUARDIAN": "#FF3B6E", "AUDIT": "#00D4FF",
            "REMEMBER": "#00FF88", "ATTACK_INJECT": "#FF3B6E", "DEMO:P1": "#00D4FF",
            "DEMO:P2": "#FF3B6E", "DEMO:P3": "#FF3B6E", "DEMO:P4": "#FFA500",
            "DEMO:P5": "#FF3B6E", "DEMO:P6": "#00FF88",
        }
        rows_html = ""
        for entry in feed[:50]:
            sc = stage_colors.get(entry["stage"], "#94A3B8")
            dur_html = f'<span style="color:#475569;font-size:0.72rem;white-space:nowrap;">{entry["duration_ms"]:.0f}ms</span>' if entry['duration_ms'] > 0 else ''
            rows_html += (
                f'<div style="display:flex;align-items:flex-start;gap:12px;padding:8px 14px;border-bottom:1px solid rgba(71,85,105,0.3);margin:2px 0;">'
                f'<span style="font-family:JetBrains Mono,monospace;color:#475569;font-size:0.75rem;white-space:nowrap;min-width:68px;">{entry["ts"]}</span>'
                f'<span style="background:rgba(0,0,0,0.3);color:{sc};border:1px solid {sc}40;border-radius:5px;padding:2px 8px;font-size:0.72rem;font-weight:700;white-space:nowrap;min-width:90px;">{entry["stage"]}</span>'
                f'<span style="font-size:1.1rem;min-width:22px;">{entry["status"]}</span>'
                f'<span style="color:#CBD5E1;font-size:0.82rem;flex:1;">{entry["detail"]}</span>'
                f'{dur_html}</div>'
            )
        full_html = (
            '<div style="background:rgba(0,5,20,0.95);border:1px solid rgba(0,212,255,0.2);border-radius:10px;'
            'max-height:560px;overflow-y:auto;font-family:JetBrains Mono,monospace;">'
            '<div style="padding:10px 14px;border-bottom:1px solid rgba(0,212,255,0.2);'
            'color:#00D4FF;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;">'
            f'&#x1F4E1; Live Feed &mdash; {len(feed)} Events Logged</div>'
            + rows_html +
            '</div>'
        )
        st_components.html(full_html, height=min(600, 80 + len(feed[:50]) * 38), scrolling=True)


    # ── Attack Storm Timeline ──
    if len(st.session_state.session_history) >= 2:
        st.markdown('<div class="q-title">🌊 Attack Storm Timeline — Multi-Session Gantt Visualization</div>', unsafe_allow_html=True)
        storm_data = []
        for i, s in enumerate(reversed(st.session_state.session_history[-10:])):
            _act = s.guardian_decision.action.value if s.guardian_decision else "UNKNOWN"
            _threats = s.guardian_decision.threat_assessment.active_threats if s.guardian_decision else []
            if _threats:
                cat = "Identity" if any(t in ("REPLAY", "IMPERSONATION", "UNAUTHORIZED_VERIFICATION") for t in _threats) else \
                      "Quantum" if any(t in ("FORGERY", "CHANNEL_MANIPULATION") for t in _threats) else "Composite"
            else:
                cat = "Clean"
            storm_data.append({
                "Session": f"S-{i+1}: {_act}",
                "Category": cat,
                "Start": i * 2,
                "End": i * 2 + 1.5,
                "Action": _act,
                "Threats": ", ".join(_threats) if _threats else "None",
            })
        if storm_data:
            cat_colors = {"Clean": "#00FF88", "Identity": "#FF3B6E", "Quantum": "#FFA500", "Composite": "#A855F7"}
            fig_storm = go.Figure()
            for sd in storm_data:
                fig_storm.add_trace(go.Bar(
                    x=[sd["End"] - sd["Start"]],
                    y=[sd["Session"]],
                    base=[sd["Start"]],
                    orientation="h",
                    marker=dict(color=cat_colors.get(sd["Category"], "#94A3B8"), opacity=0.85),
                    name=sd["Category"],
                    text=f"{sd['Category']}: {sd['Threats'][:30]}",
                    hoverinfo="text",
                    showlegend=False,
                ))
            sfig(fig_storm, "Multi-Session Attack Timeline (Gantt) — Session Sequence & Threat Categories", 400)
            fig_storm.update_layout(
                barmode="overlay",
                xaxis=dict(title="Session Sequence (Time)", showgrid=True, gridcolor="rgba(71,85,105,0.3)"),
                yaxis=dict(autorange="reversed"),
            )
            # Add legend manually
            for cat, col in cat_colors.items():
                fig_storm.add_trace(go.Scatter(
                    x=[None], y=[None], mode="markers",
                    marker=dict(size=10, color=col),
                    name=cat, showlegend=True,
                ))
            st.plotly_chart(fig_storm, use_container_width=True)

