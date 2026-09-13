"""CropGuard farmer-first home dashboard."""
from __future__ import annotations

from datetime import datetime

import streamlit as st

from database import kpi_counts, list_cases
from services.i18n import t
from services.weather import demo_weather
from utils.helpers import crop_label
from utils.ui import inject_css, lang, metric_card, sidebar_chrome, status_pill

st.set_page_config(page_title="CropGuard · Smart crop protection", page_icon="🌱", layout="wide", initial_sidebar_state="expanded")
sidebar_chrome()
inject_css()
L = lang()

cases = list_cases()
healthy = cases[cases["disease_id"].astype(str).str.contains("healthy", case=False, na=False)] if not cases.empty else cases
issues = len(cases) - len(healthy)
health_score = round(100 * len(healthy) / len(cases)) if len(cases) else 0
weather = demo_weather("Nashik")

st.markdown(
    '<div class="cg-hero"><div><div class="cg-eyebrow">SMART CROP PROTECTION</div>'
    '<h1>Good morning, farmer</h1><p>See your crop health at a glance and scan a leaf when something looks different.</p></div>'
    '<div class="cg-hero-mark">CG</div></div>', unsafe_allow_html=True
)
st.info(t(L, "simulated"))

hero_left, hero_right = st.columns((1.35, 1), gap="large")
with hero_left:
    st.markdown("### Your farm conditions")
    st.markdown(f'<div class="cg-location"><span class="cg-location-dot">●</span><div><b>Nashik, Maharashtra</b><br><span>Approximate demo location · updated {datetime.now().strftime("%H:%M")}</span></div></div>', unsafe_allow_html=True)
    w1, w2, w3, w4 = st.columns(4)
    w1.metric("Temperature", f"{weather['temperature_c']:.0f}°C")
    w2.metric("Humidity", f"{weather['humidity']:.0f}%")
    w3.metric("Wind", f"{weather['wind_kmh']:.0f} km/h")
    w4.metric("Rainfall", f"{weather['rainfall_mm']:.1f} mm")
    st.caption(f"{weather['condition']} · Open-Meteo / demo fallback")
with hero_right:
    st.markdown('<div class="cg-cta-card"><div class="cg-eyebrow">NEXT BEST ACTION</div><h2>Scan your crop</h2><p>Capture a clear leaf photo for an AI screening and weather-aware guidance.</p></div>', unsafe_allow_html=True)
    if st.button("Start a crop scan", type="primary", use_container_width=True):
        st.switch_page("pages/1_Farmer_Detection.py")

st.write("")
st.markdown("### Crop health overview")
c1, c2, c3, c4 = st.columns(4)
with c1: metric_card("Overall crop health", f"{health_score}/100", "Based on saved scans")
with c2: metric_card("Total scans", str(len(cases)), "AI screenings recorded")
with c3: metric_card("Healthy", str(len(healthy)), "Continue monitoring")
with c4: metric_card("Issues detected", str(issues), "Review recommendations")

left, right = st.columns((1.1, .9), gap="large")
with left:
    st.markdown("### Recent scans")
    if cases.empty:
        st.info("Your recent scans will appear here.")
    else:
        for _, row in cases.head(4).iterrows():
            disease = str(row.get("disease_prediction") or "Unknown")
            crop = crop_label(str(row.get("crop") or ""))
            confidence = float(row.get("confidence") or 0) * 100
            st.markdown(f'<div class="cg-scan-row"><div><b>{crop}</b><br><span>{disease} · {confidence:.0f}% confidence</span></div><div>{status_pill(str(row.get("risk_level") or "Low"))}</div></div>', unsafe_allow_html=True)
with right:
    st.markdown("### Weather risk insight")
    if weather["humidity"] >= 75 or weather["rainfall_mm"] >= 5:
        st.warning("Humid or wet conditions can increase pressure from some fungal diseases. Improve airflow and avoid unnecessary leaf wetness.")
    else:
        st.success("Current conditions are favorable for leaves to dry. Continue regular crop checks.")
    st.caption("This is an informational crop-risk signal, not a diagnosis.")

st.markdown("### How CropGuard works")
steps = [("01", "Find your farm", "Use the location and weather context."), ("02", "Capture a leaf", "Use the camera or choose a photo."), ("03", "Take the next step", "Review confidence, risk and IPM guidance.")]
cols = st.columns(3)
for col, (num, title, body) in zip(cols, steps):
    with col:
        st.markdown(f'<div class="cg-card"><div class="cg-eyebrow">{num}</div><h3>{title}</h3><p>{body}</p></div>', unsafe_allow_html=True)

st.caption("CropGuard is decision support. Confirm uncertain cases with a qualified agricultural expert or laboratory.")


# Vercel detects Python functions through a top-level WSGI/ASGI callable.
# The full interactive app remains Streamlit-first and is launched locally with
# `streamlit run app.py`; this callable keeps Vercel's Python build contract explicit.
def app(environ, start_response):
    body = (
        "CropGuard is a Streamlit application. "
        "Run it with `streamlit run app.py` or deploy it on a Streamlit host."
    ).encode("utf-8")
    start_response(
        "200 OK",
        [
            ("Content-Type", "text/plain; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ],
    )
    return [body]
