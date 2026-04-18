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
      [data-testid="stSidebarNav"] a { color: var(--text) !important; font-size: 11px; font-weight: 700; border-radius: 12px; padding: 0.72rem 0.85rem; margin-bottom: 0.18rem; background: transparent; }
      [data-testid="stSidebarNav"] a:hover { background-color: #0b1a2a; color: var(--text) !important; }
      [data-testid="stSidebarNav"] a[aria-current="page"] { background: linear-gradient(180deg, #0b1d2f 0%, #0a1827 100%); color: var(--accent) !important; border-left: 2px solid var(--accent); }
      [data-testid="stSidebarNav"] a[aria-current="page"] { background: linear-gradient(180deg, #0b1d2f 0%, #0a1827 100%); color: #f6fbff !important; border-left: 2px solid var(--accent); box-shadow: inset 0 0 0 1px rgba(53,194,255,.12); }
      [data-testid="metric-container"], div[data-testid="stMetric"] { background: linear-gradient(180deg, #07111f 0%, #081526 100%); border: 1px solid var(--border); border-radius: 14px; padding: 12px 14px; box-shadow: none; }
      [data-testid="metric-container"] label, div[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 10px !important; letter-spacing: 0.16em; text-transform: uppercase; }
      [data-testid="metric-container"] [data-testid="stMetricValue"], div[data-testid="stMetricValue"] { color: var(--text) !important; font-size: 21px !important; font-weight: 800; font-family: 'Space Mono', monospace !important; }
@@ -144,7 +144,7 @@


def terminal_ribbon(items):
    blocks = ""
    parts = []
    for label, value, delta in items:
        delta_str = str(delta)
        if delta_str.startswith("+"):
@@ -156,17 +156,14 @@
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


        parts.append(
            f'<div class="terminal-ribbon-item">'
            f'<span class="terminal-ribbon-label">{label}</span>'
            f'<span class="terminal-ribbon-value">{value}</span>'
            f'<span class="terminal-ribbon-delta" style="color:{color};background:{bg};padding:2px 8px;border-radius:999px;display:inline-block;">{delta}</span>'
            f'</div>'
        )

    html = '<div class="terminal-ribbon">' + ''.join(parts) + '</div>'
    st.markdown(html, unsafe_allow_html=True)
