import streamlit as st
from utils import apply_theme, apply_responsive_layout, page_header, app_footer
from database import get_supabase

st.set_page_config(page_title="Contact", layout="wide", page_icon="📩")
apply_theme()
apply_responsive_layout()

page_header("Contact", "Get in touch with QuantDesk Pro")

st.markdown("Use the form below to send a message.")

user = getattr(st, "user", None)
user_id = user.get("sub") if user and user.get("is_logged_in") else None
default_email = user.get("email") if user and user.get("is_logged_in") else ""

name_default = user.get("name", "") if user and user.get("is_logged_in") else ""

name = st.text_input("Name", value=name_default)
email = st.text_input("Email", value=default_email)
subject = st.text_input("Subject")
message = st.text_area("Message", height=180)

if st.button("Send Message", use_container_width=True):
    if not name.strip() or not email.strip() or not subject.strip() or not message.strip():
        st.warning("Please complete all fields before sending.")
    else:
        try:
            supabase = get_supabase()
            payload = {
                "name": name.strip(),
                "email": email.strip(),
                "subject": subject.strip(),
                "message": message.strip(),
                "user_id": user_id,
            }
            supabase.table("contact_messages").insert(payload).execute()
            st.success("Message sent successfully.")
        except Exception as e:
            st.error(f"Could not send message: {e}")

st.markdown("""
### Notes

- Messages are stored in the app database.
- A real email backend such as SendGrid can be connected later.
""")

app_footer()
