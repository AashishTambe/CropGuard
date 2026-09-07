"""CropGuard AI — home landing page."""
from __future__ import annotations

import streamlit as st

from database import kpi_counts, learning_loop_stats
from services.i18n import t
from utils.ui import inject_css, lang, metric_card, sidebar_chrome

st.set_page_config(
    page_title="CropGuard AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

sidebar_chrome()
inject_css()
L = lang()

st.markdown(
    f"""
    <div class="cg-banner">
      <h1>🌱 {t(L, "app_name")}</h1>
      <p>{t(L, "subtitle")}</p>
      <p><b>{t(L, "tagline")}</b></p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(t(L, "simulated"))

k = kpi_counts()
c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Reported cases", str(k["total"]), "Includes simulated demo records")
with c2:
    metric_card("Expert confirmed", str(k["confirmed"]), "Validated field observations")
with c3:
    metric_card("High / critical risk", str(k["high_risk"]), "Needs officer attention")
with c4:
    metric_card("Pending reviews", str(k["pending"]), "Expert-in-the-loop queue")

st.write("")
st.subheader("Capabilities")
caps = [
    ("📷", t(L, "cap1"), "Screen a leaf or plant photo before damage spreads."),
    ("🌦️", t(L, "cap2"), "Combine weather, crop stage, soil and local history."),
    ("🗺️", t(L, "cap3"), "See district clusters that may be emerging hotspots."),
    ("👨‍🌾", t(L, "cap4"), "IPM-first steps. No invented pesticide doses."),
]
cols = st.columns(4)
for col, (icon, title, text) in zip(cols, caps):
    with col:
        st.markdown(
            f'<div class="cg-card"><p class="cg-value">{icon} {title}</p>'
            f'<p class="cg-muted">{text}</p></div>',
            unsafe_allow_html=True,
        )

st.write("")
st.subheader(t(L, "how"))
steps = [t(L, f"step{i}") for i in range(1, 6)]
sc = st.columns(5)
for col, n, name in zip(sc, range(1, 6), steps):
    with col:
        st.markdown(
            f'<div class="cg-step"><div class="cg-kicker">Step {n}</div>'
            f'<div class="cg-value">{name}</div></div>',
            unsafe_allow_html=True,
        )

st.write("")
left, right = st.columns((1.2, 1))
with left:
    st.markdown("### From reactive spraying to early action")
    st.markdown(
        """
1. **See the disease** — image screening with confidence bands.  
2. **Understand the risk** — weather + stage + soil + nearby cases.  
3. **Take the right action** — IPM advisory, not a pesticide shopping list.  
4. **Map the outbreak** — officers see district hotspots.  
5. **Validate with experts** — AI does not replace agronomists.  
6. **Monitor the outcome** — follow-up after treatment.
        """
    )
    st.caption("Diagnosis answers *what might already be on this plant*. Risk answers *how likely it is to become a field problem now*.")
with right:
    st.markdown("### AI learning loop")
    stats = learning_loop_stats()
    st.metric("Total AI / demo predictions stored", stats["total_predictions"])
    st.metric("Expert confirmed", stats["expert_confirmed"])
    st.metric("Correction rate (rejects / reviews)", f"{stats['correction_rate']}%")
    st.metric("Pending review", stats["pending_review"])
    st.caption("Confirmed field observations can be used to improve future model versions. This MVP does **not** retrain automatically.")

st.success("Open **Farmer Detection** in the sidebar to run the live demo walkthrough (Tomato · Fruiting · Nashik).")
