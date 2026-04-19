import datetime
import pandas as pd
import streamlit as st

from data_loader import load_close_series
from utils import (
    apply_responsive_layout,
    apply_theme,
    get_active_plan,
    page_header,
    render_plan_selector,
    terminal_panel,
    terminal_ribbon,
)

st.set_page_config(
    page_title="QuantDesk Pro",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded",
)
apply_theme()
apply_responsive_layout()

st.sidebar.markdown("## Workspace")
plan = render_plan_selector("sidebar")
st.sidebar.caption("Free keeps the core analytics. Pro unlocks factor lab, advanced exports and premium workspace cards.")


@st.cache_data(ttl=600)
def load_market_bar_data():
    tickers = {
        "SPY": "SPY",
        "QQQ": "QQQ",
        "VIX": "^VIX",
        "BTC": "BTC-USD",
        "DXY": "DX-Y.NYB",
        "US 10Y": "^TNX",
    }
    rows = []
    for label, ticker in tickers.items():
        try:
            s = load_close_series(ticker, period="1mo", source="auto")
            if s is None or s.empty or len(s) < 2:
                continue
            last = float(s.iloc[-1])
            prev = float(s.iloc[-2])
            chg = ((last / prev) - 1) * 100
            if label == "US 10Y":
                value = f"{last/10:.2f}%"
            elif abs(last) >= 1000:
                value = f"{last:,.0f}"
            else:
                value = f"{last:,.2f}"
            rows.append((label, value, f"{chg:+.2f}%"))
        except Exception:
            continue
    return rows


def compute_home_snapshot() -> dict:
    watch = {
        "AAPL": 3,
        "MSFT": 2,
        "NVDA": 4,
        "SPY": 6,
    }
    values = []
    for ticker, shares in watch.items():
        try:
            s = load_close_series(ticker, period="6mo", source="auto")
            if s is None or s.empty:
                continue
            values.append({"Ticker": ticker, "Price": float(s.iloc[-1]), "1D": (float(s.iloc[-1]) / float(s.iloc[-2]) - 1) if len(s) > 1 else 0.0, "Value": float(s.iloc[-1]) * shares})
        except Exception:
            continue
    if not values:
        return {"portfolio_value": 0.0, "top_mover": "—", "top_move": 0.0}
    df = pd.DataFrame(values)
    top_idx = df["1D"].abs().idxmax()
    return {
        "portfolio_value": float(df["Value"].sum()),
        "top_mover": str(df.loc[top_idx, "Ticker"]),
        "top_move": float(df.loc[top_idx, "1D"]),
    }


snapshot = compute_home_snapshot()
hour = datetime.datetime.now().hour
greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"

page_header("QuantDesk Pro", "Market Intelligence Terminal")
terminal_ribbon(load_market_bar_data())
terminal_panel(
    "Command Center",
    f"{greeting}. Current workspace plan: {plan.upper()}. Use the navigation below to jump into portfolio, risk, macro and strategy modules.",
)

n1, n2, n3, n4, n5 = st.columns(5)
with n1:
    st.page_link("ap.py", label="Home")
with n2:
    st.page_link("pages/2_Risk_Attribution.py", label="Risk Lab")
with n3:
    st.page_link("pages/7_Macro.py", label="Macro")
with n4:
    st.page_link("pages/8_portfolio_manager.py", label="Portfolio Manager")
with n5:
    st.page_link("pages/9_portfolio_analysis.py", label="Saved Analysis")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Tracked Portfolio", f"${snapshot['portfolio_value']:,.0f}")
k2.metric("Top Mover", snapshot["top_mover"], delta=f"{snapshot['top_move']:+.2%}")
k3.metric("Plan", plan.upper())
k4.metric("Modules", "9")

left, right = st.columns([1.15, 0.85])
with left:
    st.markdown("### What’s New in this build")
    roadmap = pd.DataFrame(
        {
            "Module": [
                "Risk Attribution",
                "Saved Portfolio Analysis",
                "Portfolio Manager",
                "Home Dashboard",
            ],
            "Upgrade": [
                "Stress testing + factor exposure + export pack",
                "Benchmark diagnostics + downloadable report pack",
                "Fund mode + quick NAV monitor",
                "Plan toggle + workflow shortcuts",
            ],
        }
    )
    st.dataframe(roadmap, use_container_width=True, hide_index=True)

    st.markdown("### Workflow")
    st.markdown(
        "1. Create or update a portfolio in **Portfolio Manager**.\n"
        "2. Open **Saved Analysis** to run benchmark, risk and export diagnostics.\n"
        "3. Use **Risk Lab** for stress testing and factor checks.\n"
        "4. Use **Macro** to frame cross-asset context."
    )

with right:
    st.markdown("### Premium Workspace")
    premium_cards = pd.DataFrame(
        {
            "Feature": ["Factor Exposure", "Stress Lab", "Fund Mode", "Export Packs"],
            "Access": ["Pro", "Free/Pro", "Free/Pro", "Pro"],
            "Status": ["Ready", "Ready", "Ready", "Ready"],
        }
    )
    st.dataframe(premium_cards, use_container_width=True, hide_index=True)

    if get_active_plan() == "pro":
        st.success("Pro workspace active. Advanced sections are unlocked across the updated pages.")
    else:
        st.info("Free workspace active. Core analytics remain available, but premium widgets will show gated notices.")

st.markdown("### Quick Access")
q1, q2, q3 = st.columns(3)
with q1:
    st.page_link("pages/2_Risk_Attribution.py", label="Open Stress Test Lab", icon="⚠️")
with q2:
    st.page_link("pages/8_portfolio_manager.py", label="Open Fund Mode", icon="🏦")
with q3:
    st.page_link("pages/9_portfolio_analysis.py", label="Download Portfolio Report", icon="📦")
