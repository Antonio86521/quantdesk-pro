import streamlit as st
import matplotlib.pyplot as plt


ACCENT   = "#00d4ff"
ACCENT2  = "#7c3aed"
GREEN    = "#00e676"
RED      = "#ff1744"
YELLOW   = "#ffb300"
ORANGE   = "#ff6e40"
BG       = "#0a0e1a"
SURFACE  = "#111827"
BORDER   = "#1e2d45"
TEXT     = "#e2e8f0"
MUTED    = "#64748b"

PALETTE  = [ACCENT, ACCENT2, GREEN, YELLOW, RED, ORANGE, "#a78bfa", "#34d399"]


def apply_theme():
    st.markdown("""
    <style>
      :root {
        --bg:       #0a0e1a;
        --surface:  #111827;
        --border:   #1e2d45;
        --accent:   #00d4ff;
        --accent2:  #7c3aed;
        --green:    #00e676;
        --red:      #ff1744;
        --yellow:   #ffb300;
        --text:     #e2e8f0;
        --muted:    #64748b;
      }
      .stApp { background-color: var(--bg); color: var(--text); }
      section[data-testid="stSidebar"] {
        background-color: var(--surface);
        border-right: 1px solid var(--border);
      }
      [data-testid="metric-container"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 12px 16px;
      }
      [data-testid="metric-container"] label {
        color: var(--muted) !important;
        font-size: 11px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }
      [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: var(--text) !important;
        font-size: 22px !important;
        font-weight: 700;
      }
      [data-testid="metric-container"] [data-testid="stMetricDelta"] svg { display: none; }
      .stTabs [data-baseweb="tab"] { color: var(--muted); font-weight: 600; letter-spacing: 0.05em; }
      .stTabs [aria-selected="true"] { color: var(--accent) !important; border-bottom-color: var(--accent) !important; }
      .stButton > button {
        background: linear-gradient(135deg, #00d4ff18, #7c3aed18);
        border: 1px solid var(--accent);
        color: var(--accent);
        font-weight: 600;
        letter-spacing: 0.05em;
        border-radius: 6px;
        transition: all 0.2s;
      }
      .stButton > button:hover { background: var(--accent); color: #000 !important; }
      [data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 8px; }
      .stTextInput input, .stNumberInput input, textarea {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 6px !important;
      }
      div[data-baseweb="select"] > div {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
      }
      .stSlider [data-testid="stThumbValue"] { color: var(--accent); }
      h1, h2, h3, h4 { color: var(--text); }
      hr { border-color: var(--border); }
      .stAlert { border-radius: 8px; }
      #MainMenu, footer { visibility: hidden; }
      .block-container { padding-top: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)

    plt.rcParams.update({
        "figure.facecolor": BG,
        "axes.facecolor":   SURFACE,
        "axes.edgecolor":   BORDER,
        "axes.labelcolor":  "#94a3b8",
        "xtick.color":      MUTED,
        "ytick.color":      MUTED,
        "text.color":       TEXT,
        "grid.color":       BORDER,
        "grid.linewidth":   0.6,
        "lines.linewidth":  1.8,
        "legend.facecolor": SURFACE,
        "legend.edgecolor": BORDER,
        "legend.labelcolor": TEXT,
        "figure.dpi":       110,
    })


def page_header(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div style="padding: 4px 0 18px 0; border-bottom: 1px solid #1e2d45; margin-bottom: 20px;">
      <span style="font-size:26px; font-weight:800; letter-spacing:-0.5px; color:#e2e8f0;">
        {title}
      </span>
      {"" if not subtitle else f'<span style="margin-left:10px; font-size:12px; color:#64748b; letter-spacing:0.1em; text-transform:uppercase;">{subtitle}</span>'}
    </div>
    """, unsafe_allow_html=True)


def metric_row(data: dict):
    """Render a row of metric cards. data = {label: value}"""
    cols = st.columns(len(data))
    for col, (label, value) in zip(cols, data.items()):
        col.metric(label, value)


def color_pnl(val):
    """Return green/red CSS color string based on sign."""
    try:
        return GREEN if float(str(val).replace("$", "").replace("%", "").replace(",", "")) >= 0 else RED
    except Exception:
        return TEXT
