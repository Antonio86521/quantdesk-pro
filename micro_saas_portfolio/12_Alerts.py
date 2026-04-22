"""
12_Alerts.py — QuantDesk Pro
Price alert system: set price thresholds on any ticker,
view triggered/pending alerts, get live status checks.
"""

import streamlit as st
import pandas as pd
import numpy as np
import datetime

from utils import (
    apply_theme, apply_responsive_layout, page_header, section_header,
    ACCENT, ACCENT2, GREEN, RED, AMBER, PURPLE, TEXT2, BG2, BG3, BG4,
    BORDER, app_footer,
)
from data_loader import load_spot_price, load_close_series
from auth import sidebar_user_widget

st.set_page_config(page_title="Alerts — QuantDesk Pro", layout="wide", page_icon="📊")
apply_theme()
apply_responsive_layout()
page_header("Alerts", "Price threshold monitoring · Real-time status · Alert history")
sidebar_user_widget()

# ── Session state ──────────────────────────────────────────────────────────────
if "alerts" not in st.session_state:
    st.session_state["alerts"] = [
        {"id": 1, "ticker": "AAPL", "condition": "Above", "threshold": 230.0,
         "note": "Breakout target", "created": "2026-04-01", "triggered": False},
        {"id": 2, "ticker": "SPY",  "condition": "Below", "threshold": 510.0,
         "note": "Support level watch", "created": "2026-04-05", "triggered": False},
        {"id": 3, "ticker": "NVDA", "condition": "Above", "threshold": 120.0,
         "note": "Momentum entry", "created": "2026-04-10", "triggered": False},
    ]
if "alert_log" not in st.session_state:
    st.session_state["alert_log"] = []

# ── CREATE ALERT ──────────────────────────────────────────────────────────────
section_header("Create New Alert")

col1, col2, col3, col4, col5 = st.columns([1.5, 1, 1.2, 2, 1])
with col1:
    new_ticker = st.text_input("Ticker", placeholder="AAPL", key="alert_ticker").strip().upper()
with col2:
    new_cond   = st.selectbox("Condition", ["Above", "Below", "% Change Up", "% Change Down"])
with col3:
    new_thresh = st.number_input("Threshold ($  or %)", value=100.0, step=0.5)
with col4:
    new_note   = st.text_input("Note (optional)", placeholder="e.g. Breakout target")
with col5:
    st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
    if st.button("＋ Add Alert", use_container_width=True):
        if new_ticker:
            new_id = max([a["id"] for a in st.session_state["alerts"]], default=0) + 1
            st.session_state["alerts"].append({
                "id": new_id,
                "ticker": new_ticker,
                "condition": new_cond,
                "threshold": float(new_thresh),
                "note": new_note.strip(),
                "created": str(datetime.date.today()),
                "triggered": False,
            })
            st.success(f"Alert added: {new_ticker} {new_cond} ${new_thresh:.2f}")
            st.rerun()

st.divider()

# ── CHECK ALERTS ──────────────────────────────────────────────────────────────
section_header("Active Alerts")

if not st.session_state["alerts"]:
    st.markdown(
        f'<div style="background:{BG3};border:1px solid rgba(255,255,255,0.06);'
        f'border-radius:10px;padding:24px;text-align:center;">'
        f'<div style="font-size:22px;margin-bottom:8px;">🔔</div>'
        f'<div style="font-size:13px;font-weight:600;margin-bottom:4px;">No alerts set</div>'
        f'<div style="font-size:12px;color:{TEXT2};">Create an alert above to monitor price levels.</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
else:
    check_btn = st.button("⟳  Check All Prices Now", use_container_width=False)

    for alert in st.session_state["alerts"][:]:
        ticker    = alert["ticker"]
        condition = alert["condition"]
        threshold = alert["threshold"]

        # Fetch current price
        current_price = None
        status        = "Unknown"
        status_colour = TEXT2
        status_badge  = "bl"
        pct_diff      = None

        try:
            if check_btn:
                with st.spinner(f"Checking {ticker}…"):
                    current_price = load_spot_price(ticker, source="auto")
            else:
                # Use cached price
                s = load_close_series(ticker, period="5d", source="auto")
                if s is not None and not s.empty:
                    current_price = float(s.iloc[-1])
        except Exception:
            pass

        if current_price is not None and not np.isnan(current_price):
            if condition == "Above":
                triggered = current_price > threshold
                pct_diff  = (current_price / threshold - 1) * 100
            elif condition == "Below":
                triggered = current_price < threshold
                pct_diff  = (current_price / threshold - 1) * 100
            elif condition == "% Change Up":
                triggered = pct_diff is not None and pct_diff >= threshold
            else:
                triggered = pct_diff is not None and pct_diff <= -threshold

            if triggered:
                status        = "🔴 TRIGGERED"
                status_colour = RED
                status_badge  = "rd"
                alert["triggered"] = True
                log_entry = f"{datetime.datetime.now().strftime('%H:%M')}  {ticker} {condition} ${threshold:.2f}  →  current ${current_price:.2f}"
                if log_entry not in st.session_state["alert_log"]:
                    st.session_state["alert_log"].append(log_entry)
            else:
                status        = "🟢 Monitoring"
                status_colour = GREEN
                status_badge  = "gr"
        else:
            status = "⚠ No data"
            status_badge = "am"

        # Render alert row
        price_str = f"${current_price:,.2f}" if current_price is not None else "—"
        diff_str  = f"{pct_diff:+.1f}% from target" if pct_diff is not None else ""

        r1, r2, r3, r4, r5, r6, r7 = st.columns([1, 1.2, 1.2, 1.2, 1.8, 1.4, 0.8])
        r1.markdown(
            f'<div style="font-family:\'DM Mono\',monospace;font-size:14px;'
            f'font-weight:500;color:#dde4f0;padding-top:8px;">{ticker}</div>',
            unsafe_allow_html=True,
        )
        r2.markdown(
            f'<div style="font-size:12px;color:{TEXT2};padding-top:10px;">'
            f'{condition} <strong style="color:#dde4f0;">${threshold:,.2f}</strong></div>',
            unsafe_allow_html=True,
        )
        r3.markdown(
            f'<div style="font-family:\'DM Mono\',monospace;font-size:14px;'
            f'color:#dde4f0;padding-top:8px;">{price_str}</div>',
            unsafe_allow_html=True,
        )
        r4.markdown(
            f'<div style="font-size:11px;color:{TEXT2};padding-top:10px;">{diff_str}</div>',
            unsafe_allow_html=True,
        )
        r5.markdown(
            f'<div style="font-size:11px;color:{TEXT2};padding-top:10px;">'
            f'{alert["note"] or "—"}</div>',
            unsafe_allow_html=True,
        )
        r6.markdown(
            f'<div style="font-size:12px;color:{status_colour};padding-top:10px;'
            f'font-weight:500;">{status}</div>',
            unsafe_allow_html=True,
        )
        if r7.button("✕", key=f"del_alert_{alert['id']}"):
            st.session_state["alerts"] = [
                a for a in st.session_state["alerts"] if a["id"] != alert["id"]
            ]
            st.rerun()

        st.markdown("<div style='height:1px;background:rgba(255,255,255,0.04);margin:4px 0'></div>",
                    unsafe_allow_html=True)

# ── ALERT LOG ─────────────────────────────────────────────────────────────────
st.divider()
section_header("Alert Log")

if st.session_state["alert_log"]:
    for entry in reversed(st.session_state["alert_log"][-20:]):
        st.markdown(
            f'<div style="background:rgba(246,70,93,0.07);border:1px solid rgba(246,70,93,0.2);'
            f'border-radius:6px;padding:8px 12px;margin-bottom:5px;">'
            f'<div style="font-family:\'DM Mono\',monospace;font-size:11px;color:#f6465d;">'
            f'⚠ {entry}</div></div>',
            unsafe_allow_html=True,
        )
    if st.button("Clear Log"):
        st.session_state["alert_log"] = []
        st.rerun()
else:
    st.markdown(
        f'<div style="font-size:12px;color:{TEXT2};">No alerts have been triggered yet.</div>',
        unsafe_allow_html=True,
    )

st.divider()

# ── QUICK WATCHLIST PRICES ────────────────────────────────────────────────────
section_header("Quick Price Check")

quick_tickers = st.text_input(
    "Tickers to check (comma-separated)",
    value="AAPL,MSFT,NVDA,SPY,QQQ,BTC-USD",
)

if st.button("Fetch Prices", use_container_width=False):
    tickers = [t.strip().upper() for t in quick_tickers.split(",") if t.strip()]
    cols    = st.columns(min(6, len(tickers)))
    for i, t in enumerate(tickers[:6]):
        try:
            s = load_close_series(t, period="5d", source="auto")
            if s is not None and len(s) >= 2:
                last = float(s.iloc[-1])
                prev = float(s.iloc[-2])
                chg  = (last / prev - 1) * 100
                pos  = chg >= 0
                cols[i].metric(t, f"${last:,.2f}", delta=f"{chg:+.2f}%")
            else:
                cols[i].metric(t, "N/A")
        except Exception:
            cols[i].metric(t, "Error")

app_footer()
