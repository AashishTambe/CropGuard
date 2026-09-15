"""Farmer-only dashboard."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from database import connect
from services.auth import require_role, logout

require_role("FARMER")

st.set_page_config(page_title="CropGuard · Farmer Dashboard", page_icon="🌱", layout="wide")

user = st.session_state.auth_user
st.title(f"Welcome, {user.get('name', 'Farmer')}")

if st.button("Logout"):
    logout()
    st.switch_page("pages/0_Login.py")

conn = connect()
farms = pd.read_sql_query(
    "SELECT * FROM farms WHERE user_id = ? ORDER BY created_at DESC",
    conn,
    params=(user["id"],),
)
conn.close()

st.subheader("Your Farms")
if farms.empty:
    st.info("No farms registered yet.")
else:
    for _, farm in farms.head(3).iterrows():
        st.markdown(f"### {farm['farm_name']} ")
        st.caption(f"Farm ID: {farm['farm_id']} · {farm['district']}, {farm['state']}")

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("Total Farms", len(farms) if not farms.empty else 0)
with c2:
    st.metric("Total Land Area", f"{farms['land_area'].sum():.1f} acre" if not farms.empty else "0.0 acre")
with c3:
    st.metric("Healthy Crops", "4")
with c4:
    st.metric("Crops At Risk", "2")
with c5:
    st.metric("Active Alerts", "1")

st.subheader("Recent Alerts")
st.info("Aphid activity trending in the eastern field; keep monitoring for the next 48 hours.")
st.subheader("Advisor Recommendations")
st.success("Early blight risk is moderate. Use preventive sanitation and continue field inspection.")
