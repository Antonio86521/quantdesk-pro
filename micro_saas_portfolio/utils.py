"""
utils.py — QuantDesk Pro design system.
Apex Capital-inspired: deep navy/slate palette, Syne + DM Mono typography,
glass-card components, refined metric tiles and page structure.
"""

from __future__ import annotations

import io
import zipfile
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# ── Colour tokens (match Apex palette) ────────────────────────────────────────
BG      = "#080b10"
BG2     = "#0d1117"
BG3     = "#131920"
BG4     = "#1a2230"
BG5     = "#202c3a"

BORDER  = "rgba(255,255,255,0.06)"
BORDER2 = "rgba(255,255,255,0.11)"
BORDER3 = "rgba(255,255,255,0.18)"

# Matplotlib-safe border/grid colours (matplotlib cannot parse CSS rgba() strings)
MPL_BORDER = "#1e2b3a"   # equivalent of rgba(255,255,255,0.06) over dark bg
MPL_GRID   = "#161f2b"   # equivalent of rgba(255,255,255,0.04) over dark bg

TEXT    = "#dde4f0"
TEXT2   = "#7a8fa8"
TEXT3   = "#3d5068"

ACCENT  = "#2f80ed"
ACCENT2 = "#5ba3f5"
ACCENT3 = "rgba(47,128,237,0.12)"

GREEN   = "#0ecb81"
GREEN2  = "rgba(14,203,129,0.12)"
RED     = "#f6465d"
RED2    = "rgba(246,70,93,0.12)"
AMBER   = "#f0a500"
AMBER2  = "rgba(240,165,0,0.12)"
PURPLE  = "#7c5cfc"
PURPLE2 = "rgba(124,92,252,0.12)"
TEAL    = "#00c9a7"
MUTED   = TEXT2

ORANGE  = "#f0a500"   # alias kept for backward compat — same as AMBER
YELLOW  = AMBER       # alias for pages that import YELLOW

PALETTE = [ACCENT, PURPLE, GREEN, AMBER, RED, TEAL, "#d4a853", ACCENT2]


# ── Global theme ──────────────────────────────────────────────────────────────

def apply_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

        :root {
          --bg:      #080b10;
          --bg2:     #0d1117;
          --bg3:     #131920;
          --bg4:     #1a2230;
          --bg5:     #202c3a;
          --border:  rgba(255,255,255,0.06);
          --border2: rgba(255,255,255,0.11);
          --border3: rgba(255,255,255,0.18);
          --text:    #dde4f0;
          --text2:   #7a8fa8;
          --text3:   #3d5068;
          --accent:  #2f80ed;
          --accent2: #5ba3f5;
          --accent3: rgba(47,128,237,0.12);
          --green:   #0ecb81;
          --green2:  rgba(14,203,129,0.12);
          --red:     #f6465d;
          --red2:    rgba(246,70,93,0.12);
          --amber:   #f0a500;
          --purple:  #7c5cfc;
          --teal:    #00c9a7;
          --font-d:  'Syne', sans-serif;
          --font-b:  'Inter', sans-serif;
          --font-m:  'DM Mono', monospace;
        }

        html, body, [class*="css"] {
          font-family: var(--font-b);
          background: var(--bg);
          color: var(--text);
        }

        .stApp { background: var(--bg) !important; }
        .block-container { padding-top: 0.6rem; padding-bottom: 1rem; max-width: 1260px; }

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {
          background: var(--bg2) !important;
          border-right: 1px solid var(--border2) !important;
        }
        [data-testid="stSidebarNav"]::before {
          content: "QD";
          display: flex; align-items: center; justify-content: center;
          background: linear-gradient(135deg, #2f80ed 0%, #7c5cfc 100%);
          color: #fff; width: 34px; height: 34px; border-radius: 9px;
          font-family: var(--font-d); font-size: 13px; font-weight: 800;
          margin: 1rem auto 0.8rem auto;
          box-shadow: 0 0 24px rgba(47,128,237,0.35);
        }
        [data-testid="stSidebarNav"] a {
          color: var(--text2) !important;
          font-size: 12px; font-weight: 400;
          border-radius: 8px; padding: 0.55rem 0.85rem;
          transition: all 0.14s;
        }
        [data-testid="stSidebarNav"] a:hover {
          background: var(--bg3) !important; color: var(--text) !important;
        }
        [data-testid="stSidebarNav"] a[aria-current="page"] {
          background: var(--accent3) !important;
          color: var(--accent2) !important;
          border: 1px solid rgba(47,128,237,0.22);
        }

        /* ── Metrics ── */
        [data-testid="metric-container"], div[data-testid="stMetric"] {
          background: var(--bg3);
          border: 1px solid var(--border);
          border-radius: 10px;
          padding: 14px 16px;
        }
        [data-testid="metric-container"] label,
        div[data-testid="stMetricLabel"] {
          color: var(--text2) !important;
          font-size: 10px !important;
          letter-spacing: 0.4px;
          text-transform: uppercase;
          font-weight: 500;
        }
        div[data-testid="stMetricValue"] {
          color: var(--text) !important;
          font-family: var(--font-m) !important;
          font-size: 22px !important;
          font-weight: 500 !important;
          letter-spacing: -0.5px;
        }
        div[data-testid="stMetricDelta"] { font-size: 11px !important; }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
          background: var(--bg3); padding: 3px; border-radius: 8px;
          gap: 2px; width: fit-content;
        }
        .stTabs [data-baseweb="tab"] {
          background: transparent;
          color: var(--text2);
          font-size: 11.5px; font-weight: 500;
          border-radius: 6px; padding: 5px 13px;
          border: none;
        }
        .stTabs [aria-selected="true"] {
          background: var(--bg5) !important;
          color: var(--text) !important;
          font-weight: 500;
        }

        /* ── Buttons ── */
        .stButton > button, .stDownloadButton > button {
          background: var(--bg3);
          border: 1px solid var(--border2);
          color: var(--text);
          font-size: 11.5px; font-weight: 500;
          border-radius: 7px; padding: 6px 14px;
          transition: all 0.13s;
          font-family: var(--font-b);
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
          background: var(--bg4); border-color: var(--border3);
        }

        /* ── Inputs ── */
        .stTextInput input, .stNumberInput input, textarea {
          background: var(--bg4) !important;
          border: 1px solid var(--border2) !important;
          color: var(--text) !important;
          border-radius: 7px !important;
          font-size: 13px !important;
          font-family: var(--font-b) !important;
        }
        .stTextInput input:focus, .stNumberInput input:focus { border-color: var(--accent) !important; }
        div[data-baseweb="select"] > div {
          background: var(--bg4) !important;
          border: 1px solid var(--border2) !important;
          color: var(--text) !important;
          border-radius: 7px !important;
          font-size: 13px !important;
        }

        /* ── DataFrames / Tables ── */
        [data-testid="stDataFrame"] {
          border: 1px solid var(--border); border-radius: 10px; overflow: hidden;
        }
        table { font-size: 12px !important; }
        th {
          text-align: left; padding: 7px 12px;
          font-size: 10px; color: var(--text2);
          letter-spacing: 0.6px; text-transform: uppercase;
          border-bottom: 1px solid var(--border) !important;
        }
        td { padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,0.025) !important; }
        tr:hover td { background: rgba(255,255,255,0.018); }

        /* ── Typography ── */
        h1, h2, h3, h4 {
          font-family: var(--font-d);
          color: var(--text);
          letter-spacing: -0.3px;
        }
        hr { border-color: var(--border) !important; }

        /* ── Card components ── */
        .qd-card {
          background: var(--bg2);
          border: 1px solid var(--border);
          border-radius: 14px;
          padding: 16px 18px;
        }
        .qd-card-hd {
          display: flex; align-items: flex-start;
          justify-content: space-between;
          margin-bottom: 14px; gap: 10px;
        }
        .qd-card-title {
          font-family: var(--font-d);
          font-size: 13px; font-weight: 600;
        }
        .qd-card-sub { font-size: 10.5px; color: var(--text2); margin-top: 2px; }

        /* ── Badges ── */
        .b {
          display: inline-block; padding: 2px 7px;
          border-radius: 4px; font-size: 10px; font-weight: 500;
          letter-spacing: 0.2px; white-space: nowrap;
        }
        .b-bl { background: var(--accent3); color: var(--accent2); }
        .b-gr { background: var(--green2);  color: var(--green); }
        .b-rd { background: var(--red2);    color: var(--red); }
        .b-am { background: rgba(240,165,0,0.12); color: var(--amber); }
        .b-pu { background: rgba(124,92,252,0.12); color: var(--purple); }

        /* ── Section label ── */
        .section-lbl {
          font-size: 9.5px; color: var(--text3);
          letter-spacing: 1px; text-transform: uppercase;
          font-weight: 600; margin-bottom: 10px;
        }

        /* ── Page header ── */
        .pg-hd {
          margin-bottom: 18px;
          padding-bottom: 14px;
          border-bottom: 1px solid var(--border);
        }
        .pg-hd-title {
          font-family: var(--font-d);
          font-size: 20px; font-weight: 700;
          letter-spacing: -0.3px; color: var(--text);
        }
        .pg-hd-sub { font-size: 12px; color: var(--text2); margin-top: 3px; }

        /* ── Misc ── */
        .divider { height: 1px; background: var(--border); margin: 14px 0; }
        .dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; display: inline-block; }

        /* ── Footer ── */
        .qd-footer {
          margin-top: 42px; padding-top: 14px;
          border-top: 1px solid var(--border);
          color: var(--text2); font-size: 11px;
          display: flex; justify-content: space-between;
          align-items: center; flex-wrap: wrap; gap: 10px;
        }
        .qd-footer a { color: var(--accent); text-decoration: none; }
        .qd-footer a:hover { text-decoration: underline; }

        /* ── Section intro panel ── */
        .section-intro {
          background: var(--bg2);
          border: 1px solid var(--border);
          border-radius: 10px;
          padding: 12px 14px;
          margin-bottom: 14px;
        }
        .section-intro-title {
          font-family: var(--font-d);
          font-size: 11px; font-weight: 600;
          color: var(--text); margin-bottom: 4px;
        }
        .section-intro-body { color: var(--text2); font-size: 12px; line-height: 1.6; }

        /* ── Alert overrides ── */
        .stAlert { border-radius: 8px; border: 1px solid var(--border); }

        /* ── Scrollbar ── */
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: var(--bg5); border-radius: 2px; }

        #MainMenu, footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Matplotlib dark theme aligned to Apex palette
    plt.rcParams.update({
        "figure.facecolor":  BG,
        "axes.facecolor":    BG2,
        "axes.edgecolor":    BG4,
        "axes.labelcolor":   TEXT2,
        "xtick.color":       TEXT2,
        "ytick.color":       TEXT2,
        "text.color":        TEXT,
        "grid.color":        MPL_GRID,
        "grid.linewidth":    0.5,
        "lines.linewidth":   1.8,
        "legend.facecolor":  BG2,
        "legend.edgecolor":  BG4,
        "legend.labelcolor": TEXT,
        "figure.dpi":        110,
        "axes.titleweight":  "bold",
        "axes.titlesize":    11,
        "axes.spines.top":   False,
        "axes.spines.right": False,
    })


def apply_responsive_layout() -> None:
    st.markdown(
        """
        <style>
        @media (max-width: 768px) {
          .block-container {
            padding-left: 0.7rem !important;
            padding-right: 0.7rem !important;
            padding-top: 0.5rem !important;
          }
          h1 { font-size: 1.55rem !important; }
          h2 { font-size: 1.25rem !important; }
          .stButton > button, .stDownloadButton > button { width: 100% !important; }
          div[data-baseweb="select"] > div,
          .stTextInput input,
          .stNumberInput input,
          textarea { font-size: 16px !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Page header ───────────────────────────────────────────────────────────────

def page_header(title: str, subtitle: str = "") -> None:
    sub_html = f'<div class="pg-hd-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="pg-hd">
            <div class="pg-hd-title">{title}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Metric card (custom HTML, richer than st.metric) ─────────────────────────

def metric_card(label: str, value: str, delta: str = "", delta_pos: Optional[bool] = None) -> str:
    if delta:
        if delta_pos is True:
            d_style = f"color: {GREEN}; font-size: 10.5px; margin-top: 5px;"
        elif delta_pos is False:
            d_style = f"color: {RED}; font-size: 10.5px; margin-top: 5px;"
        else:
            d_style = f"color: {TEXT2}; font-size: 10.5px; margin-top: 5px;"
        delta_html = f'<div style="{d_style}">{delta}</div>'
    else:
        delta_html = ""

    return f"""
    <div style="background:{BG3}; border:1px solid {BORDER}; border-radius:10px;
                padding:14px 16px;">
      <div style="font-size:10px; color:{TEXT2}; letter-spacing:0.4px;
                  text-transform:uppercase; margin-bottom:6px;">{label}</div>
      <div style="font-family:'DM Mono',monospace; font-size:22px; font-weight:500;
                  line-height:1.1; letter-spacing:-0.5px; color:{TEXT};">{value}</div>
      {delta_html}
    </div>
    """


def badge(text: str, variant: str = "bl") -> str:
    """variant: bl/gr/rd/am/pu"""
    cls_map = {
        "bl": f"background:{ACCENT3}; color:{ACCENT2};",
        "gr": f"background:{GREEN2}; color:{GREEN};",
        "rd": f"background:{RED2}; color:{RED};",
        "am": f"background:{AMBER2}; color:{AMBER};",
        "pu": f"background:{PURPLE2}; color:{PURPLE};",
    }
    style = cls_map.get(variant, cls_map["bl"])
    return (
        f'<span style="display:inline-block; padding:2px 7px; border-radius:4px; '
        f'font-size:10px; font-weight:500; white-space:nowrap; {style}">{text}</span>'
    )


def section_intro(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="section-intro">
            <div class="section-intro-title">{title}</div>
            <div class="section-intro-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Plan helpers ──────────────────────────────────────────────────────────────

def get_active_plan() -> str:
    return st.session_state.get("active_plan", "free")


def is_pro() -> bool:
    return get_active_plan() == "pro"


def premium_notice(feature_name: str = "this feature") -> None:
    st.info(
        f"**{feature_name}** is available on the Pro plan. "
        "Switch the plan toggle in the sidebar to **Pro** to unlock it."
    )


# ── Download helpers ──────────────────────────────────────────────────────────

def make_download_zip(file_map: Dict[str, "pd.DataFrame | str"]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, obj in file_map.items():
            if isinstance(obj, pd.DataFrame):
                zf.writestr(name, obj.to_csv(index=True))
            else:
                zf.writestr(name, str(obj))
    buf.seek(0)
    return buf.getvalue()


def html_report(title: str, sections: List[Tuple[str, str]]) -> str:
    body = "".join(
        f"<section style='margin-bottom:24px;'>"
        f"<h2 style='font-family:Inter,sans-serif;color:#0f172a'>{hdr}</h2>"
        f"<div style='font-family:Inter,sans-serif;color:#334155;line-height:1.65'>{content}</div>"
        f"</section>"
        for hdr, content in sections
    )
    return f"""
    <html><head><meta charset='utf-8'><title>{title}</title></head>
    <body style='background:#f8fafc;padding:36px;'>
      <div style='max-width:980px;margin:0 auto;background:#fff;
                  border:1px solid #cbd5e1;border-radius:18px;padding:32px;'>
        <h1 style='font-family:Inter,sans-serif;color:#0f172a;margin-top:0'>{title}</h1>
        {body}
      </div>
    </body></html>
    """


# ── Formatting ────────────────────────────────────────────────────────────────

def safe_pct(value: float, decimals: int = 2) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "—"
    return f"{value:.{decimals}%}"


def safe_num(value: float, decimals: int = 2) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "—"
    return f"{value:.{decimals}f}"


# ── Metric glossary ───────────────────────────────────────────────────────────

METRIC_EXPLANATIONS: Dict[str, str] = {
    "Portfolio Value": "Current market value of all holdings at latest prices.",
    "Invested Capital": "Total originally paid for all positions.",
    "Unrealized P&L": "Mark-to-market gain/loss if all positions were closed now.",
    "Total Return": "Overall percentage gain/loss over the selected period.",
    "Ann. Return": "Annualised return estimated from daily returns.",
    "Ann. Volatility": "Annualised standard deviation of daily returns.",
    "Sharpe Ratio": "Return per unit of volatility; higher is better.",
    "Sortino": "Return per unit of downside volatility only.",
    "Calmar": "Annualised return divided by absolute max drawdown.",
    "Max Drawdown": "Largest peak-to-trough decline over the selected period.",
    "Beta": "Sensitivity of portfolio returns to benchmark moves.",
    "Alpha": "Excess return above what benchmark exposure would predict.",
    "Historical VaR 95%": "Daily loss threshold exceeded only 5% of the time.",
    "Parametric VaR 95%": "Model-based 95% daily loss threshold (normal distribution).",
    "CVaR 95%": "Average loss during the worst 5% of days.",
    "R²": "Fraction of return variation explained by the benchmark.",
    "Tracking Error": "Volatility of the portfolio's active return vs benchmark.",
    "Information Ratio": "Active return divided by tracking error.",
    "Omega": "Ratio of probability-weighted gains to losses above a threshold.",
    "Gain/Pain": "Total gains divided by total absolute losses.",
    "Market Beta": "Exposure to broad market factor (SPY proxy).",
    "Size": "Small-cap vs large-cap style tilt.",
    "Value": "Value vs growth style tilt.",
    "Momentum": "Trend-following exposure.",
}


def explain_metric(name: str) -> None:
    text = METRIC_EXPLANATIONS.get(name)
    if text:
        st.caption(text)


def glossary_expander(title: str, items: Dict[str, str]) -> None:
    with st.expander(title):
        for key, value in items.items():
            st.markdown(f"**{key}** — {value}")


# ── Footer ────────────────────────────────────────────────────────────────────

def app_footer() -> None:
    st.markdown(
        """
        <div class="qd-footer">
          <div style="display:flex;gap:14px;flex-wrap:wrap;">
            <span>© 2026 QuantDesk Pro</span>
            <a href="/About" target="_self">About</a>
            <a href="/Privacy" target="_self">Privacy</a>
            <a href="/Terms" target="_self">Terms</a>
          </div>
          <div>Educational use only · Not investment advice</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
