import streamlit as st
from utils import apply_theme

st.set_page_config(
    page_title="QuantDesk Pro",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded",
)
apply_theme()

st.markdown("""
<div style="padding: 24px 0 8px 0;">
  <span style="font-size:40px; font-weight:900; letter-spacing:-1px; color:#e2e8f0;">
    Quant<span style="color:#00d4ff;">Desk</span> <span style="color:#7c3aed;">Pro</span>
  </span>
</div>
<div style="font-size:13px; color:#64748b; letter-spacing:0.15em; text-transform:uppercase; margin-bottom:28px;">
  Professional Quantitative Finance Dashboard
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#111827; border:1px solid #1e2d45; border-radius:12px; padding:20px 28px; margin-bottom:24px;">
  <p style="color:#94a3b8; margin:0; line-height:1.8; font-size:15px;">
    A full-stack quantitative finance workstation built in Python.
    Analyse your portfolio, price options across three models, study the volatility surface,
    run Monte Carlo simulations, and backtest option strategies — all in one place.
  </p>
</div>
""", unsafe_allow_html=True)

cols = st.columns(3)

modules = [
    ("📊", "Portfolio Analytics", [
        "P&L, Sharpe, Sortino, Calmar",
        "Benchmark comparison & alpha/beta",
        "Technical indicators (RSI, MACD, BBands)",
        "Holdings breakdown & CSV export",
    ]),
    ("⚠️", "Risk & Attribution", [
        "Rolling vol, Sharpe, beta, correlation",
        "VaR / CVaR (historical & parametric)",
        "Correlation heatmap",
        "Stress test & custom scenario analysis",
    ]),
    ("📐", "Derivatives", [
        "Black-Scholes, Binomial, Monte Carlo pricing",
        "Full Greeks + ITM probability",
        "Put-call parity checker",
        "Greeks curves & P&L heatmap",
    ]),
    ("🌊", "Volatility Surface", [
        "Live options chain from market data",
        "Volatility smile per expiry",
        "ATM IV term structure",
        "2D heatmap & 3D IV surface",
    ]),
    ("🎲", "Monte Carlo & Strategy Lab", [
        "GBM paths with antithetic variates",
        "MC vs BS convergence",
        "8 option strategy payoff diagrams",
        "Breakeven & risk summary",
    ]),
    ("🔬", "Screener & Watchlist", [
        "Multi-ticker snapshot",
        "RSI & momentum signals",
        "52-week high/low proximity",
        "Volume & volatility filters",
    ]),
]

cols_layout = st.columns(3)
for i, (icon, title, features) in enumerate(modules):
    with cols_layout[i % 3]:
        features_html = "".join(f'<li style="color:#94a3b8; font-size:13px; margin:3px 0;">{f}</li>' for f in features)
        st.markdown(f"""
        <div style="background:#111827; border:1px solid #1e2d45; border-radius:10px;
                    padding:18px 20px; margin-bottom:16px; min-height:160px;">
          <div style="font-size:20px; margin-bottom:6px;">{icon}
            <span style="font-size:15px; font-weight:700; color:#e2e8f0; margin-left:6px;">{title}</span>
          </div>
          <ul style="margin:8px 0 0 0; padding-left:18px;">
            {features_html}
          </ul>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="color:#475569; font-size:12px; text-align:center; letter-spacing:0.08em;">
  QuantDesk Pro &nbsp;·&nbsp; Data via yfinance &nbsp;·&nbsp; For educational and research purposes only.
  Not financial advice.
</div>
""", unsafe_allow_html=True)