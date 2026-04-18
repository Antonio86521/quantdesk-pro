import streamlit as st
import matplotlib.pyplot as plt
import textwrap


ACCENT   = "#35c2ff"
ACCENT2  = "#4f8cff"
GREEN    = "#00d27a"
RED      = "#ff5c5c"
YELLOW   = "#ffb347"
ORANGE   = "#ff8c42"
BG       = "#05070b"
SURFACE  = "#0b1220"
SURFACE2 = "#0f1728"
BORDER   = "#1b2638"
TEXT     = "#d6deeb"
MUTED    = "#7f8ea3"

PALETTE  = [ACCENT, ACCENT2, GREEN, YELLOW, RED, ORANGE, "#8b5cf6", "#22c55e"]


def apply_theme():
    st.markdown("""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Space+Mono:wght@400;700&display=swap');

      :root {
        --bg:       #05070b;
        --surface:  #0b1220;
        --surface2: #0f1728;
        --border:   #1b2638;
        --accent:   #35c2ff;
        --accent2:  #4f8cff;
        --green:    #00d27a;
        --red:      #ff5c5c;
        --yellow:   #ffb347;
        --orange:   #ff8c42;
        --text:     #d6deeb;
        --muted:    #7f8ea3;
      }

      html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
      }

      .stApp {
        background:
          radial-gradient(circle at top right, rgba(53,194,255,0.05), transparent 20%),
          linear-gradient(180deg, #05070b 0%, #060911 100%);
        color: var(--text);
      }

      .block-container {
        padding-top: 0.9rem;
        padding-bottom: 1rem;
        max-width: 96%;
      }

      section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #07101c 0%, #091221 100%);
        border-right: 1px solid var(--border);
      }

      [data-testid="stSidebarNav"] {
        background: transparent;
      }

      [data-testid="stSidebarNav"]::before {
        content: "QUANTDESK PRO";
        display: block;
        color: var(--text);
        font-size: 11px;
        font-weight: 900;
        letter-spacing: 0.18em;
        padding: 0.8rem 1rem 0.5rem 1rem;
      }

      [data-testid="stSidebarNav"] ul {
        padding-top: 0.25rem;
      }

      [data-testid="stSidebarNav"] li div {
        border-radius: 10px;
      }

      [data-testid="stSidebarNav"] a {
        color: var(--muted) !important;
        font-size: 13px;
        font-weight: 600;
        border-radius: 10px;
        padding: 0.5rem 0.7rem;
      }

      [data-testid="stSidebarNav"] a:hover {
        background-color: #0f1728;
        color: var(--text) !important;
      }

      [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: linear-gradient(180deg, rgba(53,194,255,0.12) 0%, rgba(79,140,255,0.08) 100%);
        color: var(--accent) !important;
        border: 1px solid rgba(53,194,255,0.22);
      }

      [data-testid="metric-container"], div[data-testid="stMetric"] {
        background: linear-gradient(180deg, #0b1220 0%, #0d1526 100%);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 10px 12px;
        box-shadow: 0 10px 22px rgba(0,0,0,0.16);
      }

      [data-testid="metric-container"] label,
      div[data-testid="stMetricLabel"] {
        color: var(--muted) !important;
        font-size: 10px !important;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        font-weight: 800 !important;
      }

      [data-testid="metric-container"] [data-testid="stMetricValue"],
      div[data-testid="stMetricValue"] {
        color: var(--text) !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        font-family: 'Space Mono', monospace !important;
      }

      [data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-size: 11px !important;
      }

      .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
      }

      .stTabs [data-baseweb="tab"] {
        background: #0b1220;
        border: 1px solid var(--border);
        border-radius: 999px;
        color: var(--muted);
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 8px 14px;
      }

      .stTabs [aria-selected="true"] {
        color: var(--accent) !important;
        background: rgba(53,194,255,0.08) !important;
        border: 1px solid rgba(53,194,255,0.24) !important;
      }

      .stButton > button,
      .stDownloadButton > button {
        background: linear-gradient(180deg, #0f1a2d 0%, #0c1423 100%);
        border: 1px solid var(--border);
        color: var(--text);
        font-weight: 800;
        font-size: 12px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        border-radius: 10px;
        padding: 0.6rem 0.85rem;
        transition: all 0.18s ease;
      }

      .stButton > button:hover,
      .stDownloadButton > button:hover {
        border-color: rgba(53,194,255,0.45);
        color: var(--accent);
        background: #101a2e;
      }

      .stTextInput input,
      .stNumberInput input,
      textarea {
        background: #0b1220 !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 10px !important;
        font-size: 13px !important;
      }

      div[data-baseweb="select"] > div {
        background: #0b1220 !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 10px !important;
        font-size: 13px !important;
      }

      .stSlider [data-testid="stThumbValue"] {
        color: var(--accent);
      }

      [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
      }

      table {
        font-size: 12px !important;
      }

      h1, h2, h3, h4 {
        color: var(--text);
        letter-spacing: -0.02em;
      }

      code,
      .terminal-panel-title,
      .terminal-ribbon-value,
      .terminal-ribbon-delta {
        font-family: 'Space Mono', monospace !important;
      }

      hr {
        border-color: var(--border);
      }

      .stAlert {
        border-radius: 10px;
        border: 1px solid var(--border);
      }

      #MainMenu, footer {
        visibility: hidden;
      }

      .terminal-panel {
        background:
          radial-gradient(circle at top right, rgba(53,194,255,0.08), transparent 28%),
          linear-gradient(180deg, #0b1220 0%, #0d1526 100%);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 12px;
      }

      .terminal-panel-title {
        color: var(--accent);
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin-bottom: 8px;
      }

      .terminal-panel-subtitle {
        color: var(--muted);
        font-size: 12px;
        margin-bottom: 0;
      }

      .terminal-ribbon {
        display: flex;
        flex-wrap: wrap;
        gap: 0;
        background: linear-gradient(180deg, #0b1220 0%, #0e1627 100%);
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 12px;
      }

      .terminal-ribbon-item {
        padding: 9px 12px;
        border-right: 1px solid var(--border);
        min-width: 130px;
      }

      .terminal-ribbon-label {
        color: var(--muted);
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
      }

      .terminal-ribbon-value {
        color: var(--text);
        font-size: 13px;
        font-weight: 700;
        margin-left: 6px;
      }

      .terminal-ribbon-delta {
        font-size: 11px;
        margin-left: 6px;
        font-weight: 700;
      }

      .terminal-badge {
        display: inline-block;
        padding: 2px 7px;
        border-radius: 999px;
        font-size: 9px;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        border: 1px solid var(--border);
      }

      .section-kicker {
        color: var(--muted);
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-bottom: 8px;
      }
    </style>
    """, unsafe_allow_html=True)

    plt.rcParams.update({
        "figure.facecolor": BG,
        "axes.facecolor":   SURFACE,
        "axes.edgecolor":   BORDER,
        "axes.labelcolor":  "#9fb0c7",
        "xtick.color":      MUTED,
        "ytick.color":      MUTED,
        "text.color":       TEXT,
        "grid.color":       BORDER,
        "grid.linewidth":   0.55,
        "lines.linewidth":  1.7,
        "legend.facecolor": SURFACE,
        "legend.edgecolor": BORDER,
        "legend.labelcolor": TEXT,
        "figure.dpi":       110,
        "axes.titleweight": "bold",
        "axes.titlesize":   11,
    })


def apply_responsive_layout():
    st.markdown("""
    <style>
      @media (max-width: 768px) {
        .block-container {
          padding-left: 0.7rem !important;
          padding-right: 0.7rem !important;
          padding-top: 0.7rem !important;
          padding-bottom: 1rem !important;
          max-width: 100% !important;
        }

        h1 { font-size: 1.65rem !important; line-height: 1.2 !important; }
        h2 { font-size: 1.3rem !important; line-height: 1.25 !important; }
        h3 { font-size: 1.05rem !important; line-height: 1.25 !important; }

        .stButton > button,
        .stDownloadButton > button {
          width: 100% !important;
          min-height: 44px !important;
          border-radius: 10px !important;
        }

        div[data-baseweb="select"] > div,
        .stTextInput input,
        .stNumberInput input,
        textarea {
          font-size: 16px !important;
        }

        [data-testid="stDataFrame"] {
          overflow-x: auto !important;
        }

        [data-testid="metric-container"], div[data-testid="stMetric"] {
          padding: 8px 10px !important;
        }

        [data-testid="metric-container"] [data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] {
          font-size: 16px !important;
        }

        [data-testid="metric-container"] label,
        div[data-testid="stMetricLabel"] {
          font-size: 9px !important;
        }

        [data-testid="stSidebar"] {
          min-width: 260px !important;
        }

        .terminal-ribbon-item {
          min-width: 100% !important;
          border-right: none !important;
          border-bottom: 1px solid #1b2638 !important;
        }
      }
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div style="padding: 18px 0 14px 0; margin-top: 6px; margin-bottom: 18px; border-bottom: 1px solid #1b2638;">
            <div style="font-size: 34px; font-weight: 900; letter-spacing: -0.02em; color: #e5eefb; line-height: 1.1; margin-bottom: 6px;">
                {title}
            </div>
            <div style="font-size: 11px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #7f8ea3;">
                {subtitle}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_row(data: dict):
    cols = st.columns(len(data))
    for col, (label, value) in zip(cols, data.items()):
        col.metric(label, value)


def color_pnl(val):
    try:
        return GREEN if float(str(val).replace("$", "").replace("%", "").replace(",", "")) >= 0 else RED
    except Exception:
        return TEXT


def terminal_panel(title: str, subtitle: str = ""):
    html = textwrap.dedent(f"""
    <div class="terminal-panel">
      <div class="terminal-panel-title">{title}</div>
      {"" if not subtitle else f'<div class="terminal-panel-subtitle">{subtitle}</div>'}
    </div>
    """).strip()
    st.markdown(html, unsafe_allow_html=True)


def terminal_ribbon(items):
    if isinstance(items, str):
        terminal_panel("Workspace", items)
        return

    blocks = ""
    for label, value, delta in items:
        delta_str = str(delta)
        if delta_str.startswith("+"):
            color = GREEN
        elif delta_str.startswith("-"):
            color = RED
        else:
            color = MUTED

        blocks += f"""
        <div class="terminal-ribbon-item" style="display:flex; align-items:center; gap:6px;">
          <span class="terminal-ribbon-label">{label}</span>
          <span class="terminal-ribbon-value">{value}</span>
          <span class="terminal-ribbon-delta" style="color:{color};">{delta}</span>
        </div>
        """

    html = textwrap.dedent(f"""
    <div class="terminal-ribbon">
      {blocks}
    </div>
    """).strip()
    st.markdown(html, unsafe_allow_html=True)


