import streamlit as st
from utils import apply_theme, apply_responsive_layout, page_header, app_footer

st.set_page_config(page_title="Terms of Use", layout="wide", page_icon="📄")
apply_theme()
apply_responsive_layout()

page_header("Terms of Use", "Conditions for using QuantDesk Pro")

st.markdown("""
## Acceptance of terms

By using QuantDesk Pro, you agree to use the platform for lawful and appropriate purposes only.

## Nature of the platform

QuantDesk Pro is an informational and educational analytics platform.  
It is not a broker, exchange, investment adviser, or execution platform.

## No investment advice

Nothing displayed in the platform constitutes financial, investment, legal, or tax advice.

## Data accuracy

Market data may be delayed, incomplete, or contain inaccuracies.  
No guarantee is made regarding completeness, timeliness, or accuracy.

## User responsibility

Users are responsible for how they interpret and use the outputs of the platform.

## Availability

Features, data providers, and functionality may change, be interrupted, or become unavailable at any time.

## Limitation

Use of the platform is at your own risk.
""")

app_footer()
