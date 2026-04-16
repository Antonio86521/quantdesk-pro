import streamlit as st
import matplotlib.pyplot as plt


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

      .stApp {
        background-color: var(--bg);
        color: var(--text);
      }

      .block-container {
        padding-top: 0.9rem;
        padding-bottom: 1rem;
        max-width: 96%;
      }

      section[data-testid="stSidebar"] {
        background-color: #07101c;
        border-right: 1px solid var(--border);
      }

      [data-testid="stSidebarNav"] {
        background-color: #07101c;
      }

      [data-testid="stSidebarNav"]::before {
        content: "QUANTDESK PRO";
        display: block;
        color: var(--text);
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 0.16em;
        padding: 0.8rem 1rem 0.5rem 1rem;
      }

      [data-testid="stSidebarNav"] ul {
        padding-top: 0.2rem;
      }

      [data-testid="stSidebarNav"] li div {
        border-radius: 6px;
      }

      [data-testid="stSidebarNav"] a {
        color: var(--muted) !important;
        font-size: 13px;
        font-weight: 600;
        border-radius: 6px;
        padding: 0.35rem 0.55rem;
      }

      [data-testid="stSidebarNav"] a:hover {
        background-color: #0f1728;
        color: var(--text) !important;
      }

      [data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: #111c31;
        color: var(--accent) !important;
        border-left: 2px solid var(--accent);
      }

      [data-testid="metric-container"] {
        background: linear-gradient(180deg, #0b1220 0%, #0d1526 100%);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 8px 10px;
        box-shadow: none;
      }

      [data-testid="metric-container"] label {
        color: var(--muted) !important;
        font-size: 10px !important;
        letter-spacing: 0.12em;
        text-transform: uppercase;
      }

      [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: var(--text) !important;
        font-size: 18px !important;
        font-weight: 700;
      }

      [data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-size: 11px !important;
      }

      .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
      }

      .stTabs [data-baseweb="tab"] {
        background: #0b1220;
        border: 1px solid var(--border);
        border-radius: 6px 6px 0 0;
        color: var(--muted);
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 10px 14px;
      }

      .stTabs [aria-selected="true"] {
        color: var(--accent) !important;
        background: #101a2e !important;
        border-bottom: 1px solid #101a2e !important;
      }

      .stButton > button {
        background: linear-gradient(180deg, #0f1a2d 0%, #0c1423 100%);
        border: 1px solid var(--border);
        color: var(--text);
        font-weight: 700;
        font-size: 12px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        border-radius: 6px;
        padding: 0.55rem 0.8rem;
        transition: all 0.18s ease;
      }

      .stButton > button:hover {
        border-color: var(--accent);
        color: var(--accent);
        background: #101a2e;
      }

      .stDownloadButton > button {
        background: linear-gradient(180deg, #0f1a2d 0%, #0c1423 100%);
        border: 1px solid var(--border);
        color: var(--text);
        font-weight: 700;
        font-size: 12px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        border-radius: 6px;
      }

      .stTextInput input,
      .stNumberInput input,
      textarea {
        background: #0b1220 !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 6px !important;
        font-size: 13px !important;
      }

      div[data-baseweb="select"] > div {
        background: #0b1220 !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 6px !important;
        font-size: 13px !important;
      }

      .stSlider [data-testid="stThumbValue"] {
        color: var(--accent);
      }

      [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 6px;
        overflow: hidden;
      }

      table {
        font-size: 12px !important;
      }

      h1, h2, h3, h4 {
        color: var(--text);
        letter-spacing: -0.02em;
      }

      hr {
        border-color: var(--border);
      }

      .stAlert {
        border-radius: 6px;
        border: 1px solid var(--border);
      }

      #MainMenu, footer {
        visibility: hidden;
      }

      .terminal-panel {
        background: linear-gradient(180deg, #0b1220 0%, #0d1526 100%);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 12px;
      }

      .terminal-panel-title {
        color: var(--text);
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 6px;
      }

      .terminal-panel-subtitle {
        color: var(--muted);
        font-size: 11px;
        margin-bottom: 10px;
      }

      .terminal-ribbon {
        display: flex;
        flex-wrap: wrap;
        gap: 0;
        background: linear-gradient(180deg, #0b1220 0%, #0e1627 100%);
        border: 1px solid var(--border);
        border-radius: 7px;
        overflow: hidden;
        margin-bottom: 12px;
      }

      .terminal-ribbon-item {
        padding: 7px 12px;
        border-right: 1px solid var(--border);
        min-width: 120px;
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


def page_header(title: str, subtitle: str = "", badge: str | None = None):
    badge_html = ""
    if badge:
        badge_html = f"""
        <span class="terminal-badge" style="color:#35c2ff; margin-left:10px;">{badge}</span>
        """

    st.markdown(f"""
    <div style="padding: 2px 0 14px 0; border-bottom: 1px solid #1b2638; margin-bottom: 16px;">
      <span style="font-size:24px; font-weight:800; letter-spacing:-0.4px; color:#d6deeb;">
        {title}
      </span>
      {badge_html}
      {"" if not subtitle else f'<div style="margin-top:6px; font-size:11px; color:#7f8ea3; letter-spacing:0.12em; text-transform:uppercase;">{subtitle}</div>'}
    </div>
    """, unsafe_allow_html=True)


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
    st.markdown(f"""
    <div class="terminal-panel">
      <div class="terminal-panel-title">{title}</div>
      {"" if not subtitle else f'<div class="terminal-panel-subtitle">{subtitle}</div>'}
    </div>
    """, unsafe_allow_html=True)


def terminal_ribbon(items):
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
        <div style="
            padding:7px 12px;
            border-right:1px solid {BORDER};
            min-width:120px;
            display:flex;
            align-items:center;
            gap:6px;
        ">
          <span style="
              color:{MUTED};
              font-size:9px;
              font-weight:700;
              letter-spacing:0.14em;
              text-transform:uppercase;
          ">{label}</span>

          <span style="
              color:{TEXT};
              font-size:13px;
              font-weight:700;
          ">{value}</span>

          <span style="
              color:{color};
              font-size:11px;
              font-weight:700;
          ">{delta}</span>
        </div>
        """

    html = f"""
    <div style="
        display:flex;
        flex-wrap:wrap;
        gap:0;
        background:linear-gradient(180deg, #0b1220 0%, #0e1627 100%);
        border:1px solid {BORDER};
        border-radius:7px;
        overflow:hidden;
        margin-bottom:12px;
    ">
      {blocks}
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

