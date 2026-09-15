"""Generic password recovery page."""
from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="CropGuard · Forgot Password", page_icon="🌱", layout="centered")

from utils.ui import inject_public_layout_css

inject_public_layout_css()

st.markdown(
    """
    <style>
    .recover-card { max-width: 540px; margin: 2rem auto; padding: 1.6rem; border-radius: 22px; background: white; box-shadow: 0 15px 40px rgba(20,55,30,.08); }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="recover-card">', unsafe_allow_html=True)
st.header("Reset your password")
st.info("If your account exists, we will send a secure reset link or OTP to the registered contact within a short time window.")

with st.form("forgot_password_form"):
    role = st.selectbox("Account type", ["FARMER", "ADVISOR", "ADMIN"])
    identifier = st.text_input("Mobile number or email")
    submit = st.form_submit_button("Send reset request", use_container_width=True)
    if submit:
        if not identifier:
            st.error("Please enter a valid mobile number or email.")
        else:
            st.success("We have received your request. If the account exists, a secure reset link will be sent soon.")

if st.button("Back to login"):
    st.switch_page("pages/0_Login.py")
st.markdown("</div>", unsafe_allow_html=True)
