"""Admin-only dashboard."""
from __future__ import annotations

import streamlit as st

from services.auth import require_role, logout

require_role("ADMIN")

st.set_page_config(page_title="CropGuard · Admin Dashboard", page_icon="🛡️", layout="wide")
st.title("Admin Dashboard")

if st.button("Logout"):
    logout()
    st.switch_page("pages/0_Login.py")

st.subheader("System overview")
st.success("Admin access confirmed. System-wide controls are available here.")
