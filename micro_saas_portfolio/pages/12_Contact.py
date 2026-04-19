import streamlit as st
from utils import apply_theme, apply_responsive_layout, page_header, app_footer

st.set_page_config(page_title="Contact", layout="wide", page_icon="📩")
apply_theme()
apply_responsive_layout()

page_header("Contact", "Get in touch with QuantDesk Pro")

st.markdown("Use the form below to send a message.")

name = st.text_input("Name")
email = st.text_input("Email")
subject = st.text_input("Subject")
message = st.text_area("Message", height=180)

if st.button("Send Message", use_container_width=True):
    if not name or not email or not subject or not message:
        st.warning("Please complete all fields before sending.")
    else:
        st.success("Message submitted successfully. A real email backend can be connected next.")

st.markdown("""
### Other links

- Add your LinkedIn
- Add your GitHub
- Add a business/support email
""")

app_footer()
