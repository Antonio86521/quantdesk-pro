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
        --surface:  #07101c;
        --surface2: #0b1220;
        --surface3: #0d1526;
        --border:   #17304d;
        --accent:   #35c2ff;
        --accent2:  #4f8cff;
        --green:    #00d27a;
        --red:      #ff5c5c;
        --yellow:   #ffb347;
        --orange:   #ff8c42;
        --text:     #e7f0fd;
        --muted:    #7f8ea3;
      }
      html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
      .stApp {
        background: radial-gradient(circle at top left, rgba(53,194,255,0.07), transparent 25%), linear-gradient(180deg, #04070b 0%, #02050a 100%);
        color: var(--text);
      }
      .block-container { padding-top: 0.55rem; padding-bottom: 0.9rem; max-width: 1220px; }
      section[data-testid="stSidebar"] { background: linear-gradient(180deg, #07101c 0%, #06101a 100%); border-right: 1px solid var(--border); }
      [data-testid="stSidebarNav"]::before {
        content: "QD"; display:flex; align-items:center; justify-content:center; color:#04111b;
        background: linear-gradient(135deg, #35c2ff 0%, #7a5cff 100%); width:32px; height:32px; border-radius:8px;
        font-size:10px; font-weight:900; letter-spacing:0.08em; margin:0.45rem auto 0.85rem auto; box-shadow:0 0 25px rgba(53,194,255,0.22);
      }
      [data-testid="stSidebarNav"] ul { padding-top: 0; }
      [data-testid="stSidebarNav"] li div { border-radius: 10px; }
      [data-testid="stSidebarNav"] a { color: var(--muted) !important; font-size: 12px; font-weight: 700; border-radius: 10px; padding: 0.58rem 0.7rem; margin-bottom: 0.14rem; }
      [data-testid="stSidebarNav"] a:hover { background-color: #0b1a2a; color: var(--text) !important; }
      [data-testid="stSidebarNav"] a[aria-current="page"] { background: linear-gradient(180deg, #0b1d2f 0%, #0a1827 100%); color: var(--accent) !important; border-left: 2px solid var(--accent); }
      [data-testid="metric-container"], div[data-testid="stMetric"] { background: linear-gradient(180deg, #07111f 0%, #081526 100%); border: 1px solid var(--border); border-radius: 14px; padding: 12px 14px; box-shadow: none; }
      [data-testid="metric-container"] label, div[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 10px !important; letter-spacing: 0.16em; text-transform: uppercase; }
      [data-testid="metric-container"] [data-testid="stMetricValue"], div[data-testid="stMetricValue"] { color: var(--text) !important; font-size: 21px !important; font-weight: 800; font-family: 'Space Mono', monospace !important; }
      [data-testid="metric-container"] [data-testid="stMetricDelta"], div[data-testid="stMetricDelta"] { font-size: 11px !important; }
      .stTabs [data-baseweb="tab-list"] { gap: 8px; }
      .stTabs [data-baseweb="tab"] { background: #07111f; border: 1px solid var(--border); border-radius: 999px; color: var(--muted); font-size: 11px; font-weight: 700; letter-spacing: 0.02em; padding: 8px 14px; }
      .stTabs [aria-selected="true"] { color: var(--accent) !important; background: #08192a !important; border-color: var(--accent) !important; }
      .stButton > button, .stDownloadButton > button { background: linear-gradient(180deg, #091321 0%, #07111d 100%); border: 1px solid var(--border); color: var(--text); font-weight: 700; font-size: 12px; letter-spacing: 0.02em; border-radius: 999px; padding: 0.58rem 1rem; transition: all 0.18s ease; }
      .stButton > button:hover, .stDownloadButton > button:hover { border-color: var(--accent); color: var(--accent); background: #091a2b; }
      .stTextInput input, .stNumberInput input, textarea { background: #07111f !important; border: 1px solid var(--border) !important; color: var(--text) !important; border-radius: 10px !important; font-size: 13px !important; }
      div[data-baseweb="select"] > div { background: #07111f !important; border: 1px solid var(--border) !important; color: var(--text) !important; border-radius: 10px !important; font-size: 13px !important; }
      [data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 14px; overflow: hidden; }
      table { font-size: 12px !important; }
      h1, h2, h3, h4 { color: var(--text); letter-spacing: -0.02em; }
      hr { border-color: var(--border); }
      .stAlert { border-radius: 10px; border: 1px solid var(--border); }
      #MainMenu, footer { visibility: hidden; }
      .terminal-panel { background: linear-gradient(180deg, #07111f 0%, #091629 100%); border: 1px solid var(--border); border-radius: 18px; padding: 18px 18px; margin-bottom: 14px; }
      .terminal-panel-title { color: var(--accent); font-size: 10px; font-weight: 800; letter-spacing: 0.24em; text-transform: uppercase; margin-bottom: 8px; }
      .terminal-panel-subtitle { color: var(--muted); font-size: 12px; }
      .terminal-ribbon { display: flex; flex-wrap: nowrap; gap: 0; background: linear-gradient(180deg, #07111f 0%, #081426 100%); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; margin-bottom: 12px; }
      .terminal-ribbon-item { padding: 10px 16px; border-right: 1px solid var(--border); min-width: 118px; }
      .terminal-ribbon-label { color: var(--muted); font-size: 9px; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; display:block; margin-bottom: 5px; }
      .terminal-ribbon-value { color: var(--text); font-size: 13px; font-weight: 800; display:block; margin-bottom: 5px; font-family: 'Space Mono', monospace !important; }
      .terminal-ribbon-delta { font-size: 11px; font-weight: 700; }
      .terminal-badge { display: inline-block; padding: 2px 7px; border-radius: 999px; font-size: 9px; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; border: 1px solid var(--border); }
    </style>
    """, unsafe_allow_html=True)
    plt.rcParams.update({
        "figure.facecolor": BG, "axes.facecolor": SURFACE, "axes.edgecolor": BORDER, "axes.labelcolor": "#9fb0c7",
        "xtick.color": MUTED, "ytick.color": MUTED, "text.color": TEXT, "grid.color": BORDER, "grid.linewidth": 0.55,
        "lines.linewidth": 1.7, "legend.facecolor": SURFACE, "legend.edgecolor": BORDER, "legend.labelcolor": TEXT,
        "figure.dpi": 110, "axes.titleweight": "bold", "axes.titlesize": 11,
    })


def apply_responsive_layout():
    st.markdown("""
    <style>
      @media (max-width: 768px) {
        .block-container { padding-left: 0.7rem !important; padding-right: 0.7rem !important; padding-top: 0.6rem !important; padding-bottom: 0.8rem !important; max-width: 100% !important; }
        h1 { font-size: 1.6rem !important; line-height: 1.18 !important; }
        h2 { font-size: 1.28rem !important; }
        h3 { font-size: 1.04rem !important; }
        .stButton > button, .stDownloadButton > button { width: 100% !important; min-height: 44px !important; }
        div[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input, textarea { font-size: 16px !important; }
        [data-testid="stDataFrame"] { overflow-x: auto !important; }
        [data-testid="metric-container"], div[data-testid="stMetric"] { padding: 10px 12px !important; }
        [data-testid="metric-container"] [data-testid="stMetricValue"], div[data-testid="stMetricValue"] { font-size: 17px !important; }
        section[data-testid="stSidebar"] { min-width: 250px !important; }
        .terminal-ribbon { flex-wrap: wrap !important; }
        .terminal-ribbon-item { min-width: 50% !important; border-right: 1px solid #17304d !important; border-bottom: 1px solid #17304d !important; }
      }
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    st.markdown(f"""
        <div style="padding: 8px 0 14px 0; margin-top: 2px; margin-bottom: 18px; border-bottom: 1px solid #17304d;">
            <div style="font-size: 32px; font-weight: 900; letter-spacing: -0.02em; color: #e7f0fd; line-height: 1.05; margin-bottom: 6px;">{title}</div>
            <div style="font-size: 10px; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; color: #7f8ea3;">{subtitle}</div>
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
    html = textwrap.dedent(f"""
    <div class="terminal-panel">
      <div class="terminal-panel-title">{title}</div>
      {"" if not subtitle else f'<div class="terminal-panel-subtitle">{subtitle}</div>'}
    </div>
    """).strip()
    st.markdown(html, unsafe_allow_html=True)


def terminal_ribbon(items):
    blocks = ""
    for label, value, delta in items:
        delta_str = str(delta)
        if delta_str.startswith("+"):
            color = GREEN
            bg = "rgba(0,210,122,0.14)"
        elif delta_str.startswith("-"):
            color = RED
            bg = "rgba(255,92,92,0.14)"
        else:
            color = MUTED
            bg = "transparent"
        blocks += f"""
        <div class="terminal-ribbon-item">
          <span class="terminal-ribbon-label">{label}</span>
          <span class="terminal-ribbon-value">{value}</span>
          <span class="terminal-ribbon-delta" style="color:{color}; background:{bg}; padding:2px 8px; border-radius:999px; display:inline-block;">{delta}</span>
        </div>
        """
    html = textwrap.dedent(f"""
    <div class="terminal-ribbon">{blocks}</div>
    """).strip()
    st.markdown(html, unsafe_allow_html=True)



