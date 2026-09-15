"""Advisor-only dashboard."""
from __future__ import annotations

import streamlit as st

from services.auth import require_role, logout

require_role("ADVISOR")

st.set_page_config(page_title="CropGuard · Advisor Dashboard", page_icon="🌾", layout="wide")
st.title("Advisor Dashboard")

if st.button("Logout"):
    logout()
    st.switch_page("pages/0_Login.py")

st.subheader("Assigned farmers")
st.info("This dashboard is reserved for advisor users only.")
