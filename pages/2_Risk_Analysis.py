"""Standalone risk explorer using last farmer result or sample inputs."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from database import list_cases
from services.i18n import t
from services.risk_prediction import assess_risk
from services.weather import demo_weather
from utils.helpers import GROWTH_STAGES, MAHARASHTRA_LOCATIONS, crop_catalog, crop_keys, crop_label
from utils.ui import lang, sidebar_chrome, status_pill

st.set_page_config(page_title="Risk Analysis · CropGuard AI", page_icon="🌦️", layout="wide")
sidebar_chrome()
L = lang()
st.title(f"🌦️ {t(L, 'nav_risk')}")
st.caption(t(L, "risk_meaning"))
st.warning(t(L, "prototype_risk"))
st.info(t(L, "simulated"))

last = st.session_state.get("last_result")
crops = crop_keys()
c1, c2, c3 = st.columns(3)
with c1:
    crop_ui = st.selectbox("Crop", [crop_label(k) for k in crops], index=0)
    crop = [k for k in crops if crop_label(k) == crop_ui][0]
    classes = crop_catalog()["crops"][crop]["classes"]
    disease = st.selectbox("Issue class", [c["name"] for c in classes])
    disease_id = next(c["id"] for c in classes if c["name"] == disease)
    kind = next(c.get("kind", "disease") for c in classes if c["name"] == disease)
with c2:
    stage = st.selectbox("Growth stage", GROWTH_STAGES, index=3)
    variety = st.selectbox("Variety", crop_catalog()["crops"][crop]["varieties"])
    district = st.selectbox("District", list(MAHARASHTRA_LOCATIONS.keys()), index=1)
with c3:
    temp = st.slider("Temperature °C", 10, 42, 25)
    hum = st.slider("Humidity %", 20, 100, 82)
    rain = st.slider("Rainfall mm", 0.0, 40.0, 8.4)
    moisture = st.selectbox("Soil moisture", ["Unknown", "Dry", "Adequate", "Wet", "Waterlogged"], index=3)

weather = demo_weather(district)
weather.update({"temperature_c": temp, "humidity": hum, "rainfall_mm": rain, "source": "demo"})
soil = {"soil_type": "Black cotton", "moisture": moisture, "ph": "Unknown", "drainage": "Moderate"}
risk = assess_risk(
    crop=crop,
    disease_id=disease_id,
    disease_name=disease,
    growth_stage=stage,
    variety=variety,
    weather=weather,
    soil=soil,
    cases=list_cases(),
    district=district,
    kind=kind,
)

st.markdown("### Risk result")
st.markdown(status_pill(risk["level"]) + f" **{risk['score']} / 100**", unsafe_allow_html=True)
st.caption("This is **not** a diagnosis. Change stage, humidity or district to see the score move.")

comp = risk["components"]
fig = go.Figure(
    go.Bar(
        x=list(comp.keys()),
        y=list(comp.values()),
        marker_color=["#2e7d32", "#558b2f", "#9ccc65", "#c0ca33", "#ef6c00"],
    )
)
fig.update_layout(title="Score components (prototype)", yaxis_title="Contribution", height=320, margin=dict(t=40, b=20))
st.plotly_chart(fig, use_container_width=True)

st.markdown("#### Contributing factors")
for f in risk["factors"]:
    st.write(f"✓ {f}")

if last:
    st.divider()
    st.markdown("#### Last farmer analysis")
    st.write(
        f"{last['crop_ui']} · {last['pred']['disease']} · {last['risk']['level']} ({last['risk']['score']}/100) · {last['district']}"
    )
