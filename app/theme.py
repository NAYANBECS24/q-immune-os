"""Q-IMMUNE QDS — Premium High-Contrast Cyber Theme & Design System.

Design: Vivid neon colors on a rich deep-navy base with generous spacing,
clear input/output separation, and high readability for all components.
"""

CYBER_QUANTUM_CSS = """
<style>
    /* ─── FONTS ─── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    code, pre, .stCode, [data-testid="stCode"] {
        font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
    }

    /* ─── GLOBAL BACKGROUND ─── */
    .stApp {
        background: #05091A !important;
        color: #FFFFFF !important;
    }

    /* Container padding */
    .main .block-container {
        background: transparent !important;
        padding-top: 1.2rem !important;
        padding-bottom: 3rem !important;
        max-width: 96% !important;
    }

    /* ─── ALL STREAMLIT TEXT OVERRIDE ─── */
    .stApp,
    .stApp .stMarkdown,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stText"] {
        color: #E2E8F0 !important;
    }

    /* ─── SIDEBAR ─── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A0F2E 0%, #0D1240 100%) !important;
        border-right: 2px solid #00D4FF !important;
        padding-top: 1rem !important;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown {
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stRadio > label {
        color: #00D4FF !important;
        font-weight: 800 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
    }

    section[data-testid="stSidebar"] .stRadio label span {
        color: #CBD5E1 !important;
        font-size: 0.85rem !important;
    }

    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #00D4FF !important;
        font-weight: 700 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
    }

    section[data-testid="stSidebar"] .stCaptionContainer p,
    section[data-testid="stSidebar"] small {
        color: #94A3B8 !important;
    }

    section[data-testid="stSidebar"] hr {
        border-color: rgba(0, 212, 255, 0.2) !important;
    }

    /* ─── MAIN HEADINGS ─── */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, h1, h2, h3 {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    /* ─── CODE BLOCKS & CODE ELEMENTS ─── */
    [data-testid="stCodeBlock"],
    [data-testid="stCode"],
    .stCode,
    pre,
    div[data-testid="stCodeBlock"] > div {
        background: #081122 !important;
        border: 1px solid rgba(0, 212, 255, 0.35) !important;
        border-radius: 10px !important;
        padding: 8px !important;
    }

    [data-testid="stCodeBlock"] code,
    [data-testid="stCode"] code,
    .stCode code,
    pre code,
    section[data-testid="stSidebar"] code {
        background: transparent !important;
        color: #00D4FF !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
    }

    /* ─── UNIVERSAL BUTTON & DOWNLOAD BUTTON OVERRIDE ─── */
    button,
    button:not([disabled]),
    a[role="button"],
    .stButton > button,
    .stDownloadButton > button,
    .stDownloadButton > a,
    .stDownloadButton button,
    .stDownloadButton a,
    div[data-testid="stDownloadButton"] > button,
    div[data-testid="stDownloadButton"] > a,
    div[data-testid="stDownloadButton"] button,
    div[data-testid="stDownloadButton"] a,
    [data-testid*="Button"],
    [data-testid*="button"],
    button[kind="secondary"],
    button[kind="primary"] {
        background: linear-gradient(135deg, #0F1F38, #0A1628) !important;
        background-color: #0A1628 !important;
        color: #00D4FF !important;
        border: 1.5px solid rgba(0, 212, 255, 0.5) !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        font-size: 0.88rem !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.25s ease !important;
        letter-spacing: 0.3px !important;
        text-decoration: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
    }

    /* Force all text inside buttons to bright cyan */
    button *,
    button span,
    button p,
    button div,
    a[role="button"] *,
    a[role="button"] span,
    a[role="button"] p,
    .stButton > button *,
    .stDownloadButton *,
    .stDownloadButton * span,
    .stDownloadButton * p,
    div[data-testid="stDownloadButton"] *,
    div[data-testid="stDownloadButton"] span,
    div[data-testid="stDownloadButton"] p,
    [data-testid*="Button"] *,
    [data-testid*="Button"] span,
    [data-testid*="Button"] p {
        color: #00D4FF !important;
        font-weight: 800 !important;
        background: transparent !important;
        text-decoration: none !important;
    }

    button:hover,
    a[role="button"]:hover,
    .stButton > button:hover,
    .stDownloadButton > button:hover,
    .stDownloadButton > a:hover,
    .stDownloadButton button:hover,
    .stDownloadButton a:hover,
    div[data-testid="stDownloadButton"] > button:hover,
    div[data-testid="stDownloadButton"] > a:hover,
    div[data-testid="stDownloadButton"] button:hover,
    div[data-testid="stDownloadButton"] a:hover,
    [data-testid*="Button"]:hover,
    button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #0E7490, #0369A1) !important;
        background-color: #0E7490 !important;
        border-color: #00D4FF !important;
        color: #FFFFFF !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 24px rgba(0, 212, 255, 0.4) !important;
    }

    button:hover *,
    a[role="button"]:hover *,
    .stButton > button:hover *,
    .stDownloadButton *:hover,
    div[data-testid="stDownloadButton"] *:hover,
    [data-testid*="Button"]:hover * {
        color: #FFFFFF !important;
    }

    /* Primary button variant (Form Submit etc.) */
    .stButton > button[kind="primary"],
    .stDownloadButton > button[kind="primary"],
    [data-testid*="stBaseButton-primary"],
    button[kind="primary"] {
        background: linear-gradient(135deg, #0EA5E9, #0284C7) !important;
        background-color: #0EA5E9 !important;
        border-color: #38BDF8 !important;
        color: #FFFFFF !important;
    }

    .stButton > button[kind="primary"] *,
    .stDownloadButton > button[kind="primary"] *,
    [data-testid*="stBaseButton-primary"] *,
    button[kind="primary"] * {
        color: #FFFFFF !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stDownloadButton > button[kind="primary"]:hover,
    [data-testid*="stBaseButton-primary"]:hover,
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #38BDF8, #0EA5E9) !important;
        background-color: #38BDF8 !important;
        box-shadow: 0 6px 30px rgba(14, 165, 233, 0.5) !important;
    }

    /* ─── INPUTS & TEXT AREAS ─── */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: #0B162C !important;
        color: #FFFFFF !important;
        border: 1.5px solid rgba(0, 212, 255, 0.4) !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        font-size: 0.9rem !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #00D4FF !important;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.25) !important;
    }

    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: #64748B !important;
    }

    .stTextInput > label, .stTextArea > label, .stSlider > label, .stSelectbox > label {
        color: #CBD5E1 !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        margin-bottom: 6px !important;
    }

    /* Sliders */
    .stSlider [data-testid="stTickBarMin"],
    .stSlider [data-testid="stTickBarMax"] {
        color: #94A3B8 !important;
    }

    /* ─── DATAFRAMES / TABLES ─── */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1.5px solid rgba(0, 212, 255, 0.25) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
    }

    /* ─── FORMS ─── */
    [data-testid="stForm"] {
        background: linear-gradient(145deg, #0A162C, #060E1E) !important;
        border: 1.5px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 16px !important;
        padding: 22px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35) !important;
    }

    /* ─── TABS ─── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        border-bottom: 2px solid rgba(0, 212, 255, 0.2) !important;
        padding-bottom: 4px !important;
    }

    .stTabs [data-baseweb="tab"] {
        color: #94A3B8 !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 10px 18px !important;
        background: rgba(15, 23, 42, 0.4) !important;
        border: 1px solid transparent !important;
    }

    .stTabs [aria-selected="true"] {
        color: #00D4FF !important;
        background: rgba(0, 212, 255, 0.1) !important;
        border: 1px solid rgba(0, 212, 255, 0.4) !important;
        border-bottom: 2px solid #00D4FF !important;
    }

    /* ─── EXPANDERS ─── */
    .stExpander {
        background: #0A1528 !important;
        border: 1px solid rgba(0, 212, 255, 0.25) !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
    }

    /* ─── ALERTS / CALLOUTS ─── */
    .stAlert {
        background: rgba(14, 165, 233, 0.12) !important;
        border: 1.5px solid rgba(14, 165, 233, 0.45) !important;
        border-radius: 12px !important;
        color: #E2E8F0 !important;
    }

    /* ─── SCROLLBAR ─── */
    ::-webkit-scrollbar { width: 7px; height: 7px; }
    ::-webkit-scrollbar-track { background: #05091A; }
    ::-webkit-scrollbar-thumb { background: #1E3A5F; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #00D4FF; }

    /* ══════════════════════════════════════════
       CUSTOM CYBER-QUANTUM COMPONENTS
    ══════════════════════════════════════════ */

    /* ─── HEADER ─── */
    .q-header {
        background: linear-gradient(135deg, #0A1628 0%, #0D1F3C 50%, #0A1628 100%);
        border: 1.5px solid rgba(0, 212, 255, 0.35);
        border-radius: 20px;
        padding: 26px 32px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.45);
    }

    .q-header::before {
        content: "";
        position: absolute;
        top: -60%; right: -10%;
        width: 550px; height: 550px;
        background: radial-gradient(circle, rgba(0, 212, 255, 0.08) 0%, transparent 70%);
        pointer-events: none;
    }

    .q-header h1 {
        margin: 0 !important;
        font-size: 1.85rem !important;
        font-weight: 900 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.5px;
    }

    .q-header h1 .accent {
        background: linear-gradient(90deg, #00D4FF, #38BDF8, #818CF8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .q-header .subtitle {
        margin: 8px 0 0 0 !important;
        color: #CBD5E1 !important;
        font-size: 0.9rem !important;
    }

    /* ─── METRIC CARD ─── */
    .q-card {
        background: linear-gradient(145deg, #0D1B2E, #0A1525);
        border: 1.5px solid rgba(0, 212, 255, 0.2);
        border-radius: 16px;
        padding: 22px 24px;
        margin-bottom: 18px;
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
        position: relative;
        overflow: hidden;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.35);
    }

    .q-card:hover {
        border-color: rgba(0, 212, 255, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 10px 36px rgba(0, 212, 255, 0.15);
    }

    /* Accent left borders */
    .q-card-cyan    { border-left: 5px solid #00D4FF !important; }
    .q-card-emerald { border-left: 5px solid #00FF88 !important; }
    .q-card-red     { border-left: 5px solid #FF3B6E !important; }
    .q-card-amber   { border-left: 5px solid #FFA500 !important; }
    .q-card-violet  { border-left: 5px solid #A855F7 !important; }

    /* ─── METRIC LABEL ─── */
    .q-label {
        display: block;
        font-size: 0.72rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2.5px;
        color: #94A3B8;
        margin-bottom: 8px;
    }

    /* ─── METRIC VALUE ─── */
    .q-value {
        font-size: clamp(1.4rem, 2.2vw, 2.4rem);
        font-weight: 900;
        letter-spacing: -0.5px;
        line-height: 1.15;
        color: #00D4FF;
        word-break: keep-all;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .q-value-green  { color: #00FF88 !important; }
    .q-value-red    { color: #FF3B6E !important; }
    .q-value-amber  { color: #FFA500 !important; }
    .q-value-violet { color: #C084FC !important; }
    .q-value-white  { color: #FFFFFF !important; }

    .q-sub {
        font-size: 0.8rem;
        color: #94A3B8;
        margin-top: 8px;
    }

    /* ─── LIVE BADGES ─── */
    @keyframes pulse-c { 0%,100% { box-shadow:0 0 0 0 rgba(0,212,255,0.5); } 50% { box-shadow:0 0 14px 5px rgba(0,212,255,0.15); } }
    @keyframes pulse-g { 0%,100% { box-shadow:0 0 0 0 rgba(0,255,136,0.5); } 50% { box-shadow:0 0 14px 5px rgba(0,255,136,0.15); } }
    @keyframes pulse-r { 0%,100% { box-shadow:0 0 0 0 rgba(255,59,110,0.5); } 50% { box-shadow:0 0 14px 5px rgba(255,59,110,0.15); } }
    @keyframes pulse-a { 0%,100% { box-shadow:0 0 0 0 rgba(255,165,0,0.5); } 50% { box-shadow:0 0 14px 5px rgba(255,165,0,0.15); } }

    .badge {
        display: inline-flex; align-items: center; gap: 7px;
        padding: 6px 15px; border-radius: 24px;
        font-weight: 800; font-size: 0.8rem; letter-spacing: 0.5px;
    }

    .badge-cyan   { background:rgba(0,212,255,0.15);  color:#00D4FF; border:1.5px solid rgba(0,212,255,0.5);  animation:pulse-c 2.5s ease-in-out infinite; }
    .badge-green  { background:rgba(0,255,136,0.15);  color:#00FF88; border:1.5px solid rgba(0,255,136,0.5);  animation:pulse-g 2.5s ease-in-out infinite; }
    .badge-red    { background:rgba(255,59,110,0.15); color:#FF3B6E; border:1.5px solid rgba(255,59,110,0.5); animation:pulse-r 2.5s ease-in-out infinite; }
    .badge-amber  { background:rgba(255,165,0,0.15);  color:#FFA500; border:1.5px solid rgba(255,165,0,0.5);  animation:pulse-a 2.5s ease-in-out infinite; }

    .dot { width:9px; height:9px; border-radius:50%; display:inline-block; }
    .dot-c { background:#00D4FF; box-shadow:0 0 10px #00D4FF; }
    .dot-g { background:#00FF88; box-shadow:0 0 10px #00FF88; }
    .dot-r { background:#FF3B6E; box-shadow:0 0 10px #FF3B6E; }
    .dot-a { background:#FFA500; box-shadow:0 0 10px #FFA500; }

    /* ─── SECTION TITLE ─── */
    .q-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 24px 0 14px 0;
        display: flex; align-items: center; gap: 10px;
    }

    .q-title::after {
        content: "";
        flex: 1; height: 1px;
        background: linear-gradient(90deg, rgba(0,212,255,0.45), transparent);
        margin-left: 14px;
    }

    /* ─── HASH PILL ─── */
    .hash {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.76rem;
        color: #00D4FF;
        background: rgba(0, 212, 255, 0.12);
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid rgba(0, 212, 255, 0.3);
        word-break: break-all;
    }

    /* ─── THREAT TAG ─── */
    .ttag {
        display: inline-block;
        padding: 5px 12px; border-radius: 6px;
        font-size: 0.75rem; font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        margin-right: 6px; margin-bottom: 5px;
    }

    .ttag-red    { background:rgba(255,59,110,0.18); color:#FF3B6E; border:1px solid rgba(255,59,110,0.5); }
    .ttag-amber  { background:rgba(255,165,0,0.18);  color:#FFA500; border:1px solid rgba(255,165,0,0.5); }
    .ttag-green  { background:rgba(0,255,136,0.18);  color:#00FF88; border:1px solid rgba(0,255,136,0.5); }

    /* ─── ROWS ─── */
    .clean-row {
        display: flex; align-items: flex-start; gap: 12px;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        color: #E2E8F0;
        font-size: 0.88rem;
    }

    .clean-row .ck { color: #00FF88; font-size: 1.15rem; font-weight: 800; }

    .prov-row {
        display: flex; align-items: center; gap: 14px;
        padding: 10px 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }

    .prov-key {
        color: #94A3B8;
        font-size: 0.82rem;
        font-weight: 700;
        min-width: 130px;
    }

    .prec-row {
        display: flex; align-items: center; gap: 14px;
        padding: 12px 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }

    .prec-idx {
        font-family: 'JetBrains Mono', monospace;
        color: #00D4FF; font-size: 0.9rem; font-weight: 800; min-width: 26px;
    }

    .prec-name {
        color: #FFFFFF; font-weight: 700; font-size: 0.92rem; flex: 1;
    }

    .prec-desc {
        color: #94A3B8; font-size: 0.82rem; flex: 1.4;
    }

    .assum-row {
        display: flex; gap: 14px;
        padding: 14px 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }

    .assum-ck { color: #00FF88; font-size: 1.25rem; flex-shrink: 0; margin-top: 2px; font-weight: 800; }
    .assum-title { color: #FFFFFF; font-weight: 800; font-size: 0.95rem; }
    .assum-desc { color: #CBD5E1; font-size: 0.85rem; margin-top: 4px; line-height: 1.5; }

    /* ─── SIDEBAR LOGO ─── */
    .sidebar-logo {
        text-align: center;
        padding: 18px 10px 16px 10px;
        border-bottom: 1.5px solid rgba(0,212,255,0.25);
        margin-bottom: 18px;
    }

    .sidebar-logo .logo-icon { font-size: 2.5rem; }

    .sidebar-logo .logo-title {
        color: #FFFFFF;
        font-weight: 900;
        font-size: 1.3rem;
        letter-spacing: 1.5px;
        margin: 6px 0 2px 0;
    }

    .sidebar-logo .logo-sub {
        color: #94A3B8;
        font-size: 0.72rem;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin: 0 0 12px 0;
    }

    .status-row {
        display: flex; align-items: center; gap: 10px;
        color: #FFFFFF;
        font-size: 0.88rem;
        font-weight: 700;
    }
</style>
"""

# ─── PLOTLY DARK TEMPLATE ───
PLOTLY_DARK_TEMPLATE = dict(
    paper_bgcolor="rgba(10, 17, 38, 0.9)",
    plot_bgcolor="rgba(10, 17, 38, 0.5)",
    font=dict(family="Inter, sans-serif", color="#CBD5E1", size=12),
    xaxis=dict(gridcolor="rgba(51,65,85,0.4)", zerolinecolor="rgba(51,65,85,0.4)", color="#94A3B8"),
    yaxis=dict(gridcolor="rgba(51,65,85,0.4)", zerolinecolor="rgba(51,65,85,0.4)", color="#94A3B8"),
    margin=dict(l=45, r=20, t=55, b=45),
    legend=dict(font=dict(color="#CBD5E1")),
)

NEON_COLORS = ["#00D4FF", "#00FF88", "#A855F7", "#FF3B6E", "#FFA500", "#38BDF8", "#818CF8", "#22D3EE"]
