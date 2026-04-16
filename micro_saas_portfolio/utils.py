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
