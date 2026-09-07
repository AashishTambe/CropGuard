"""Follow-up monitoring after first observation."""
from __future__ import annotations

import io
from datetime import date

import streamlit as st
from PIL import Image, UnidentifiedImageError

from database import add_followup, list_cases, list_followups
from services.i18n import t
from utils.helpers import OUTCOMES, UPLOAD_DIR, save_upload, today_str
from utils.ui import lang, sidebar_chrome

st.set_page_config(page_title="Follow-up · CropGuard AI", page_icon="🔁", layout="wide")
sidebar_chrome()
L = lang()
st.title(f"🔁 {t(L, 'nav_followup')}")
st.caption("Initial observation → action → follow-up image → updated severity → outcome")
st.info(t(L, "simulated"))

cases = list_cases()
if cases.empty:
    st.warning("No cases yet. Submit one from Farmer Detection.")
    st.stop()

ids = cases["case_id"].tolist()
default = st.session_state.get("last_case_id")
index = ids.index(default) if default in ids else 0
cid = st.selectbox("Case", ids, index=index)
row = cases[cases["case_id"] == cid].iloc[0]

st.markdown("#### Initial observation")
c1, c2, c3 = st.columns(3)
c1.write(f"**Crop:** {row['crop']}")
c2.write(f"**Issue:** {row['disease_prediction']}")
c3.write(f"**Status:** {row['status']}")
st.write(f"**Location:** {row['village']}, {row['district']} · **Risk:** {row['risk_level']} ({row['risk_score']}/100)")

img = row.get("image_path") or ""
if img and (UPLOAD_DIR / str(img)).exists():
    st.image(str(UPLOAD_DIR / str(img)), caption="First image", width=280)

st.markdown("#### Add follow-up")
with st.form("fu"):
    d = st.date_input("Follow-up date", value=date.today())
    date_s = str(d) if d else today_str()
    severity = st.selectbox("Updated severity", ["low", "moderate", "high", "critical", "unknown"])
    outcome = st.selectbox("Outcome", OUTCOMES)
    notes = st.text_area("What was done / what changed?")
    photo = st.file_uploader("Follow-up image (optional)", type=["jpg", "jpeg", "png"])
    ok = st.form_submit_button("Save follow-up", type="primary")
if ok:
    fname = ""
    if photo:
        try:
            Image.open(io.BytesIO(photo.getvalue()))
            suffix = ".png" if photo.name.lower().endswith(".png") else ".jpg"
            fname = save_upload(photo.getvalue(), suffix)
        except (UnidentifiedImageError, OSError):
            st.error("Follow-up image could not be read. Record saved without image." if False else "Could not read that image.")
            fname = ""
    add_followup(cid, date_s, severity, outcome, notes, fname)
    st.success(t(L, "followup_saved"))
    st.rerun()

st.markdown("#### Timeline")
fu = list_followups(cid)
if fu.empty:
    st.write("No follow-up visits yet. Record one after the farmer takes action.")
else:
    for _, r in fu.iterrows():
        st.markdown(
            f"- **{r['followup_date']}** · {r['outcome']} · severity {r['severity']}  \n"
            f"  {r.get('notes') or ''}"
        )
        p = r.get("image_path") or ""
        if p and (UPLOAD_DIR / str(p)).exists():
            st.image(str(UPLOAD_DIR / str(p)), width=200)
