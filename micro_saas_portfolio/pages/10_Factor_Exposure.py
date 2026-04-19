import streamlit as st
import pandas as pd
import numpy as np
import statsmodels.api as sm

from utils import apply_theme, apply_responsive_layout, page_header
from data_loader import load_close_series

st.set_page_config(page_title="Factor Exposure", layout="wide", page_icon="📊")
apply_theme()
apply_responsive_layout()
page_header("Factor Exposure", "Fama-French Style Regression · Beta Decomposition")

# ── Sidebar Inputs ─────────────────────────────────────────
st.sidebar.markdown("## Inputs")

tickers_input = st.sidebar.text_input("Portfolio Tickers", "AAPL,MSFT,SPY")
weights_input = st.sidebar.text_input("Weights", "0.3,0.3,0.4")

period = st.sidebar.selectbox("Period", ["6mo", "1y", "2y", "5y"], index=1)

run = st.sidebar.button("Run Factor Analysis")

if not run:
    st.info("Enter inputs and run analysis.")
    st.stop()

# ── Parse ─────────────────────────────────────────
tickers = [t.strip().upper() for t in tickers_input.split(",")]
weights = np.array([float(x) for x in weights_input.split(",")])

if len(tickers) != len(weights):
    st.error("Tickers and weights mismatch")
    st.stop()

weights = weights / weights.sum()

# ── Load Data ─────────────────────────────────────
prices = pd.DataFrame()

for t in tickers:
    s = load_close_series(t, period=period, source="auto")
    if s.empty:
        st.error(f"No data for {t}")
        st.stop()
    prices[t] = s

prices = prices.dropna()

# ── Portfolio returns ─────────────────────────────
returns = prices.pct_change().dropna()
port_ret = returns.dot(weights)

# ── Proxy Factors (simple version)
# Market = SPY
# Size = IWM
# Value = VLUE
# Momentum = MTUM

factors = {
    "MKT": "SPY",
    "SIZE": "IWM",
    "VALUE": "VLUE",
    "MOMENTUM": "MTUM"
}

factor_df = pd.DataFrame()

for name, ticker in factors.items():
    s = load_close_series(ticker, period=period, source="auto")
    factor_df[name] = s

factor_df = factor_df.pct_change().dropna()

# Align
df = pd.concat([port_ret, factor_df], axis=1).dropna()
df.columns = ["PORT"] + list(factors.keys())

# ── Regression ────────────────────────────────────
X = df[factors.keys()]
X = sm.add_constant(X)

y = df["PORT"]

model = sm.OLS(y, X).fit()

# ── Output ───────────────────────────────────────
st.markdown("## Factor Loadings")

coeffs = model.params

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Alpha", f"{coeffs['const']:.5f}")
c2.metric("Market Beta", f"{coeffs['MKT']:.2f}")
c3.metric("Size", f"{coeffs['SIZE']:.2f}")
c4.metric("Value", f"{coeffs['VALUE']:.2f}")
c5.metric("Momentum", f"{coeffs['MOMENTUM']:.2f}")

st.markdown("## Model Statistics")
st.write({
    "R²": round(model.rsquared, 4),
    "Adj R²": round(model.rsquared_adj, 4)
})

st.markdown("## Regression Summary")
st.text(model.summary())

# ── Visualization ────────────────────────────────
import matplotlib.pyplot as plt

fig, ax = plt.subplots()

betas = coeffs.drop("const")
ax.bar(betas.index, betas.values)

ax.set_title("Factor Exposure")
st.pyplot(fig)
