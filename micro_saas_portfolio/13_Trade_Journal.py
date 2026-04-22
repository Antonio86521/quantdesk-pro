"""
13_Trade_Journal.py — QuantDesk Pro
Professional trade journal: log entries, P&L tracking, 
performance statistics, win rate, payoff ratio, equity curve.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

from utils import (
    apply_theme, apply_responsive_layout, page_header, section_header,
    ACCENT, ACCENT2, GREEN, RED, AMBER, PURPLE, TEXT2, BG2, BG3, BG4,
    MPL_BORDER, MPL_GRID, PALETTE, app_footer, safe_pct, safe_num,
)
from auth import sidebar_user_widget

st.set_page_config(page_title="Trade Journal — QuantDesk Pro", layout="wide", page_icon="📊")
apply_theme()
apply_responsive_layout()
page_header("Trade Journal", "Log trades · Track P&L · Analyse performance")
sidebar_user_widget()

# ── Session state ──────────────────────────────────────────────────────────────
if "trades" not in st.session_state:
    st.session_state["trades"] = [
        {"id": 1, "date": "2026-01-15", "ticker": "AAPL", "direction": "Long",
         "entry": 182.50, "exit": 198.30, "shares": 50, "sector": "Technology",
         "setup": "Breakout", "notes": "Above 200 SMA, strong volume"},
        {"id": 2, "date": "2026-01-28", "ticker": "MSFT", "direction": "Long",
         "entry": 378.00, "exit": 412.50, "shares": 20, "sector": "Technology",
         "setup": "Earnings Play", "notes": "Beat on revenue, guidance raised"},
        {"id": 3, "date": "2026-02-10", "ticker": "NVDA", "direction": "Long",
         "entry": 780.00, "exit": 742.00, "shares": 15, "sector": "Technology",
         "setup": "Momentum", "notes": "Stopped out, sector rotation"},
        {"id": 4, "date": "2026-02-22", "ticker": "SPY", "direction": "Short",
         "entry": 545.00, "exit": 521.00, "shares": 30, "sector": "Index",
         "setup": "Macro Hedge", "notes": "Rate hike fear, took profit"},
        {"id": 5, "date": "2026-03-05", "ticker": "GOOGL", "direction": "Long",
         "entry": 162.00, "exit": 175.50, "shares": 40, "sector": "Technology",
         "setup": "Value", "notes": "AI monetisation thesis"},
        {"id": 6, "date": "2026-03-18", "ticker": "GLD", "direction": "Long",
         "entry": 220.50, "exit": 238.90, "shares": 60, "sector": "Commodities",
         "setup": "Safe Haven", "notes": "Dollar weakness, geopolitical risk"},
        {"id": 7, "date": "2026-04-02", "ticker": "TSLA", "direction": "Long",
         "entry": 198.00, "exit": 186.00, "shares": 25, "sector": "Consumer",
         "setup": "Momentum", "notes": "Failed breakout, cut loss"},
        {"id": 8, "date": "2026-04-14", "ticker": "META", "direction": "Long",
         "entry": 501.00, "exit": 548.00, "shares": 18, "sector": "Technology",
         "setup": "Earnings Play", "notes": "Ad revenue beat, raised guidance"},
    ]

# ── LOG NEW TRADE ──────────────────────────────────────────────────────────────
section_header("Log New Trade")

with st.expander("＋ Add Trade Entry", expanded=False):
    c1,c2,c3,c4 = st.columns(4)
    t_date  = c1.date_input("Date", value=datetime.date.today())
    t_tick  = c2.text_input("Ticker", placeholder="AAPL").strip().upper()
    t_dir   = c3.selectbox("Direction", ["Long", "Short"])
    t_sec   = c4.selectbox("Sector", ["Technology","Financials","Healthcare","Energy",
                                        "Consumer","Industrials","Commodities","Index","Other"])
    c5,c6,c7,c8 = st.columns(4)
    t_entry  = c5.number_input("Entry Price ($)", min_value=0.01, value=100.0, step=0.01)
    t_exit   = c6.number_input("Exit Price ($)",  min_value=0.01, value=105.0, step=0.01)
    t_shares = c7.number_input("Shares / Qty",    min_value=1,    value=100,   step=1)
    t_setup  = c8.selectbox("Setup Type", ["Breakout","Momentum","Earnings Play",
                                             "Value","Macro Hedge","Mean Reversion",
                                             "Swing","Safe Haven","Other"])
    t_notes = st.text_area("Notes / Rationale", height=70, placeholder="Entry thesis, market conditions…")

    if st.button("Save Trade", use_container_width=False):
        if t_tick:
            new_id = max([t["id"] for t in st.session_state["trades"]], default=0) + 1
            st.session_state["trades"].append({
                "id": new_id, "date": str(t_date), "ticker": t_tick,
                "direction": t_dir, "entry": float(t_entry), "exit": float(t_exit),
                "shares": int(t_shares), "sector": t_sec, "setup": t_setup,
                "notes": t_notes.strip(),
            })
            st.success(f"Trade logged: {t_dir} {t_tick}")
            st.rerun()

# ── BUILD DATAFRAME ────────────────────────────────────────────────────────────
trades = st.session_state["trades"]
if not trades:
    st.info("No trades logged yet. Add your first trade above.")
    st.stop()

df = pd.DataFrame(trades)
df["date"]    = pd.to_datetime(df["date"])
df["pnl_pts"] = np.where(df["direction"] == "Long",
                          df["exit"] - df["entry"],
                          df["entry"] - df["exit"])
df["pnl_$"]   = df["pnl_pts"] * df["shares"]
df["pnl_%"]   = df["pnl_pts"] / df["entry"] * 100
df["win"]     = df["pnl_$"] > 0
df = df.sort_values("date")
df["equity_curve"] = df["pnl_$"].cumsum()

# ── PERFORMANCE STATS ──────────────────────────────────────────────────────────
section_header("Performance Summary")

total_pnl    = df["pnl_$"].sum()
win_rate     = df["win"].mean() * 100
avg_win      = df.loc[df["win"],  "pnl_$"].mean() if df["win"].any()  else 0
avg_loss     = df.loc[~df["win"], "pnl_$"].mean() if (~df["win"]).any() else 0
payoff_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else np.nan
profit_factor = (df.loc[df["win"],  "pnl_$"].sum() /
                 abs(df.loc[~df["win"],"pnl_$"].sum())
                 if df.loc[~df["win"],"pnl_$"].sum() != 0 else np.nan)
avg_pnl      = df["pnl_$"].mean()
best_trade   = df["pnl_$"].max()
worst_trade  = df["pnl_$"].min()
n_trades     = len(df)
largest_win  = df.loc[df["pnl_$"].idxmax(), "ticker"] if n_trades else "—"
largest_loss = df.loc[df["pnl_$"].idxmin(), "ticker"] if n_trades else "—"

r1 = st.columns(5)
r1[0].metric("Total P&L",      f"${total_pnl:,.0f}", delta=f"{'+' if total_pnl >= 0 else ''}{total_pnl:,.0f}")
r1[1].metric("Win Rate",       f"{win_rate:.1f}%")
r1[2].metric("Payoff Ratio",   safe_num(payoff_ratio))
r1[3].metric("Profit Factor",  safe_num(profit_factor))
r1[4].metric("Total Trades",   str(n_trades))

r2 = st.columns(5)
r2[0].metric("Avg Trade P&L",  f"${avg_pnl:,.0f}")
r2[1].metric("Avg Win",        f"${avg_win:,.0f}")
r2[2].metric("Avg Loss",       f"${avg_loss:,.0f}")
r2[3].metric("Best Trade",     f"${best_trade:,.0f}  ({largest_win})")
r2[4].metric("Worst Trade",    f"${worst_trade:,.0f}  ({largest_loss})")

st.divider()

# ── CHARTS ─────────────────────────────────────────────────────────────────────
section_header("Equity Curve & Analytics")

left_col, right_col = st.columns([1.6, 1])

with left_col:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6),
                                    gridspec_kw={"height_ratios": [2.5, 1]})
    # Equity curve
    ax1.plot(df["date"], df["equity_curve"], color=ACCENT, lw=2, zorder=3)
    ax1.fill_between(df["date"], df["equity_curve"], 0,
                     where=df["equity_curve"] >= 0, alpha=0.12, color=GREEN)
    ax1.fill_between(df["date"], df["equity_curve"], 0,
                     where=df["equity_curve"] < 0, alpha=0.12, color=RED)
    ax1.axhline(0, color="#3d5068", lw=0.8, ls="--")
    ax1.set_title("Cumulative P&L Equity Curve")
    ax1.set_ylabel("Cumulative P&L ($)")
    ax1.grid(True, alpha=0.2)

    # Individual trade P&L bars
    colors = [GREEN if v >= 0 else RED for v in df["pnl_$"]]
    ax2.bar(range(len(df)), df["pnl_$"], color=colors, edgecolor="#0d1117", width=0.7)
    ax2.axhline(0, color="#3d5068", lw=0.8, ls="--")
    ax2.set_title("Individual Trade P&L")
    ax2.set_ylabel("P&L ($)")
    ax2.set_xticks(range(len(df)))
    ax2.set_xticklabels(df["ticker"], rotation=45, ha="right", fontsize=8)
    ax2.grid(True, alpha=0.2, axis="y")

    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

with right_col:
    # Win/Loss donut
    wins   = df["win"].sum()
    losses = n_trades - wins
    fig2, ax3 = plt.subplots(figsize=(4, 3.5))
    ax3.pie([wins, losses],
            labels=[f"Wins ({wins})", f"Losses ({losses})"],
            colors=[GREEN, RED],
            autopct="%1.0f%%", startangle=90,
            wedgeprops=dict(edgecolor="#0d1117", linewidth=2))
    ax3.set_title("Win / Loss Split")
    st.pyplot(fig2, use_container_width=True)
    plt.close()

    # P&L by sector
    sector_pnl = df.groupby("sector")["pnl_$"].sum().sort_values()
    if not sector_pnl.empty:
        fig3, ax4 = plt.subplots(figsize=(4, max(2.5, len(sector_pnl) * 0.4)))
        colors_s = [GREEN if v >= 0 else RED for v in sector_pnl.values]
        ax4.barh(sector_pnl.index, sector_pnl.values, color=colors_s, edgecolor="#0d1117", height=0.6)
        ax4.axvline(0, color="#3d5068", lw=0.8, ls="--")
        ax4.set_title("P&L by Sector")
        ax4.grid(True, alpha=0.2, axis="x")
        st.pyplot(fig3, use_container_width=True)
        plt.close()

    # Setup breakdown
    setup_pnl = df.groupby("setup")["pnl_$"].sum().sort_values(ascending=False)
    if not setup_pnl.empty:
        fig4, ax5 = plt.subplots(figsize=(4, max(2.5, len(setup_pnl) * 0.4)))
        colors_sp = [GREEN if v >= 0 else RED for v in setup_pnl.values]
        ax5.barh(setup_pnl.index, setup_pnl.values, color=colors_sp, edgecolor="#0d1117", height=0.6)
        ax5.axvline(0, color="#3d5068", lw=0.8, ls="--")
        ax5.set_title("P&L by Setup Type")
        ax5.grid(True, alpha=0.2, axis="x")
        st.pyplot(fig4, use_container_width=True)
        plt.close()

st.divider()

# ── TRADE LOG TABLE ────────────────────────────────────────────────────────────
section_header("Trade Log")

filter_dir = st.selectbox("Filter direction", ["All", "Long", "Short"])
disp = df if filter_dir == "All" else df[df["direction"] == filter_dir]

display_cols = ["date","ticker","direction","entry","exit","shares","pnl_$","pnl_%","setup","sector"]
styled = disp[display_cols].copy()
styled["date"] = styled["date"].dt.strftime("%Y-%m-%d")

def highlight_pnl(row):
    out = []
    for col in row.index:
        if col in ["pnl_$","pnl_%"]:
            out.append(f"color: {'#0ecb81' if row[col] >= 0 else '#f6465d'}")
        else:
            out.append("")
    return out

st.dataframe(
    styled.style
    .format({"entry": "${:.2f}", "exit": "${:.2f}", "pnl_$": "${:+,.0f}", "pnl_%": "{:+.2f}%"})
    .apply(highlight_pnl, axis=1),
    use_container_width=True, hide_index=True,
)

# Export
csv = disp[display_cols].to_csv(index=False).encode()
st.download_button("⬇ Export Journal CSV", csv, "trade_journal.csv", "text/csv")

st.divider()

# ── NOTES / LESSONS LEARNED ───────────────────────────────────────────────────
section_header("Trading Notes")

if "journal_notes" not in st.session_state:
    st.session_state["journal_notes"] = (
        "Key observations:\n"
        "- Technology sector continues to outperform; maintain overweight\n"
        "- Momentum setups performing better than mean-reversion in current regime\n"
        "- Avoid earnings plays in high-VIX environments\n"
        "- Size down on macro uncertainty days\n"
    )

notes = st.text_area(
    "Free-form notes, lessons learned, market observations…",
    value=st.session_state["journal_notes"],
    height=180,
    key="journal_text",
)
if st.button("Save Notes"):
    st.session_state["journal_notes"] = notes
    st.success("Notes saved.")

app_footer()
