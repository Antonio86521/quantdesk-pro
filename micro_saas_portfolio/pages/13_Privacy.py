import streamlit as st
from utils import apply_theme, apply_responsive_layout, page_header, app_footer

st.set_page_config(page_title="Privacy Policy", layout="wide", page_icon="🔒")
apply_theme()
apply_responsive_layout()

page_header("Privacy Policy", "How data is handled on QuantDesk Pro")

st.markdown("""
## Information we may collect

QuantDesk Pro may collect limited information required for app functionality, such as:

- login/account information
- saved portfolio data
- user-submitted contact messages
- technical usage data from hosting providers

## How data is used

Data is used only to:

- operate the platform
- save user portfolios and settings
- improve product functionality
- respond to user contact requests

## Third-party services

QuantDesk Pro may rely on third-party infrastructure or data providers, including:

- Streamlit Cloud
- Supabase
- Yahoo Finance
- Alpha Vantage

These providers may process limited technical data required for the app to function.

## Data sharing

We do not sell personal data.

## Market data disclaimer

Market data may be delayed, incomplete, or temporarily unavailable.

## Final note

QuantDesk Pro is intended for educational and informational use only and is not investment advice.
""")

app_footer()
