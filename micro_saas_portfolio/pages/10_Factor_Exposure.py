import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm

from utils import apply_theme, apply_responsive_layout, page_header, BORDER, TEXT, MUTED, ACCENT, ACCENT2

st.set_page_config(page_title="Factor Exposure", layout="wide", page_icon="📊")
apply_theme()
apply_responsive_layout()
page_header("Factor Exposure", "Factor Regression · Beta Decomposition · Exposure Map")

from data_loader import load_close_series

st.markdown(
    f"""
    <style>
    .fx-card {{
        border: 1px solid {BORDER};
        border-radius: 16px;
        background: linear-gradient(180deg, #081220 0%, #0a1626 100%);
        padding: 16px 16px 14px 16px;
        min-height: 110px;
    }}
    .fx-label {{
        color: {MUTED};
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }}
    .fx-value {{
        color: {TEXT};
        font-size: 30px;
        font-weight: 900;
        line-height: 1;
    }}
    .fx-sub {{
        color: {MUTED};
        font-size: 12px;
        margin-top: 8px;
    }}
    .section-shell {{
        border: 1px solid {BORDER};
        border-radius: 18px;
        background: linear-gradient(180deg, #07111c 0%, #0a1422 100%);
        padding: 18px;
        margin-bottom: 16px;
    }}
    .mini-stat {{
        border: 1px solid {BORDER};
        border-radius: 14px;
        background: #08111d;
        padding: 14px;
        min-height: 88px;
    }}
    .mini-stat-label {{
        color: {MUTED};
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    }}
    .mini-stat-value {{
        color: {TEXT};
        font-size: 24px;
        font-weight: 900;
    }}
    .summary-box {{
        border: 1px solid {BORDER};
        border-radius: 16px;
        background: #07101a;
        padding: 16px;
        overflow-x: auto;
    }}
    .summary-box pre {{
        color: #d6deeb;
        font-size: 12px;
        line-height: 1.45;
        margin: 0;
        white-space: pre-wrap;
        word-wrap: break-word;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## Inputs")
tickers_input = st.sidebar.text_input("Portfolio Tickers", "AAPL,MSFT,SPY")
weights_input = st.sidebar.text_input("Weights", "0.3,0.3,0.4")
period = st.sidebar.selectbox("Period", ["6mo", "1y", "2y", "5y"], index=1)
run = st.sidebar.button("Run Factor Analysis", use_container_width=True)

if not run:
    st.info("Enter portfolio inputs in the sidebar and click **Run Factor Analysis**.")
    st.stop()

# ── Parse inputs ──────────────────────────────────────────────────────────────
try:
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    weights = np.array([float(x.strip()) for x in weights_input.split(",") if x.strip()], dtype=float)
except Exception:
    st.error("Could not parse tickers or weights.")
    st.stop()

if len(tickers) == 0:
    st.error("Enter at least one ticker.")
    st.stop()

if len(tickers) != len(weights):
    st.error("Tickers and weights must have the same length.")
    st.stop()

if np.isclose(weights.sum(), 0):
    st.error("Weights must not sum to zero.")
    st.stop()

weights = weights / weights.sum()

# ── Load portfolio prices ─────────────────────────────────────────────────────
prices = pd.DataFrame()
for t in tickers:
    s = load_close_series(t, period=period, source="auto")
    if s is None or s.empty:
        st.error(f"No data found for {t}.")
        st.stop()
    prices[t] = s

prices = prices.dropna()
if prices.empty or len(prices) < 30:
    st.error("Not enough aligned price history for the selected portfolio.")
    st.stop()

port_ret = prices.pct_change().dropna().dot(weights)
port_ret.name = "PORT"

# ── Factor proxies ────────────────────────────────────────────────────────────
factor_map = {
    "MKT": "SPY",
    "SIZE": "IWM",
    "VALUE": "VLUE",
    "MOMENTUM": "MTUM",
}

factor_prices = pd.DataFrame()
missing = []

for factor_name, ticker in factor_map.items():
    s = load_close_series(ticker, period=period, source="auto")
    if s is None or s.empty:
        missing.append(factor_name)
        continue
    factor_prices[factor_name] = s

if factor_prices.empty:
    st.error("Could not load factor proxy data.")
    st.stop()

factor_rets = factor_prices.pct_change().dropna()

# ── Align and regress ─────────────────────────────────────────────────────────
df = pd.concat([port_ret, factor_rets], axis=1).dropna()
if len(df) < 30:
    st.error("Not enough overlapping data between portfolio and factor proxies.")
    st.stop()

y = df["PORT"]
X = sm.add_constant(df[[c for c in factor_map.keys() if c in df.columns]])
model = sm.OLS(y, X).fit()

coeffs = model.params
tvals = model.tvalues
pvals = model.pvalues
conf = model.conf_int()
conf.columns = ["CI Low", "CI High"]

results_df = pd.DataFrame({
    "Coefficient": coeffs,
    "t-Stat": tvals,
    "p-Value": pvals,
}).join(conf)

# ── Top metrics ───────────────────────────────────────────────────────────────
st.markdown("## Factor Loadings")
m1, m2, m3, m4, m5 = st.columns(5)

cards = [
    ("Alpha", coeffs.get("const", np.nan), "Daily intercept"),
    ("Market Beta", coeffs.get("MKT", np.nan), "Market sensitivity"),
    ("Size", coeffs.get("SIZE", np.nan), "Small-cap exposure"),
    ("Value", coeffs.get("VALUE", np.nan), "Value tilt"),
    ("Momentum", coeffs.get("MOMENTUM", np.nan), "Trend exposure"),
]

for col, (label, value, subtitle) in zip([m1, m2, m3, m4, m5], cards):
    with col:
        st.markdown(
            f"""
            <div class="fx-card">
                <div class="fx-label">{label}</div>
                <div class="fx-value">{value:.2f if label != 'Alpha' else value:.5f}</div>
                <div class="fx-sub">{subtitle}</div>
            </div>
            """.replace("{value:.2f if label != 'Alpha' else value:.5f}", f"{value:.5f}" if label == "Alpha" else f"{value:.2f}"),
            unsafe_allow_html=True,
        )

# ── Model stats ───────────────────────────────────────────────────────────────
st.markdown("## Model Statistics")
s1, s2, s3, s4 = st.columns(4)

stats_cards = [
    ("R²", f"{model.rsquared:.4f}"),
    ("Adj. R²", f"{model.rsquared_adj:.4f}"),
    ("Observations", f"{int(model.nobs)}"),
    ("F-Statistic", f"{model.fvalue:.2f}" if model.fvalue is not None else "—"),
]

for col, (label, value) in zip([s1, s2, s3, s4], stats_cards):
    with col:
        st.markdown(
            f"""
            <div class="mini-stat">
                <div class="mini-stat-label">{label}</div>
                <div class="mini-stat-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── Main charts ───────────────────────────────────────────────────────────────
left, right = st.columns([1.15, 1])

with left:
    st.markdown("## Factor Exposure Chart")
    betas_only = pd.Series({
        "MKT": coeffs.get("MKT", np.nan),
        "SIZE": coeffs.get("SIZE", np.nan),
        "VALUE": coeffs.get("VALUE", np.nan),
        "MOMENTUM": coeffs.get("MOMENTUM", np.nan),
    }).dropna()

    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.bar(betas_only.index, betas_only.values)
    ax.axhline(0, linewidth=1)
    ax.set_ylabel("Exposure")
    ax.set_title("Portfolio Factor Betas")
    st.pyplot(fig, use_container_width=True)

with right:
    st.markdown("## Interpretation")
    strongest = betas_only.abs().idxmax() if not betas_only.empty else "—"
    direction = "positive" if not betas_only.empty and betas_only.loc[strongest] >= 0 else "negative"

    st.markdown(
        f"""
        <div class="section-shell">
            <p style="color:{TEXT}; font-size:14px; margin-top:0;">
                This portfolio is primarily driven by <b>{strongest}</b> with a
                <b>{direction}</b> loading.
            </p>
            <p style="color:{MUTED}; font-size:13px;">
                Market beta above 1.0 suggests the portfolio moves more than the market.
                Negative size/value/momentum coefficients indicate underweight exposure to those styles.
            </p>
            <p style="color:{MUTED}; font-size:13px; margin-bottom:0;">
                Use this page as a style map: it tells you whether your holdings behave
                like broad beta, small caps, value names, or momentum-driven assets.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Fitted vs actual ──────────────────────────────────────────────────────────
st.markdown("## Actual vs Fitted Returns")
compare = pd.DataFrame({
    "Actual": y,
    "Fitted": model.fittedvalues,
}, index=df.index)

fig2, ax2 = plt.subplots(figsize=(10, 4.5))
ax2.plot(compare.index, compare["Actual"], label="Actual", linewidth=1.3)
ax2.plot(compare.index, compare["Fitted"], label="Fitted", linewidth=1.3)
ax2.set_title("Portfolio Returns vs Factor Model Fit")
ax2.legend()
st.pyplot(fig2, use_container_width=True)

# ── Regression table ──────────────────────────────────────────────────────────
st.markdown("## Regression Output Table")
display_df = results_df.rename(index={"const": "Alpha"}).copy()

st.dataframe(
    display_df.style.format({
        "Coefficient": "{:.6f}",
        "t-Stat": "{:.3f}",
        "p-Value": "{:.4f}",
        "CI Low": "{:.6f}",
        "CI High": "{:.6f}",
    }),
    use_container_width=True,
)

# ── Raw statsmodels output in expander ────────────────────────────────────────
with st.expander("Full statsmodels summary"):
    st.markdown(
        f"""
        <div class="summary-box">
            <pre>{model.summary().as_text()}</pre>
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.expander("Factor proxy tickers used"):
    st.write({
        "MKT": "SPY",
        "SIZE": "IWM",
        "VALUE": "VLUE",
        "MOMENTUM": "MTUM",
    })

if missing:
    st.warning(f"Some factor proxies could not be loaded: {', '.join(missing)}")
