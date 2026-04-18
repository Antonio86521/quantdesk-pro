import streamlit as st
import matplotlib.pyplot as plt
import textwrap

# ── Colour tokens (used by all pages for matplotlib charts) ───────────────────
ACCENT   = "#00d4ff"
ACCENT2  = "#7c5cfc"
GREEN    = "#00e5a0"
RED      = "#ff4560"
YELLOW   = "#ffd166"
ORANGE   = "#ff8c42"
BG       = "#060b14"
SURFACE  = "#0a1120"
SURFACE2 = "#0d1628"
BORDER   = "#1a2840"
TEXT     = "#e2eaf5"
MUTED    = "#5a7a9a"

PALETTE  = [ACCENT, ACCENT2, GREEN, YELLOW, RED, ORANGE, "#8b5cf6", "#22c55e"]


# ── Master theme (call once per page, right after set_page_config) ─────────────
def apply_theme():
    st.markdown(
        """
        <style>
        /* ── Fonts ── */
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

        /* ── Root tokens ── */
        :root {
            --bg:       #060b14;
            --s1:       #0a1120;
            --s2:       #0d1628;
            --border:   #1a2840;
            --accent:   #00d4ff;
            --accent2:  #7c5cfc;
            --green:    #00e5a0;
            --red:      #ff4560;
            --yellow:   #ffd166;
            --orange:   #ff8c42;
            --text:     #e2eaf5;
            --muted:    #5a7a9a;
            --font-main: 'DM Sans', sans-serif;
            --font-mono: 'Space Mono', monospace;
        }

        /* ── App shell ── */
        .stApp {
            background-color: var(--bg);
            color: var(--text);
            font-family: var(--font-main);
        }

        .block-container {
            padding-top: 0.8rem;
            padding-bottom: 1rem;
            max-width: 96%;
        }

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {
            background-color: #07101c;
            border-right: 1px solid var(--border);
            min-width: 220px;
            max-width: 240px;
        }

        /* Sidebar brand label */
        [data-testid="stSidebarNav"]::before {
            content: "QUANTDESK PRO";
            display: block;
            color: var(--accent);
            font-family: var(--font-mono);
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.22em;
            padding: 1.1rem 1rem 0.6rem 1rem;
            border-bottom: 1px solid var(--border);
            margin-bottom: 0.4rem;
        }

        [data-testid="stSidebarNav"] {
            background-color: #07101c;
        }

        [data-testid="stSidebarNav"] ul {
            padding-top: 0.3rem;
        }

        [data-testid="stSidebarNav"] li div {
            border-radius: 7px;
        }

        /* Nav links */
        [data-testid="stSidebarNav"] a {
            color: var(--muted) !important;
            font-family: var(--font-main);
            font-size: 13px;
            font-weight: 500;
            border-radius: 7px;
            padding: 0.42rem 0.7rem;
            transition: all 0.15s;
        }

        [data-testid="stSidebarNav"] a:hover {
            background-color: #0d1628;
            color: var(--text) !important;
        }

        /* Active page highlight */
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background-color: rgba(0, 212, 255, 0.08);
            color: var(--accent) !important;
            border-left: 2px solid var(--accent);
            border-radius: 0 7px 7px 0;
        }

        /* ── Metric cards ── */
        [data-testid="metric-container"] {
            background: linear-gradient(180deg, #0a1120 0%, #0d1628 100%);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 10px 12px;
            box-shadow: none;
        }

        [data-testid="metric-container"] label {
            color: var(--muted) !important;
            font-family: var(--font-mono) !important;
            font-size: 9px !important;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }

        [data-testid="metric-container"] [data-testid="stMetricValue"] {
            color: var(--text) !important;
            font-family: var(--font-mono) !important;
            font-size: 20px !important;
            font-weight: 700;
        }

        [data-testid="metric-container"] [data-testid="stMetricDelta"] {
            font-size: 11px !important;
        }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 3px;
            border-bottom: 1px solid var(--border);
            padding-bottom: 0;
        }

        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border: 1px solid transparent;
            border-radius: 7px 7px 0 0;
            color: var(--muted);
            font-family: var(--font-main);
            font-size: 12px;
            font-weight: 500;
            letter-spacing: 0.05em;
            padding: 8px 16px;
            transition: all 0.15s;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: var(--text);
            background: rgba(255,255,255,0.03);
        }

        .stTabs [aria-selected="true"] {
            color: var(--accent) !important;
            background: rgba(0,212,255,0.07) !important;
            border: 1px solid var(--border) !important;
            border-bottom: 1px solid var(--bg) !important;
        }

        /* ── Buttons ── */
        .stButton > button {
            background: linear-gradient(180deg, #0d1628 0%, #0a1120 100%);
            border: 1px solid var(--border);
            color: var(--text);
            font-family: var(--font-main);
            font-weight: 600;
            font-size: 12px;
            letter-spacing: 0.06em;
            border-radius: 7px;
            padding: 0.5rem 1rem;
            transition: all 0.18s ease;
        }

        .stButton > button:hover {
            border-color: var(--accent);
            color: var(--accent);
            background: rgba(0,212,255,0.06);
        }

        .stDownloadButton > button {
            background: linear-gradient(180deg, #0d1628 0%, #0a1120 100%);
            border: 1px solid var(--border);
            color: var(--text);
            font-family: var(--font-main);
            font-weight: 600;
            font-size: 12px;
            letter-spacing: 0.06em;
            border-radius: 7px;
        }

        .stDownloadButton > button:hover {
            border-color: var(--accent);
            color: var(--accent);
        }

        /* ── Inputs ── */
        .stTextInput input,
        .stNumberInput input,
        textarea {
            background: #0a1120 !important;
            border: 1px solid var(--border) !important;
            color: var(--text) !important;
            border-radius: 7px !important;
            font-family: var(--font-main) !important;
            font-size: 13px !important;
        }

        .stTextInput input:focus,
        .stNumberInput input:focus,
        textarea:focus {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 2px rgba(0,212,255,0.12) !important;
        }

        div[data-baseweb="select"] > div {
            background: #0a1120 !important;
            border: 1px solid var(--border) !important;
            color: var(--text) !important;
            border-radius: 7px !important;
            font-family: var(--font-main) !important;
            font-size: 13px !important;
        }

        /* ── Slider ── */
        .stSlider [data-testid="stThumbValue"] {
            color: var(--accent);
            font-family: var(--font-mono);
            font-size: 11px;
        }

        /* ── Dataframes ── */
        [data-testid="stDataFrame"] {
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
        }

        table {
            font-family: var(--font-main) !important;
            font-size: 12px !important;
        }

        /* ── Typography ── */
        h1, h2, h3, h4 {
            color: var(--text);
            font-family: var(--font-main);
            letter-spacing: -0.02em;
        }

        hr {
            border-color: var(--border);
            margin: 1.2rem 0;
        }

        /* ── Alerts ── */
        .stAlert {
            border-radius: 7px;
            border: 1px solid var(--border);
            font-family: var(--font-main);
        }

        /* ── Hide Streamlit chrome ── */
        #MainMenu, footer, header { visibility: hidden; }

        /* ── Custom components ── */
        .qdp-panel {
            background: linear-gradient(180deg, #0a1120 0%, #0d1628 100%);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 14px;
        }

        .qdp-panel-title {
            color: var(--text);
            font-family: var(--font-mono);
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .qdp-panel-title::before {
            content: '';
            width: 2px;
            height: 12px;
            background: var(--accent);
            border-radius: 1px;
        }

        .qdp-panel-subtitle {
            color: var(--muted);
            font-family: var(--font-main);
            font-size: 11px;
            margin-bottom: 10px;
        }

        .qdp-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 999px;
            font-family: var(--font-mono);
            font-size: 9px;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            border: 1px solid var(--border);
            color: var(--muted);
        }

        .qdp-badge-accent {
            border-color: rgba(0,212,255,0.3);
            color: var(--accent);
            background: rgba(0,212,255,0.07);
        }

        .qdp-badge-green {
            border-color: rgba(0,229,160,0.3);
            color: var(--green);
            background: rgba(0,229,160,0.07);
        }

        .qdp-badge-red {
            border-color: rgba(255,69,96,0.3);
            color: var(--red);
            background: rgba(255,69,96,0.07);
        }

        /* Pulse animation for live dot */
        @keyframes qdp-pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.25; }
        }

        .qdp-live-dot {
            display: inline-block;
            width: 6px;
            height: 6px;
            background: var(--green);
            border-radius: 50%;
            animation: qdp-pulse 2s infinite;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Matplotlib dark theme — applied globally
    plt.rcParams.update({
        "figure.facecolor":  BG,
        "axes.facecolor":    SURFACE,
        "axes.edgecolor":    BORDER,
        "axes.labelcolor":   "#8fa8c0",
        "xtick.color":       MUTED,
        "ytick.color":       MUTED,
        "text.color":        TEXT,
        "grid.color":        BORDER,
        "grid.linewidth":    0.5,
        "lines.linewidth":   1.8,
        "legend.facecolor":  SURFACE,
        "legend.edgecolor":  BORDER,
        "legend.labelcolor": TEXT,
        "figure.dpi":        110,
        "axes.titleweight":  "bold",
        "axes.titlesize":    11,
        "axes.spines.top":   False,
        "axes.spines.right": False,
    })


# ── Responsive mobile CSS (call after apply_theme on every page) ──────────────
def apply_responsive_layout():
    st.markdown(
        """
        <style>
        @media (max-width: 768px) {
            .block-container {
                padding-left: 0.6rem !important;
                padding-right: 0.6rem !important;
                padding-top: 0.6rem !important;
                max-width: 100% !important;
            }
            h1 { font-size: 1.55rem !important; }
            h2 { font-size: 1.25rem !important; }
            h3 { font-size: 1.0rem  !important; }

            .stButton > button,
            .stDownloadButton > button {
                width: 100% !important;
                min-height: 44px !important;
            }

            div[data-baseweb="select"] > div,
            .stTextInput input,
            .stNumberInput input,
            textarea { font-size: 16px !important; }

            [data-testid="stDataFrame"] { overflow-x: auto !important; }

            [data-testid="metric-container"] { padding: 8px 10px !important; }
            [data-testid="metric-container"] [data-testid="stMetricValue"] {
                font-size: 16px !important;
            }
            [data-testid="metric-container"] label { font-size: 9px !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Page header (replaces the old version — call on every page) ───────────────
def page_header(title: str, subtitle: str = ""):
    """
    Renders a consistent top header across all pages.
    Includes the QuantDesk Pro brand label, page title, subtitle,
    and a live status indicator.
    """
    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            padding: 14px 0 14px 0;
            margin-bottom: 20px;
            border-bottom: 1px solid #1a2840;
        ">
            <div>
                <div style="
                    font-family: 'Space Mono', monospace;
                    font-size: 9px;
                    color: #5a7a9a;
                    letter-spacing: 0.22em;
                    text-transform: uppercase;
                    margin-bottom: 6px;
                ">
                    QUANTDESK PRO
                </div>
                <div style="
                    font-family: 'DM Sans', sans-serif;
                    font-size: 28px;
                    font-weight: 600;
                    letter-spacing: -0.02em;
                    color: #e2eaf5;
                    line-height: 1.1;
                    margin-bottom: 4px;
                ">
                    {title}
                </div>
                <div style="
                    font-family: 'DM Sans', sans-serif;
                    font-size: 12px;
                    font-weight: 400;
                    color: #5a7a9a;
                    letter-spacing: 0.04em;
                ">
                    {subtitle}
                </div>
            </div>
            <div style="
                display: flex;
                align-items: center;
                gap: 6px;
                padding-bottom: 4px;
            ">
                <span class="qdp-live-dot"></span>
                <span style="
                    font-family: 'Space Mono', monospace;
                    font-size: 9px;
                    color: #5a7a9a;
                    letter-spacing: 0.14em;
                ">LIVE</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Metric row helper ─────────────────────────────────────────────────────────
def metric_row(data: dict):
    """Render a row of st.metric cards from a {label: value} dict."""
    cols = st.columns(len(data))
    for col, (label, value) in zip(cols, data.items()):
        col.metric(label, value)


# ── Colour helper for P&L values ──────────────────────────────────────────────
def color_pnl(val) -> str:
    try:
        n = float(str(val).replace("$", "").replace("%", "").replace(",", ""))
        return GREEN if n >= 0 else RED
    except Exception:
        return TEXT


# ── Panel component ───────────────────────────────────────────────────────────
def terminal_panel(title: str, subtitle: str = ""):
    """
    Renders a titled section panel with an accent left-border indicator.
    Use instead of st.markdown('### ...') for consistent section headers.
    """
    sub_html = (
        f'<div class="qdp-panel-subtitle">{subtitle}</div>'
        if subtitle else ""
    )
    st.markdown(
        f"""
        <div class="qdp-panel">
          <div class="qdp-panel-title">{title}</div>
          {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Ticker ribbon ─────────────────────────────────────────────────────────────
def terminal_ribbon(items):
    """
    Renders a horizontal ribbon of labelled metrics with delta colours.

    items: list of (label, value, delta_str) tuples
           delta_str should start with '+' or '-' for auto-colouring.

    Example:
        terminal_ribbon([
            ("SPY",  "538.42", "+0.84%"),
            ("VIX",  "14.83",  "-2.31%"),
            ("BTC",  "84,201", "+2.05%"),
        ])
    """
    blocks = ""
    for label, value, delta in items:
        delta_str = str(delta)
        if delta_str.startswith("+"):
            color = GREEN
        elif delta_str.startswith("-"):
            color = RED
        else:
            color = MUTED

        blocks += textwrap.dedent(f"""
        <div style="
            padding: 8px 14px;
            border-right: 1px solid {BORDER};
            min-width: 110px;
            display: flex;
            flex-direction: column;
            gap: 2px;
        ">
          <span style="
              font-family: 'Space Mono', monospace;
              color: {MUTED};
              font-size: 9px;
              font-weight: 700;
              letter-spacing: 0.16em;
              text-transform: uppercase;
          ">{label}</span>
          <span style="
              font-family: 'Space Mono', monospace;
              color: {TEXT};
              font-size: 14px;
              font-weight: 700;
          ">{value}</span>
          <span style="
              font-family: 'Space Mono', monospace;
              color: {color};
              font-size: 10px;
              font-weight: 700;
          ">{delta}</span>
        </div>
        """).strip()

    st.markdown(
        f"""
        <div style="
            display: flex;
            flex-wrap: wrap;
            gap: 0;
            background: linear-gradient(180deg, #0a1120 0%, #0d1628 100%);
            border: 1px solid {BORDER};
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 14px;
        ">
          {blocks}
        </div>
        """,
        unsafe_allow_html=True,
    )

