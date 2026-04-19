import streamlit as st
from utils import apply_theme, apply_responsive_layout, page_header, app_footer

st.set_page_config(page_title="About", layout="wide", page_icon="📊")
apply_theme()
apply_responsive_layout()

page_header("About QuantDesk Pro", "Professional portfolio analytics platform")

st.markdown("""
### What is QuantDesk Pro?

QuantDesk Pro is a multi-page financial analytics platform designed to simulate the workflow of a professional portfolio and risk monitoring environment.

It combines:

- Portfolio analytics
- Risk attribution
- Derivatives pricing
- Volatility analysis
- Monte Carlo simulations
- Macro monitoring
- Factor exposure
- Portfolio and fund workspace tools

### Purpose

The goal of the platform is to make advanced finance analytics more practical, visual, and accessible through a clean, professional interface.

### Data sources

The platform uses public market data providers such as Yahoo Finance and Alpha Vantage.  
Some data may be delayed and should be treated as informational rather than execution-grade market data.

### Important disclaimer

QuantDesk Pro is for educational and informational purposes only and does **not** constitute financial, investment, legal, or tax advice.
""")

app_footer()
