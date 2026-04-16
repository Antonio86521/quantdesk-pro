import streamlit as st

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

PALETTE = [ACCENT, ACCENT2, GREEN, YELLOW, RED, ORANGE, "#8b5cf6", "#22c55e"]


def apply_theme():
    st.markdown(
        f"""
        <style>
          :root {{
            --bg: {BG};
            --surface: {SURFACE};
            --surface2: {SURFACE2};
            --border: {BORDER};
            --accent: {ACCENT};
            --accent2: {ACCENT2};
            --green: {GREEN};
            --red: {RED};
            --yellow: {YELLOW};
            --orange: {ORANGE};
            --text: {TEXT};
            --muted: {MUTED};
          }}

          .stApp {{
            background-color: var(--bg);
            color: var(--text);
          }}

          .block-container {{
            padding-top: 0.85rem;
            padding-bottom: 1rem;
            max-width: 96%;
          }}

          section[data-testid="stSidebar"] {{
            background-color: #07101c;
            border-right: 1px solid var(--border);
          }}

          [data-testid="stSidebarNav"] {{
            background-color: #07101c;
          }}

          [data-testid="stSidebarNav"]::before {{
            content: "QUANTDESK PRO";
            display: block;
            color: var(--text);
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.16em;
            padding: 0.85rem 1rem 0.55rem 1rem;
          }}

          [data-testid="stSidebarNav"] ul {{
            padding-top: 0.15rem;
          }}

          [data-testid="stSidebarNav"] a {{
            color: var(--muted) !important;
            font-size: 13px;
            font-weight: 600;
            border-radius: 6px;
            padding: 0.38rem 0.55rem;
          }}

          [data-testid="stSidebarNav"] a:hover {{
            background-color: #0f1728;
            color: var(--text) !important;
          }}

          [data-testid="stSidebarNav"] a[aria-current="page"] {{
            background-color: #111c31;
            color: var(--accent) !important;
            border-left: 2px solid var(--accent);
          }}

          [data-testid="metric-container"] {{
            background: linear-gradient(180deg, #0b1220 0%, #0d1526 100%);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 10px 12px;
            box-shadow: none;
          }}

          [data-testid="metric-container"] label {{
            color: var(--muted) !important;
            font-size: 10px !important;
            letter-spacing: 0.12em;
            text-transform: uppercase;
          }}

          [data-testid="metric-container"] [data-testid="stMetricValue"] {{
            color: var(--text) !important;
            font-size: 18px !important;
            font-weight: 700;
          }}

          [data-testid="metric-container"] [data-testid="stMetricDelta"] {{
            font-size: 11px !important;
          }}

          .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
          }}

          .stTabs [data-baseweb="tab"] {{
            background: #0b1220;
            border: 1px solid var(--border);
            border-radius: 8px 8px 0 0;
            color: var(--muted);
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 10px 14px;
          }}

          .stTabs [aria-selected="true"] {{
            color: var(--accent) !important;
            background: #101a2d !important;
          }}

          .stButton > button {{
            background: linear-gradient(180deg, #0d1526 0%, #101b30 100%);
            color: var(--text);
            border: 1px solid var(--border);
            border-radius: 8px;
            font-weight: 700;
            letter-spacing: 0.04em;
          }}

          .stButton > button:hover {{
            border-color: var(--accent);
            color: var(--accent);
          }}

          .stSelectbox label,
          .stMultiSelect label,
          .stTextInput label,
          .stTextArea label,
          .stNumberInput label,
          .stSlider label {{
            color: var(--muted) !important;
            font-size: 11px !important;
            font-weight: 700 !important;
            letter-spacing: 0.06em;
            text-transform: uppercase;
          }}

          .stDataFrame, .stTable {{
            border-radius: 8px;
            overflow: hidden;
          }}

          hr {{
            border-color: var(--border);
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title, subtitle="", badge=None):
    badge_html = ""
    if badge:
        badge_html = f"""
        <span style="
            display:inline-block;
            margin-left:10px;
            padding:2px 8px;
            border-radius:999px;
            border:1px solid {BORDER};
            color:{ACCENT};
            font-size:9px;
            font-weight:800;
            letter-spacing:0.12em;
            text-transform:uppercase;
            vertical-align:middle;
        ">
            {badge}
        </span>
        """

    subtitle_html = ""
    if subtitle:
        subtitle_html = f"""
        <div style="
            margin-top:6px;
            color:{MUTED};
            font-size:11px;
            letter-spacing:0.14em;
            text-transform:uppercase;
        ">
            {subtitle}
        </div>
        """

    st.markdown(
        f"""
        <div style="
            padding: 4px 0 14px 0;
            border-bottom: 1px solid {BORDER};
            margin-bottom: 16px;
        ">
          <div style="
              font-size: 28px;
              font-weight: 900;
              letter-spacing: -0.6px;
              color: {TEXT};
              line-height: 1.1;
          ">
            {title}
            {badge_html}
          </div>
          {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title, subtitle=""):
    subtitle_html = ""
    if subtitle:
        subtitle_html = f"""
        <div style="color:{MUTED}; font-size:11px; margin-top:6px;">
            {subtitle}
        </div>
        """

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(180deg,#0b1220 0%, #0d1526 100%);
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 12px 14px;
            margin-bottom: 12px;
        ">
          <div style="
              color:{TEXT};
              font-size:12px;
              font-weight:800;
              letter-spacing:0.14em;
              text-transform:uppercase;
          ">
            {title}
          </div>
          {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def info_card(title, body):
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(180deg,#0b1220 0%, #0d1526 100%);
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 12px 14px;
            margin-bottom: 12px;
        ">
          <div style="
              color:{TEXT};
              font-size:12px;
              font-weight:800;
              letter-spacing:0.14em;
              text-transform:uppercase;
          ">
            {title}
          </div>
          <div style="
              color:{MUTED};
              font-size:12px;
              line-height:1.75;
              margin-top:8px;
          ">
            {body}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_pill(text, tone="blue"):
    color_map = {
        "blue": ACCENT,
        "green": GREEN,
        "red": RED,
        "yellow": YELLOW,
        "gray": MUTED,
    }
    color = color_map.get(tone, ACCENT)

    return f"""
    <span style="
        display:inline-block;
        padding:2px 8px;
        border-radius:999px;
        border:1px solid {BORDER};
        color:{color};
        font-size:9px;
        font-weight:800;
        letter-spacing:0.12em;
        text-transform:uppercase;
    ">
        {text}
    </span>
    """


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
            padding:8px 12px;
            border-right:1px solid {BORDER};
            min-width:118px;
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
          ">
            {label}
          </span>
          <span style="
              color:{TEXT};
              font-size:13px;
              font-weight:700;
          ">
            {value}
          </span>
          <span style="
              color:{color};
              font-size:11px;
              font-weight:700;
          ">
            {delta}
          </span>
        </div>
        """

    st.markdown(
        f"""
        <div style="
            display:flex;
            flex-wrap:wrap;
            gap:0;
            background: linear-gradient(180deg,#0b1220 0%, #0e1627 100%);
            border:1px solid {BORDER};
            border-radius:8px;
            overflow:hidden;
            margin-bottom:14px;
        ">
          {blocks}
        </div>
        """,
        unsafe_allow_html=True,
    )
