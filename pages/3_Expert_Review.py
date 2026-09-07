"""Expert-in-the-loop review queue."""
from __future__ import annotations

import json

import streamlit as st

from database import add_referral, add_review, get_case, pending_expert_cases
from services.i18n import t
from utils.helpers import UPLOAD_DIR, crop_catalog
from utils.ui import lang, sidebar_chrome, status_pill

st.set_page_config(page_title="Expert Review · CropGuard AI", page_icon="🧑‍🔬", layout="wide")
sidebar_chrome()
L = lang()
st.title(f"🧑‍🔬 {t(L, 'nav_expert')}")
st.caption("AI screens. Experts confirm. Confirmed cases become surveillance data.")
st.info(t(L, "simulated"))

df = pending_expert_cases()
if df.empty:
    st.success("No cases waiting. Submit a farmer case or request verification.")
    st.stop()

ids = df["case_id"].tolist()
selected = st.selectbox("Case to review", ids)
row = df[df["case_id"] == selected].iloc[0]
case = get_case(selected) or row.to_dict()

left, right = st.columns((1, 1.2))
with left:
    img = case.get("image_path") or ""
    path = UPLOAD_DIR / img if img else None
    if path and path.exists():
        st.image(str(path), caption="Field image", use_container_width=True)
    else:
        st.info("No uploaded image for this demo seed case (map/table still valid).")
    st.write(f"**Location:** {case.get('village')}, {case.get('district')}, {case.get('state')}")
    st.write(f"**Crop / stage / variety:** {case.get('crop')} · {case.get('growth_stage')} · {case.get('variety')}")
    st.write(f"**AI prediction:** {case.get('disease_prediction')} ({float(case.get('confidence') or 0)*100:.0f}%)")
    st.markdown(status_pill(str(case.get("risk_level"))) + f" {case.get('risk_score')}/100", unsafe_allow_html=True)
    try:
        w = json.loads(case.get("weather_json") or "{}")
        st.write(f"**Weather:** {w.get('temperature_c')}°C, RH {w.get('humidity')}%, rain {w.get('rainfall_mm')} mm ({w.get('source')})")
    except Exception:
        pass

with right:
    st.markdown("#### Local context")
    same = df[df["district"] == case.get("district")]
    st.write(f"{len(same)} queued/open cases currently listed for **{case.get('district')}**.")
    diagnosis_opts = []
    crop = str(case.get("crop") or "tomato").lower()
    classes = crop_catalog()["crops"].get(crop, {}).get("classes", [])
    diagnosis_opts = [c["name"] for c in classes] or [str(case.get("disease_prediction"))]
    action = st.radio("Decision", ["confirm", "reject", "needs_lab"], format_func=lambda x: t(L, {"confirm": "confirm", "reject": "reject", "needs_lab": "needs_lab"}[x]))
    diagnosis = st.selectbox("Correct / working diagnosis", diagnosis_opts)
    severity = st.selectbox("Severity", ["low", "moderate", "high", "critical"])
    notes = st.text_area("Expert notes", placeholder="Field signs, look-alikes, recommended next check…")
    if st.button("Save expert decision", type="primary"):
        add_review(selected, action, diagnosis, severity, notes)
        if action == "confirm":
            st.success(f"{selected} → {t(L, 'expert_confirmed')}")
        elif action == "reject":
            st.warning(f"{selected} rejected / not this issue.")
        else:
            st.info(t(L, "lab_needed"))
        st.rerun()
    if action == "needs_lab" or float(case.get("confidence") or 1) < 0.60:
        st.info(t(L, "lab_needed"))
        if st.button(t(L, "generate_referral")):
            add_referral(selected, diagnosis, notes or "Expert requested laboratory verification.")
            st.success("Referral stored. There is no live laboratory integration in this MVP.")
