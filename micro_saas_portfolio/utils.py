"""
utils.py — QuantDesk Pro · Elite Design System v3
Complete ground-up rewrite. Every component is built in HTML/CSS
for maximum visual fidelity — no reliance on Streamlit default styling.
"""

from __future__ import annotations

import io
import zipfile
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# COLOUR TOKENS
# ─────────────────────────────────────────────────────────────────────────────
BG      = "#080b10"
BG2     = "#0d1117"
BG3     = "#111820"
BG4     = "#161e2a"
BG5     = "#1c2636"

BORDER  = "rgba(255,255,255,0.055)"
BORDER2 = "rgba(255,255,255,0.10)"
BORDER3 = "rgba(255,255,255,0.16)"

MPL_BORDER = "#1a2535"
MPL_GRID   = "#131d2a"

TEXT    = "#e2eaf6"
TEXT2   = "#6e84a0"
TEXT3   = "#344d68"

ACCENT  = "#2d7ff9"
ACCENT2 = "#5b9ef5"
ACCENT3 = "rgba(45,127,249,0.13)"

GREEN   = "#0ec97d"
GREEN2  = "rgba(14,201,125,0.13)"
RED     = "#f5415a"
RED2    = "rgba(245,65,90,0.13)"
AMBER   = "#f0a500"
AMBER2  = "rgba(240,165,0,0.13)"
PURPLE  = "#7c5cfc"
PURPLE2 = "rgba(124,92,252,0.13)"
TEAL    = "#00c9a7"
MUTED   = TEXT2
ORANGE  = AMBER
YELLOW  = AMBER

PALETTE = [ACCENT, PURPLE, GREEN, AMBER, RED, TEAL, "#e05c3a", ACCENT2]


# ─────────────────────────────────────────────────────────────────────────────
# MASTER THEME
# ─────────────────────────────────────────────────────────────────────────────

def apply_theme() -> None:
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&family=Syne:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

/* ─── RESET & ROOT ──────────────────────────────────────────────────── */
:root {
  --bg:      #080b10;
  --bg2:     #0d1117;
  --bg3:     #111820;
  --bg4:     #161e2a;
  --bg5:     #1c2636;
  --bg6:     #222d3e;
  --b1:  rgba(255,255,255,0.055);
  --b2:  rgba(255,255,255,0.10);
  --b3:  rgba(255,255,255,0.16);
  --text:    #e2eaf6;
  --text2:   #6e84a0;
  --text3:   #344d68;
  --accent:  #2d7ff9;
  --accent2: #5b9ef5;
  --accent3: rgba(45,127,249,0.13);
  --green:   #0ec97d;
  --green2:  rgba(14,201,125,0.13);
  --red:     #f5415a;
  --red2:    rgba(245,65,90,0.13);
  --amber:   #f0a500;
  --purple:  #7c5cfc;
  --teal:    #00c9a7;
  --fd: 'Syne', sans-serif;
  --fb: 'Inter', sans-serif;
  --fm: 'DM Mono', monospace;
  --r:  8px;
  --r2: 12px;
  --r3: 16px;
  --shadow: 0 4px 24px rgba(0,0,0,0.4);
  --shadow-sm: 0 2px 12px rgba(0,0,0,0.3);
  --glow-blue: 0 0 30px rgba(45,127,249,0.18);
}

*, *::before, *::after { box-sizing: border-box; }

html, body {
  font-family: var(--fb);
  background: var(--bg) !important;
  color: var(--text);
  -webkit-font-smoothing: antialiased;
}

/* ─── STREAMLIT WRAPPERS ─────────────────────────────────────────────── */
.stApp, .stApp > div, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
}
.stApp > div > div {
  background: transparent !important;
}
.block-container {
  padding-top: 0.75rem !important;
  padding-bottom: 2rem !important;
  padding-left: 1.5rem !important;
  padding-right: 1.5rem !important;
  max-width: 1340px !important;
}
#MainMenu, footer,
[data-testid="manage-app-button"] { visibility: hidden !important; }
header[data-testid="stHeader"] {
  background: transparent !important;
  border-bottom: none !important;
}

/* ─── SIDEBAR ────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--b1) !important;
}
/* Sidebar collapse/expand button — always on top, always clickable */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
  z-index: 9999 !important;
  visibility: visible !important;
  opacity: 1 !important;
  display: flex !important;
}
section[data-testid="stSidebar"] > div {
  background: transparent !important;
  padding-top: 0 !important;
}
[data-testid="stSidebarNav"] {
  padding: 0 8px !important;
}
[data-testid="stSidebarNav"]::before {
  content: "QD";
  display: flex; align-items: center; justify-content: center;
  width: 36px; height: 36px; border-radius: 10px;
  background: linear-gradient(135deg, #2d7ff9 0%, #7c5cfc 100%);
  color: #fff; font-family: var(--fd); font-size: 14px; font-weight: 800;
  margin: 1.2rem auto 1.4rem;
  box-shadow: 0 0 20px rgba(45,127,249,0.4);
}
[data-testid="stSidebarNav"] ul {
  padding: 0 !important; list-style: none !important;
}
[data-testid="stSidebarNav"] li {
  list-style: none !important; margin: 1px 0 !important;
}
[data-testid="stSidebarNav"] a {
  display: flex !important; align-items: center !important; gap: 9px !important;
  padding: 9px 12px !important; border-radius: var(--r) !important;
  color: var(--text2) !important; font-family: var(--fb) !important;
  font-size: 13px !important; font-weight: 400 !important;
  border: 1px solid transparent !important; transition: all 0.15s ease !important;
  text-decoration: none !important; white-space: nowrap !important;
  opacity: 1 !important; visibility: visible !important;
  position: relative !important; inset: auto !important;
  width: auto !important; height: auto !important;
}
[data-testid="stSidebarNav"] a:hover {
  background: var(--bg3) !important; color: var(--text) !important;
  border-color: var(--b1) !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
  background: var(--accent3) !important; color: var(--accent2) !important;
  border-color: rgba(45,127,249,0.25) !important; font-weight: 500 !important;
}
section[data-testid="stSidebar"] .stMarkdown p {
  color: var(--text3) !important;
  font-size: 9.5px !important; font-weight: 700 !important;
  letter-spacing: 1.2px !important; text-transform: uppercase !important;
  padding: 14px 12px 4px !important; margin: 0 !important;
}
section[data-testid="stSidebar"] .stButton > button {
  background: var(--bg3) !important; border: 1px solid var(--b2) !important;
  border-radius: var(--r) !important; color: var(--text) !important;
  font-size: 12.5px !important; font-weight: 500 !important;
  width: 100% !important; padding: 9px 14px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
  background: var(--bg4) !important; border-color: var(--b3) !important;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
  color: var(--text2) !important; font-size: 12px !important;
  font-weight: 400 !important; text-transform: none !important;
  letter-spacing: 0 !important;
}

/* ─── HEADINGS ────────────────────────────────────────────────────────── */
h1, h2, h3, h4,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4 {
  font-family: var(--fd) !important;
  color: var(--text) !important;
  letter-spacing: -0.4px !important;
  font-weight: 700 !important;
}
[data-testid="stMarkdownContainer"] h1 { font-size: 1.75rem !important; }
[data-testid="stMarkdownContainer"] h2 { font-size: 1.3rem !important; }
[data-testid="stMarkdownContainer"] h3 {
  font-size: 1rem !important;
  margin: 0 0 14px !important;
  padding-bottom: 10px !important;
  border-bottom: 1px solid var(--b1) !important;
}
[data-testid="stMarkdownContainer"] p {
  color: var(--text2);
  font-size: 13px; line-height: 1.65;
}

/* ─── NATIVE METRICS (overridden — we use custom HTML ones mostly) ─── */
[data-testid="metric-container"], div[data-testid="stMetric"] {
  background: var(--bg3) !important;
  border: 1px solid var(--b1) !important;
  border-radius: var(--r2) !important;
  padding: 16px 18px !important;
  transition: border-color 0.15s !important;
}
[data-testid="metric-container"]:hover { border-color: var(--b2) !important; }
div[data-testid="stMetricLabel"] {
  color: var(--text2) !important; font-family: var(--fb) !important;
  font-size: 10.5px !important; font-weight: 500 !important;
  letter-spacing: 0.5px !important; text-transform: uppercase !important;
}
div[data-testid="stMetricValue"] {
  color: var(--text) !important; font-family: var(--fm) !important;
  font-size: 24px !important; font-weight: 400 !important;
  letter-spacing: -0.8px !important; line-height: 1.15 !important;
}
div[data-testid="stMetricDelta"] {
  font-size: 11.5px !important; font-family: var(--fb) !important;
}
div[data-testid="stMetricDelta"] svg { display: none !important; }

/* ─── TABS ───────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg3) !important;
  border: 1px solid var(--b1) !important;
  border-radius: var(--r) !important;
  padding: 3px !important; gap: 2px !important;
  width: fit-content !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important; border: none !important;
  color: var(--text2) !important; font-family: var(--fb) !important;
  font-size: 12px !important; font-weight: 500 !important;
  border-radius: 6px !important; padding: 6px 16px !important;
  transition: all 0.15s !important;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--text) !important; }
.stTabs [aria-selected="true"] {
  background: var(--bg5) !important; color: var(--text) !important;
  box-shadow: var(--shadow-sm) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ─── BUTTONS ────────────────────────────────────────────────────────── */
.stButton > button, .stDownloadButton > button {
  background: var(--bg3) !important; border: 1px solid var(--b2) !important;
  color: var(--text) !important; font-family: var(--fb) !important;
  font-size: 12.5px !important; font-weight: 500 !important;
  border-radius: var(--r) !important; padding: 8px 18px !important;
  transition: all 0.15s ease !important; cursor: pointer !important;
  white-space: nowrap !important;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  background: var(--bg4) !important; border-color: var(--b3) !important;
  transform: translateY(-1px) !important; box-shadow: var(--shadow-sm) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ─── INPUTS ─────────────────────────────────────────────────────────── */
.stTextInput input, .stNumberInput input, textarea,
.stTextArea textarea {
  background: var(--bg4) !important; border: 1px solid var(--b2) !important;
  color: var(--text) !important; border-radius: var(--r) !important;
  font-family: var(--fb) !important; font-size: 13px !important;
  transition: border-color 0.15s !important;
}
.stTextInput input:focus, .stNumberInput input:focus,
textarea:focus, .stTextArea textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(45,127,249,0.12) !important;
  outline: none !important;
}
.stTextInput label, .stNumberInput label,
.stTextArea label, .stSelectbox label {
  color: var(--text2) !important; font-size: 11.5px !important;
  font-weight: 500 !important; letter-spacing: 0.3px !important;
}
div[data-baseweb="select"] > div {
  background: var(--bg4) !important; border: 1px solid var(--b2) !important;
  border-radius: var(--r) !important; color: var(--text) !important;
  font-family: var(--fb) !important; font-size: 13px !important;
}
div[data-baseweb="select"] > div:focus-within {
  border-color: var(--accent) !important;
}
[data-baseweb="popover"] [data-baseweb="menu"] {
  background: var(--bg4) !important; border: 1px solid var(--b2) !important;
  border-radius: var(--r) !important;
}
[data-baseweb="option"]:hover { background: var(--bg5) !important; }

/* ─── SLIDERS ────────────────────────────────────────────────────────── */
[data-testid="stSlider"] > div > div > div {
  background: var(--bg5) !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
  background: var(--accent) !important;
  border: 2px solid var(--accent2) !important;
  box-shadow: 0 0 10px rgba(45,127,249,0.4) !important;
}
[data-testid="stSlider"] [data-testid="stTickBarMin"],
[data-testid="stSlider"] [data-testid="stTickBarMax"] {
  color: var(--text3) !important;
}

/* ─── CHECKBOX & RADIO ───────────────────────────────────────────────── */
[data-testid="stCheckbox"] label,
[data-testid="stRadio"] label,
[data-testid="stCheckbox"] span,
[data-testid="stRadio"] span {
  color: var(--text2) !important; font-size: 12.5px !important;
}

/* ─── DATAFRAMES ─────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
  border: 1px solid var(--b1) !important;
  border-radius: var(--r2) !important;
  overflow: hidden !important;
}
[data-testid="stDataFrame"] th {
  background: var(--bg3) !important; color: var(--text3) !important;
  font-family: var(--fb) !important; font-size: 10.5px !important;
  font-weight: 600 !important; letter-spacing: 0.6px !important;
  text-transform: uppercase !important; padding: 8px 12px !important;
  border-bottom: 1px solid var(--b2) !important;
}
[data-testid="stDataFrame"] td {
  color: var(--text) !important; font-size: 12.5px !important;
  padding: 10px 12px !important;
  border-bottom: 1px solid rgba(255,255,255,0.03) !important;
}
[data-testid="stDataFrame"] tr:hover td {
  background: rgba(255,255,255,0.02) !important;
}

/* ─── EXPANDERS ──────────────────────────────────────────────────────── */
details[data-testid="stExpander"] {
  background: var(--bg3) !important; border: 1px solid var(--b1) !important;
  border-radius: var(--r2) !important; overflow: hidden !important;
}
details[data-testid="stExpander"] summary {
  color: var(--text2) !important; font-family: var(--fb) !important;
  font-size: 12.5px !important; font-weight: 500 !important;
  padding: 12px 16px !important;
}
details[data-testid="stExpander"] summary:hover { color: var(--text) !important; }
details[data-testid="stExpander"] summary svg {
  fill: var(--text3) !important;
}

/* ─── ALERTS ─────────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
  border-radius: var(--r2) !important; font-size: 13px !important;
}
[data-testid="stAlert"][kind="info"] {
  background: rgba(45,127,249,0.08) !important;
  border-color: rgba(45,127,249,0.25) !important;
  color: var(--accent2) !important;
}
[data-testid="stAlert"][kind="success"] {
  background: rgba(14,201,125,0.08) !important;
  border-color: rgba(14,201,125,0.25) !important;
}
[data-testid="stAlert"][kind="warning"] {
  background: rgba(240,165,0,0.08) !important;
  border-color: rgba(240,165,0,0.25) !important;
}
[data-testid="stAlert"][kind="error"] {
  background: rgba(245,65,90,0.08) !important;
  border-color: rgba(245,65,90,0.25) !important;
}

/* ─── SPINNER ────────────────────────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* ─── CAPTIONS ───────────────────────────────────────────────────────── */
[data-testid="stCaptionContainer"] p {
  color: var(--text3) !important; font-size: 11px !important;
}

/* ─── HR / DIVIDER ───────────────────────────────────────────────────── */
hr, [data-testid="stDivider"] {
  border-color: var(--b1) !important;
  margin: 24px 0 !important;
}

/* ─── PAGE LINKS ─────────────────────────────────────────────────────── */
div[data-testid="stPageLink"] a {
  display: inline-flex !important; align-items: center !important;
  padding: 7px 14px !important; border-radius: var(--r) !important;
  background: var(--bg3) !important; border: 1px solid var(--b2) !important;
  color: var(--text2) !important; font-size: 12.5px !important;
  font-weight: 500 !important; text-decoration: none !important;
  transition: all 0.15s !important;
}
div[data-testid="stPageLink"] a:hover {
  background: var(--bg4) !important; border-color: var(--accent) !important;
  color: var(--accent2) !important;
}

/* ─── PROGRESS ───────────────────────────────────────────────────────── */
[data-testid="stProgress"] > div > div {
  background: var(--bg4) !important;
}
[data-testid="stProgress"] > div > div > div {
  background: linear-gradient(90deg, var(--accent), var(--purple)) !important;
  border-radius: 4px !important;
}

/* ─── SCROLLBAR ──────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--bg5); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--bg6); }

/* ─── DESIGN SYSTEM COMPONENTS ───────────────────────────────────────── */

/* Metric card */
.qd-metric {
  background: var(--bg3); border: 1px solid var(--b1);
  border-radius: var(--r2); padding: 16px 18px;
  transition: border-color 0.15s, transform 0.15s;
}
.qd-metric:hover { border-color: var(--b2); transform: translateY(-1px); }
.qd-metric-label {
  font-family: var(--fb); font-size: 10.5px; color: var(--text2);
  font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase;
  margin-bottom: 8px;
}
.qd-metric-value {
  font-family: var(--fm); font-size: 26px; font-weight: 400;
  color: var(--text); letter-spacing: -1px; line-height: 1;
}
.qd-metric-delta {
  font-size: 11.5px; margin-top: 6px; font-family: var(--fb);
}
.qd-metric-delta.up { color: var(--green); }
.qd-metric-delta.dn { color: var(--red); }
.qd-metric-delta.nu { color: var(--text2); }

/* Card */
.qd-card {
  background: var(--bg2); border: 1px solid var(--b1);
  border-radius: var(--r3); padding: 18px 20px;
}
.qd-card-hd {
  display: flex; align-items: flex-start;
  justify-content: space-between; margin-bottom: 16px; gap: 12px;
}
.qd-card-title {
  font-family: var(--fd); font-size: 13.5px; font-weight: 600;
  color: var(--text); letter-spacing: -0.2px;
}
.qd-card-sub { font-size: 11px; color: var(--text2); margin-top: 3px; }

/* Page header */
.pg-hd {
  display: flex; align-items: flex-start; justify-content: space-between;
  padding-bottom: 18px; margin-bottom: 22px;
  border-bottom: 1px solid var(--b1);
}
.pg-hd-left {}
.pg-hd-title {
  font-family: var(--fd) !important; font-size: 24px !important;
  font-weight: 700 !important; color: var(--text) !important;
  letter-spacing: -0.5px !important; line-height: 1.2 !important;
}
.pg-hd-sub {
  font-size: 12.5px; color: var(--text2); margin-top: 5px;
  font-family: var(--fb);
}
.pg-hd-badge {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 4px 10px; border-radius: 5px; font-size: 10.5px;
  font-weight: 600; letter-spacing: 0.3px; white-space: nowrap;
  background: var(--accent3); color: var(--accent2);
  border: 1px solid rgba(45,127,249,0.2);
}

/* Section header */
.qd-section {
  font-family: var(--fb); font-size: 10px; color: var(--text3);
  font-weight: 700; letter-spacing: 1.4px; text-transform: uppercase;
  margin: 26px 0 12px;
  display: flex; align-items: center; gap: 10px;
}
.qd-section::after {
  content: ''; flex: 1; height: 1px;
  background: var(--b1);
}

/* Badge */
.qd-badge {
  display: inline-flex; align-items: center;
  padding: 2px 8px; border-radius: 4px;
  font-size: 10.5px; font-weight: 500; white-space: nowrap;
}
.qd-badge-bl { background: var(--accent3); color: var(--accent2); }
.qd-badge-gr { background: var(--green2); color: var(--green); }
.qd-badge-rd { background: var(--red2); color: var(--red); }
.qd-badge-am { background: var(--amber2); color: var(--amber); }
.qd-badge-pu { background: var(--purple2); color: var(--purple); }
.qd-badge-tl { background: rgba(0,201,167,0.13); color: var(--teal); }

/* Stat row (horizontal key-value) */
.qd-stat-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 0; border-bottom: 1px solid var(--b1);
}
.qd-stat-row:last-child { border-bottom: none; padding-bottom: 0; }
.qd-stat-label { font-size: 12.5px; color: var(--text2); }
.qd-stat-value { font-family: var(--fm); font-size: 13px; color: var(--text); }

/* Table */
.qd-table { width: 100%; border-collapse: collapse; }
.qd-table th {
  text-align: left; padding: 8px 12px;
  font-size: 10px; color: var(--text3); font-weight: 700;
  letter-spacing: 0.8px; text-transform: uppercase;
  border-bottom: 1px solid var(--b2); white-space: nowrap;
}
.qd-table td {
  padding: 11px 12px; font-size: 12.5px; color: var(--text);
  border-bottom: 1px solid rgba(255,255,255,0.028);
}
.qd-table tr:hover td { background: rgba(255,255,255,0.02); }
.qd-table tr:last-child td { border-bottom: none; }
.qd-table .mono { font-family: var(--fm); font-size: 12px; }
.qd-table .dim { color: var(--text2); font-size: 11px; }
.qd-table .up { color: var(--green); }
.qd-table .dn { color: var(--red); }

/* Spark bars */
.qd-spark {
  display: flex; align-items: flex-end; gap: 2px; height: 28px;
}
.qd-spark-bar {
  flex: 1; border-radius: 2px 2px 0 0; min-width: 3px;
}

/* Pill/Tag */
.qd-pill {
  display: inline-block; padding: 3px 9px; border-radius: 20px;
  font-size: 10.5px; font-weight: 600; letter-spacing: 0.2px;
}

/* Gauge bar */
.qd-gauge {
  height: 5px; border-radius: 3px; background: var(--bg5);
  overflow: hidden; position: relative;
}
.qd-gauge-fill {
  height: 100%; border-radius: 3px;
  background: linear-gradient(90deg, var(--accent), var(--purple));
}

/* Footer */
.qd-footer {
  margin-top: 48px; padding-top: 16px;
  border-top: 1px solid var(--b1);
  display: flex; justify-content: space-between;
  align-items: center; flex-wrap: wrap; gap: 12px;
  font-size: 11px; color: var(--text3);
  font-family: var(--fb);
}
.qd-footer a { color: var(--text2); text-decoration: none; }
.qd-footer a:hover { color: var(--accent2); }

/* Chart wrapper */
.qd-chart-wrap {
  background: var(--bg2); border: 1px solid var(--b1);
  border-radius: var(--r2); padding: 4px;
  overflow: hidden;
}
.qd-chart-hd {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px 8px;
}
.qd-chart-title {
  font-family: var(--fd); font-size: 13px; font-weight: 600; color: var(--text);
}
.qd-chart-sub { font-size: 11px; color: var(--text2); margin-top: 2px; }

/* Wl item */
.qd-wl {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px; background: var(--bg3); border-radius: var(--r);
  margin-bottom: 5px; border: 1px solid transparent;
  cursor: pointer; transition: border-color 0.14s;
}
.qd-wl:hover { border-color: var(--b2); }
.qd-wl-sym {
  font-family: var(--fm); font-size: 13.5px; font-weight: 500; color: var(--text);
}
.qd-wl-name { font-size: 10.5px; color: var(--text2); margin-top: 1px; }
.qd-wl-price { font-family: var(--fm); font-size: 14px; text-align: right; color: var(--text); }
.qd-wl-chg { font-size: 11px; text-align: right; margin-top: 2px; }

/* Empty state */
.qd-empty {
  text-align: center; padding: 40px 24px;
  background: var(--bg3); border: 1px solid var(--b1);
  border-radius: var(--r3);
}
.qd-empty-icon { font-size: 28px; margin-bottom: 12px; opacity: 0.6; }
.qd-empty-title {
  font-family: var(--fd); font-size: 15px; font-weight: 600;
  color: var(--text); margin-bottom: 6px;
}
.qd-empty-body { font-size: 13px; color: var(--text2); line-height: 1.6; }

/* Two-column layout helper */
.qd-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.qd-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.qd-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
</style>
""", unsafe_allow_html=True)

    # ── Matplotlib ──────────────────────────────────────────────────────────────
    _T  = "#8ba3bd"
    _T2 = "#c8d8e8"
    _BG = "#080b10"
    _S  = "#0d1117"

    plt.rcParams.update({
        "figure.facecolor":            _BG,
        "axes.facecolor":              _S,
        "axes.edgecolor":              "#1a2535",
        "axes.labelcolor":             _T,
        "axes.labelsize":              10,
        "axes.labelpad":               6,
        "axes.titlesize":              11.5,
        "axes.titleweight":            "600",
        "axes.titlecolor":             _T2,
        "axes.titlepad":               10,
        "axes.spines.top":             False,
        "axes.spines.right":           False,
        "axes.spines.left":            True,
        "axes.spines.bottom":          True,
        "axes.prop_cycle":             plt.cycler("color", [
            "#2d7ff9","#7c5cfc","#0ec97d","#f0a500",
            "#f5415a","#00c9a7","#e05c3a","#5b9ef5",
        ]),
        "xtick.color":                 _T,
        "ytick.color":                 _T,
        "xtick.labelsize":             9,
        "ytick.labelsize":             9,
        "xtick.major.pad":             5,
        "ytick.major.pad":             5,
        "text.color":                  _T2,
        "grid.color":                  MPL_GRID,
        "grid.linewidth":              0.5,
        "grid.linestyle":              "--",
        "grid.alpha":                  0.6,
        "lines.linewidth":             2.0,
        "lines.solid_capstyle":        "round",
        "patch.edgecolor":             _BG,
        "patch.linewidth":             0,
        "legend.facecolor":            "#111820",
        "legend.edgecolor":            "#1a2535",
        "legend.labelcolor":           _T2,
        "legend.fontsize":             9.5,
        "legend.framealpha":           0.9,
        "legend.borderpad":            0.6,
        "legend.labelspacing":         0.4,
        "figure.dpi":                  115,
        "figure.autolayout":           True,
        "savefig.facecolor":           _BG,
        "savefig.edgecolor":           "none",
    })


def apply_responsive_layout() -> None:
    st.markdown("""
<style>
/* Sidebar always visible */
section[data-testid="stSidebar"] {
  min-width: 220px !important;
}
section[data-testid="stSidebar"] * {
  visibility: visible !important;
}
[data-testid="stSidebarNav"] a {
  opacity: 1 !important;
  visibility: visible !important;
  position: relative !important;
  inset: auto !important;
}

/* Page link buttons — always visible and styled */
div[data-testid="stPageLink"] a {
  opacity: 1 !important;
  visibility: visible !important;
  position: relative !important;
  inset: auto !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 100% !important;
  padding: 8px 12px !important;
  background: rgba(45,127,249,0.08) !important;
  border: 1px solid rgba(45,127,249,0.2) !important;
  border-radius: 8px !important;
  color: #5b9ef5 !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  text-decoration: none !important;
  transition: all 0.15s !important;
  margin-top: 6px !important;
}
div[data-testid="stPageLink"] a:hover {
  background: rgba(45,127,249,0.15) !important;
  border-color: rgba(45,127,249,0.4) !important;
  color: #7cb8ff !important;
}
div[data-testid="stPageLink"] { margin: 0 !important; }

@media (max-width: 900px) {
  .block-container {
    padding-left: 0.9rem !important;
    padding-right: 0.9rem !important;
  }
  .qd-grid-2, .qd-grid-3, .qd-grid-4 {
    grid-template-columns: 1fr !important;
  }
}
@media (max-width: 600px) {
  div[data-baseweb="select"] > div,
  .stTextInput input, .stNumberInput input, textarea {
    font-size: 16px !important;
  }
  .block-container {
    padding-left: 0.6rem !important;
    padding-right: 0.6rem !important;
  }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# COMPONENT HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def page_header(title: str, subtitle: str = "", badge: str = "") -> None:
    """Render the top-of-page header bar."""
    sub_html   = f'<div class="pg-hd-sub">{subtitle}</div>' if subtitle else ""
    badge_html = f'<div class="pg-hd-badge">{badge}</div>' if badge else ""
    st.markdown(f"""
<div class="pg-hd">
  <div class="pg-hd-left">
    <div class="pg-hd-title">{title}</div>
    {sub_html}
  </div>
  {badge_html}
</div>""", unsafe_allow_html=True)


def section_header(title: str) -> None:
    """Apex-style ALL-CAPS section divider label."""
    st.markdown(
        f'<div class="qd-section">{title}</div>',
        unsafe_allow_html=True,
    )


def metric_row(metrics: list[dict]) -> None:
    """
    Render a row of rich metric cards.
    Each dict: {label, value, delta?, delta_pos?}
    delta_pos: True=green, False=red, None=neutral
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        delta_html = ""
        if m.get("delta"):
            cls = "up" if m.get("delta_pos") is True else ("dn" if m.get("delta_pos") is False else "nu")
            delta_html = f'<div class="qd-metric-delta {cls}">{m["delta"]}</div>'
        sub_html = f'<div class="qd-metric-sub" style="font-size:11px;color:#6e84a0;margin-top:4px;">{m["sub"]}</div>' if m.get("sub") else ""
        col.markdown(f"""
<div class="qd-metric">
  <div class="qd-metric-label">{m["label"]}</div>
  <div class="qd-metric-value">{m["value"]}</div>
  {delta_html}{sub_html}
</div>""", unsafe_allow_html=True)


def stat_table(rows: list[tuple], cols: int = 2) -> None:
    """Render a compact key-value stat table in `cols` columns."""
    n = len(rows)
    per_col = (n + cols - 1) // cols
    chunks  = [rows[i:i+per_col] for i in range(0, n, per_col)]
    st_cols = st.columns(len(chunks))
    for st_col, chunk in zip(st_cols, chunks):
        html = '<div>'
        for label, value, *rest in chunk:
            color = ""
            if rest:
                v = rest[0]
                if v is True:   color = f"color:{GREEN}"
                elif v is False: color = f"color:{RED}"
            html += f"""
<div class="qd-stat-row">
  <span class="qd-stat-label">{label}</span>
  <span class="qd-stat-value" style="{color}">{value}</span>
</div>"""
        html += '</div>'
        st_col.markdown(html, unsafe_allow_html=True)


def badge(text: str, variant: str = "bl") -> str:
    cls = f"qd-badge qd-badge-{variant}"
    return f'<span class="{cls}">{text}</span>'


def empty_state(icon: str, title: str, body: str) -> None:
    st.markdown(f"""
<div class="qd-empty">
  <div class="qd-empty-icon">{icon}</div>
  <div class="qd-empty-title">{title}</div>
  <div class="qd-empty-body">{body}</div>
</div>""", unsafe_allow_html=True)


def chart_card(title: str, subtitle: str = "", badge_text: str = "") -> None:
    """Output the header for a chart card. Call before st.pyplot()."""
    badge_html = f'<span class="qd-badge qd-badge-bl" style="margin-left:auto">{badge_text}</span>' if badge_text else ""
    st.markdown(f"""
<div class="qd-chart-wrap">
  <div class="qd-chart-hd">
    <div>
      <div class="qd-chart-title">{title}</div>
      {'<div class="qd-chart-sub">'+subtitle+'</div>' if subtitle else ''}
    </div>
    {badge_html}
  </div>""", unsafe_allow_html=True)


def chart_card_close() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def info_panel(title: str, body: str, variant: str = "bl") -> None:
    color_map = {
        "bl": (ACCENT3, ACCENT2), "gr": (GREEN2, GREEN),
        "rd": (RED2, RED),        "am": (AMBER2, AMBER),
    }
    bg, clr = color_map.get(variant, color_map["bl"])
    st.markdown(f"""
<div style="background:{bg};border:1px solid {clr}33;border-radius:10px;padding:14px 16px;margin:8px 0;">
  <div style="font-family:'Syne',sans-serif;font-size:12px;font-weight:600;
              color:{clr};margin-bottom:4px;">{title}</div>
  <div style="font-size:12.5px;color:#8ba3bd;line-height:1.6;">{body}</div>
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PLAN HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_active_plan() -> str:
    return st.session_state.get("active_plan", "free")

def is_pro() -> bool:
    return get_active_plan() == "pro"

def premium_notice(feature_name: str = "this feature") -> None:
    info_panel("Pro Feature", f"{feature_name} is available on the Pro plan.", "am")


# ─────────────────────────────────────────────────────────────────────────────
# DOWNLOAD / EXPORT
# ─────────────────────────────────────────────────────────────────────────────

def make_download_zip(file_map: Dict[str, "pd.DataFrame | str"]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, obj in file_map.items():
            zf.writestr(name, obj.to_csv(index=True) if isinstance(obj, pd.DataFrame) else str(obj))
    buf.seek(0)
    return buf.getvalue()

def html_report(title: str, sections: List[Tuple[str, str]]) -> str:
    body = "".join(
        f"<section style='margin-bottom:28px;'>"
        f"<h2 style='font-family:Inter,sans-serif;font-size:15px;color:#0f172a;border-bottom:1px solid #e2e8f0;padding-bottom:8px;margin-bottom:12px;'>{hdr}</h2>"
        f"<div style='font-family:Inter,sans-serif;font-size:13px;color:#334155;line-height:1.7'>{content}</div>"
        f"</section>"
        for hdr, content in sections
    )
    return f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'>
<title>{title}</title>
<style>body{{font-family:Inter,sans-serif;background:#f1f5f9;margin:0;padding:36px;}}
.wrap{{max-width:1000px;margin:0 auto;background:#fff;border:1px solid #cbd5e1;
border-radius:16px;padding:36px;box-shadow:0 4px 24px rgba(0,0,0,0.06);}}
h1{{font-size:22px;color:#0f172a;margin-top:0;border-bottom:2px solid #e2e8f0;padding-bottom:14px;margin-bottom:24px;}}
table{{width:100%;border-collapse:collapse;font-size:12px;}}
th{{background:#f8fafc;text-align:left;padding:8px 12px;color:#64748b;font-weight:600;border-bottom:1px solid #e2e8f0;}}
td{{padding:8px 12px;border-bottom:1px solid #f1f5f9;}}</style>
</head><body><div class='wrap'><h1>{title}</h1>{body}</div></body></html>"""


# ─────────────────────────────────────────────────────────────────────────────
# FORMATTERS
# ─────────────────────────────────────────────────────────────────────────────

def safe_pct(value: float, decimals: int = 2) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "—"
    return f"{value:.{decimals}%}"

def safe_num(value: float, decimals: int = 2) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "—"
    return f"{value:.{decimals}f}"

def fmt_dollar(value: float) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "—"
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"${value:,.0f}"
    return f"${value:.2f}"

def colour_pct(value: float, decimals: int = 2) -> str:
    """Return coloured HTML span for a percentage."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return '<span style="color:#344d68">—</span>'
    clr = GREEN if value >= 0 else RED
    sign = "+" if value >= 0 else ""
    return f'<span style="color:{clr};font-family:\'DM Mono\',monospace;font-size:12px;">{sign}{value:.{decimals}f}%</span>'


# ─────────────────────────────────────────────────────────────────────────────
# GLOSSARY
# ─────────────────────────────────────────────────────────────────────────────

METRIC_EXPLANATIONS: Dict[str, str] = {
    "Portfolio Value":    "Current market value of all holdings at latest prices.",
    "Invested Capital":   "Total originally paid for all positions.",
    "Unrealized P&L":     "Mark-to-market gain/loss if all positions were closed now.",
    "Total Return":       "Overall percentage gain/loss over the selected period.",
    "Ann. Return":        "Annualised return estimated from daily returns.",
    "Ann. Volatility":    "Annualised standard deviation of daily returns.",
    "Sharpe Ratio":       "Excess return per unit of volatility.",
    "Sortino":            "Return per unit of downside volatility only.",
    "Calmar":             "Annualised return divided by absolute max drawdown.",
    "Max Drawdown":       "Largest peak-to-trough decline over the selected period.",
    "Beta":               "Sensitivity of portfolio returns to benchmark moves.",
    "Alpha":              "Excess return above what benchmark exposure would predict.",
    "Historical VaR 95%": "Daily loss threshold exceeded only 5% of the time.",
    "CVaR 95%":           "Average loss during the worst 5% of days.",
    "R²":                 "Fraction of return variation explained by the benchmark.",
    "Tracking Error":     "Volatility of the portfolio's active return vs benchmark.",
    "Information Ratio":  "Active return divided by tracking error.",
    "Omega":              "Ratio of gains to losses above a threshold.",
    "Gain/Pain":          "Total gains divided by total absolute losses.",
}

def explain_metric(name: str) -> None:
    text = METRIC_EXPLANATIONS.get(name)
    if text:
        st.caption(text)

def glossary_expander(title: str, items: Dict[str, str]) -> None:
    with st.expander(title):
        for key, value in items.items():
            st.markdown(f"**{key}** — {value}")


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────

def app_footer() -> None:
    st.markdown("""
<div class="qd-footer">
  <div style="display:flex;gap:6px;align-items:center;">
    <span style="width:22px;height:22px;border-radius:6px;background:linear-gradient(135deg,#2d7ff9,#7c5cfc);
                 display:inline-flex;align-items:center;justify-content:center;
                 font-family:'Syne',sans-serif;font-size:9px;font-weight:800;color:#fff;">QD</span>
    <span style="color:#6e84a0;">QuantDesk Pro &nbsp;·&nbsp; © 2026</span>
    <span style="color:#344d68;">&nbsp;|&nbsp;</span>
    <a href="#">Docs</a>
    <a href="#">Privacy</a>
    <a href="#">Terms</a>
  </div>
  <div style="color:#344d68;font-size:10.5px;">
    Educational use only &nbsp;·&nbsp; Not investment advice &nbsp;·&nbsp;
    Data via yfinance &amp; Alpha Vantage
  </div>
</div>""", unsafe_allow_html=True)
