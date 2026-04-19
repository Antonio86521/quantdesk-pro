import io
import textwrap
import zipfile
from typing import Dict, Iterable, List, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# ── Design tokens ──────────────────────────────────────────────────────────────
ACCENT   = "#2563eb"   # electric blue — primary action
ACCENT2  = "#0ea5e9"   # sky blue — secondary
GREEN    = "#10b981"   # emerald
RED      = "#ef4444"   # red
YELLOW   = "#f59e0b"   # amber
ORANGE   = "#f97316"   # orange
BG       = "#f8fafc"   # near-white page background
SURFACE  = "#ffffff"   # card surface
SURFACE2 = "#f1f5f9"   # subtle inset surface
BORDER   = "#e2e8f0"   # hairline border
TEXT     = "#0f172a"   # near-black body text
MUTED    = "#64748b"   # slate-500 secondary text

# Legacy tokens — kept for page compatibility (7_Macro, 10_Factor_Exposure use these)
BORDER   = "#e2e8f0"
TEXT     = "#0f172a"
BG       = "#f8fafc"
SURFACE  = "#ffffff"
SURFACE2 = "#f1f5f9"

PALETTE = [ACCENT, ACCENT2, GREEN, YELLOW, RED, ORANGE, "#8b5cf6", "#06b6d4"]


def apply_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Mono:wght@400;500&display=swap');

        :root {
            --bg:       #f8fafc;
            --surface:  #ffffff;
            --surface2: #f1f5f9;
            --border:   #e2e8f0;
            --accent:   #2563eb;
            --accent2:  #0ea5e9;
            --green:    #10b981;
            --red:      #ef4444;
            --yellow:   #f59e0b;
            --orange:   #f97316;
            --text:     #0f172a;
            --muted:    #64748b;
            --radius:   10px;
        }

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
            color: var(--text);
        }

        .stApp {
            background: var(--bg);
        }

        /* ── Layout ── */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
            max-width: 1200px !important;
        }

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {
            background: var(--surface);
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebarNav"] a {
            color: var(--muted) !important;
            font-size: 13px;
            font-weight: 500;
            border-radius: 8px;
            padding: 0.55rem 0.9rem;
            margin-bottom: 2px;
        }

        [data-testid="stSidebarNav"] a:hover {
            background: var(--surface2);
            color: var(--text) !important;
        }

        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background: #eff6ff;
            color: var(--accent) !important;
            font-weight: 600;
        }

        /* ── Metrics ── */
        [data-testid="metric-container"],
        div[data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 16px 18px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }

        [data-testid="metric-container"] label,
        div[data-testid="stMetricLabel"] {
            color: var(--muted) !important;
            font-size: 11px !important;
            font-weight: 600 !important;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }

        [data-testid="metric-container"] [data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] {
            color: var(--text) !important;
            font-size: 22px !important;
            font-weight: 700 !important;
            font-family: 'DM Mono', monospace !important;
            letter-spacing: -0.01em;
        }

        div[data-testid="stMetricDelta"] {
            font-size: 12px !important;
            font-weight: 600 !important;
        }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            border-bottom: 1px solid var(--border);
            background: transparent;
        }

        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border: none;
            border-bottom: 2px solid transparent;
            border-radius: 0;
            color: var(--muted);
            font-size: 13px;
            font-weight: 600;
            padding: 10px 18px;
            margin-bottom: -1px;
        }

        .stTabs [aria-selected="true"] {
            color: var(--accent) !important;
            border-bottom-color: var(--accent) !important;
            background: transparent !important;
        }

        /* ── Buttons ── */
        .stButton > button,
        .stDownloadButton > button {
            background: var(--accent);
            border: none;
            color: #fff;
            font-weight: 600;
            font-size: 13px;
            border-radius: 8px;
            padding: 0.5rem 1.1rem;
            transition: background 0.15s ease, box-shadow 0.15s ease;
            box-shadow: 0 1px 2px rgba(37,99,235,0.18);
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            background: #1d4ed8;
            box-shadow: 0 4px 12px rgba(37,99,235,0.28);
        }

        /* ── Inputs ── */
        .stTextInput input,
        .stNumberInput input,
        textarea {
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            color: var(--text) !important;
            border-radius: 8px !important;
            font-size: 14px !important;
            font-family: 'DM Sans', sans-serif !important;
        }

        .stTextInput input:focus,
        .stNumberInput input:focus,
        textarea:focus {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
        }

        div[data-baseweb="select"] > div {
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            color: var(--text) !important;
            border-radius: 8px !important;
            font-size: 14px !important;
        }

        /* ── DataFrames ── */
        [data-testid="stDataFrame"] {
            border: 1px solid var(--border);
            border-radius: var(--radius);
            overflow: hidden;
        }

        table { font-size: 13px !important; }

        /* ── Typography ── */
        h1 { font-size: 26px !important; font-weight: 700 !important; letter-spacing: -0.02em; color: var(--text); }
        h2 { font-size: 19px !important; font-weight: 700 !important; letter-spacing: -0.01em; color: var(--text); }
        h3 { font-size: 16px !important; font-weight: 600 !important; color: var(--text); }

        hr { border-color: var(--border); margin: 1.5rem 0; }

        .stAlert {
            border-radius: 8px;
            border: 1px solid var(--border);
            font-size: 13px;
        }

        #MainMenu, footer { visibility: hidden; }

        /* ── Shared components ── */
        .qd-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 20px 22px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }

        .qd-section-label {
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--muted);
            margin-bottom: 14px;
        }

        .qd-badge {
            display: inline-flex;
            align-items: center;
            padding: 3px 9px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.04em;
        }

        .qd-badge-green  { background: #d1fae5; color: #065f46; }
        .qd-badge-red    { background: #fee2e2; color: #991b1b; }
        .qd-badge-blue   { background: #dbeafe; color: #1e40af; }
        .qd-badge-gray   { background: #f1f5f9; color: #475569; }
        .qd-badge-yellow { background: #fef3c7; color: #92400e; }

        .qd-divider {
            height: 1px;
            background: var(--border);
            margin: 16px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Matplotlib to match light theme
    plt.rcParams.update(
        {
            "figure.facecolor":   "#ffffff",
            "axes.facecolor":     "#ffffff",
            "axes.edgecolor":     "#e2e8f0",
            "axes.labelcolor":    "#64748b",
            "xtick.color":        "#94a3b8",
            "ytick.color":        "#94a3b8",
            "text.color":         "#0f172a",
            "grid.color":         "#f1f5f9",
            "grid.linewidth":     0.8,
            "lines.linewidth":    2.0,
            "legend.facecolor":   "#ffffff",
            "legend.edgecolor":   "#e2e8f0",
            "legend.labelcolor":  "#0f172a",
            "figure.dpi":         120,
            "axes.titleweight":   "bold",
            "axes.titlesize":     12,
            "axes.spines.top":    False,
            "axes.spines.right":  False,
        }
    )


def apply_responsive_layout():
    st.markdown(
        """
        <style>
        @media (max-width: 768px) {
            .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                padding-top: 1rem !important;
                max-width: 100% !important;
            }
            h1 { font-size: 1.5rem !important; }
            h2 { font-size: 1.2rem !important; }
            .stButton > button,
            .stDownloadButton > button { width: 100% !important; min-height: 44px !important; }
            div[data-baseweb="select"] > div,
            .stTextInput input,
            .stNumberInput input,
            textarea { font-size: 16px !important; }
            [data-testid="stDataFrame"] { overflow-x: auto !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <div style="font-size: 24px; font-weight: 700; letter-spacing: -0.02em;
                        color: #0f172a; line-height: 1.2; margin-bottom: 4px;">{title}</div>
            {"" if not subtitle else
             f'<div style="font-size: 13px; color: #64748b; font-weight: 400;">{subtitle}</div>'}
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


def badge(text: str, variant: str = "gray") -> str:
    """Return an inline HTML badge. variant: green | red | blue | gray | yellow"""
    return f'<span class="qd-badge qd-badge-{variant}">{text}</span>'


def section_label(text: str):
    st.markdown(f'<div class="qd-section-label">{text}</div>', unsafe_allow_html=True)


def card_open():
    st.markdown('<div class="qd-card">', unsafe_allow_html=True)


def card_close():
    st.markdown('</div>', unsafe_allow_html=True)


def get_active_plan() -> str:
    if "active_plan" not in st.session_state:
        st.session_state["active_plan"] = "pro"
    return str(st.session_state["active_plan"]).lower()


def plan_is_pro() -> bool:
    return get_active_plan() == "pro"


def render_plan_selector(location: str = "sidebar") -> str:
    host = st.sidebar if location == "sidebar" else st
    current = get_active_plan()
    plan = host.radio(
        "Access Plan",
        options=["free", "pro"],
        index=0 if current == "free" else 1,
        horizontal=True,
        key=f"plan_selector_{location}",
    )
    st.session_state["active_plan"] = plan
    return plan


def premium_notice(feature_name: str = "this feature"):
    st.info(f"**{feature_name}** is available on the Pro plan.")


def make_download_zip(file_map: Dict[str, "pd.DataFrame | str"]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, obj in file_map.items():
            if isinstance(obj, pd.DataFrame):
                zf.writestr(name, obj.to_csv(index=True))
            else:
                zf.writestr(name, str(obj))
    buffer.seek(0)
    return buffer.getvalue()


def html_report(title: str, sections: List[Tuple[str, str]]) -> str:
    body = "".join(
        f"<section style='margin-bottom:24px;'>"
        f"<h2 style='font-family:DM Sans,sans-serif;color:#0f172a;font-size:16px;font-weight:600'>{header}</h2>"
        f"<div style='font-family:DM Sans,sans-serif;color:#475569;font-size:14px;line-height:1.7'>{content}</div>"
        f"</section>"
        for header, content in sections
    )
    return f"""
    <html>
      <head>
        <meta charset='utf-8'>
        <title>{title}</title>
        <link href='https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&display=swap' rel='stylesheet'>
      </head>
      <body style='background:#f8fafc;padding:40px;'>
        <div style='max-width:900px;margin:0 auto;background:white;border:1px solid #e2e8f0;border-radius:12px;padding:40px;'>
          <h1 style='font-family:DM Sans,sans-serif;color:#0f172a;font-size:22px;font-weight:700;margin-top:0;
                     letter-spacing:-0.02em'>{title}</h1>
          <hr style='border:none;border-top:1px solid #e2e8f0;margin:20px 0 28px 0'>
          {body}
        </div>
      </body>
    </html>
    """


def safe_pct(value: float, decimals: int = 2) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{value:.{decimals}%}"


def safe_num(value: float, decimals: int = 2) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{value:.{decimals}f}"


# ── Legacy aliases (kept for page compatibility) ───────────────────────────────
def terminal_panel(title: str, subtitle: str = ""):
    """Deprecated — use page_header() or section_label() instead."""
    page_header(title, subtitle)


def terminal_ribbon(items: Iterable[Tuple[str, str, str]]):
    """Deprecated — use st.columns + st.metric instead."""
    data = {label: value for label, value, _ in items}
    metric_row(data)
