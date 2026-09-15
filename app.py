"""CropGuard farmer-first home dashboard."""
from __future__ import annotations

from datetime import datetime

import streamlit as st

from database import kpi_counts, list_cases
from services.auth import get_current_user
from services.i18n import t
from services.weather import demo_weather
from utils.helpers import crop_label
from utils.ui import inject_css, lang, metric_card, sidebar_chrome, status_pill

if get_current_user() is None:
    st.switch_page("pages/0_Login.py")


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="CropGuard · Smart crop protection",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Common UI setup
# ---------------------------------------------------------
sidebar_chrome()
inject_css()

# Get currently selected language
L = lang()


# ---------------------------------------------------------
# Data
# ---------------------------------------------------------
cases = list_cases()

healthy = (
    cases[
        cases["disease_id"]
        .astype(str)
        .str.contains("healthy", case=False, na=False)
    ]
    if not cases.empty
    else cases
)

issues = len(cases) - len(healthy)

health_score = (
    round(100 * len(healthy) / len(cases))
    if len(cases)
    else 0
)

weather = demo_weather("Nashik")

current_hour = datetime.now().hour


# ---------------------------------------------------------
# Greeting
# ---------------------------------------------------------
if 5 <= current_hour < 12:
    greeting_key = "good_morning"
elif 12 <= current_hour < 17:
    greeting_key = "good_afternoon"
elif 17 <= current_hour < 21:
    greeting_key = "good_evening"
else:
    greeting_key = "good_night"

greeting = t(L, greeting_key)
farm_hero = t(L, "farm_hero")


# ---------------------------------------------------------
# Hero section
# ---------------------------------------------------------
st.markdown(
    f"""
    <div class="cg-hero">
        <div class="cg-eyebrow">
            {t(L, "smart_crop_protection")}
        </div>
        <h1>{greeting}, {farm_hero}</h1>
        <p>
            {t(L, "hero_description")}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(t(L, "simulated"))


# ---------------------------------------------------------
# Farm conditions + Scan CTA
# ---------------------------------------------------------
hero_left, hero_right = st.columns((1.35, 1), gap="large")


with hero_left:
    st.markdown(
        f"### {t(L, 'farm_conditions')}"
    )

    st.markdown(
        f"""
        <div class="cg-location">
            <span class="cg-location-dot">●</span>
            <div>
                <b>{t(L, "nashik_maharashtra")}</b><br>
                <span>
                    {t(L, "demo_location")} ·
                    {t(L, "updated_at")}
                    {datetime.now().strftime("%H:%M")}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    w1, w2, w3, w4 = st.columns(4)

    w1.metric(
        t(L, "temperature"),
        f"{weather['temperature_c']:.0f}°C",
    )

    w2.metric(
        t(L, "humidity"),
        f"{weather['humidity']:.0f}%",
    )

    w3.metric(
        t(L, "wind"),
        f"{weather['wind_kmh']:.0f} km/h",
    )

    w4.metric(
        t(L, "rainfall"),
        f"{weather['rainfall_mm']:.1f} mm",
    )

    st.caption(
        f"{weather['condition']} · {t(L, 'weather_source')}"
    )


with hero_right:
    st.markdown(
        f"""
        <div class="cg-cta-card">
            <div class="cg-eyebrow">
                {t(L, "next_best_action")}
            </div>

            <h2>{t(L, "scan_your_crop")}</h2>

            <p>
                {t(L, "scan_description")}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        t(L, "start_crop_scan"),
        type="primary",
        use_container_width=True,
    ):
        st.switch_page("pages/1_Farmer_Detection.py")


# ---------------------------------------------------------
# Crop health overview
# ---------------------------------------------------------
st.write("")

st.markdown(
    f"### {t(L, 'crop_health_overview')}"
)

c1, c2, c3, c4 = st.columns(4)


with c1:
    metric_card(
        t(L, "overall_crop_health"),
        f"{health_score}/100",
        t(L, "based_on_saved_scans"),
    )


with c2:
    metric_card(
        t(L, "total_scans"),
        str(len(cases)),
        t(L, "ai_screenings_recorded"),
    )


with c3:
    metric_card(
        t(L, "healthy"),
        str(len(healthy)),
        t(L, "continue_monitoring"),
    )


with c4:
    metric_card(
        t(L, "issues_detected"),
        str(issues),
        t(L, "review_recommendations"),
    )


# ---------------------------------------------------------
# Recent scans + Weather risk
# ---------------------------------------------------------
left, right = st.columns((1.1, 0.9), gap="large")


with left:
    st.markdown(
        f"### {t(L, 'recent_scans')}"
    )

    if cases.empty:
        st.info(t(L, "recent_scans_empty"))

    else:
        for _, row in cases.head(4).iterrows():

            disease = str(
                row.get("disease_prediction") or "Unknown"
            )

            crop = crop_label(
                str(row.get("crop") or "")
            )

            confidence = (
                float(row.get("confidence") or 0) * 100
            )

            risk_level = str(
                row.get("risk_level") or "Low"
            )

            st.markdown(
                f"""
                <div class="cg-scan-row">
                    <div>
                        <b>{crop}</b><br>
                        <span>
                            {disease} ·
                            {confidence:.0f}%
                            {t(L, "confidence_short")}
                        </span>
                    </div>

                    <div>
                        {status_pill(risk_level)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


with right:
    st.markdown(
        f"### {t(L, 'weather_risk_insight')}"
    )

    if (
        weather["humidity"] >= 75
        or weather["rainfall_mm"] >= 5
    ):
        st.warning(
            t(L, "weather_risk_high")
        )

    else:
        st.success(
            t(L, "weather_risk_low")
        )

    st.caption(
        t(L, "risk_disclaimer")
    )


# ---------------------------------------------------------
# How CropGuard works
# ---------------------------------------------------------
st.markdown(
    f"### {t(L, 'how_cropguard_works')}"
)

steps = [
    (
        "01",
        t(L, "step_find_farm"),
        t(L, "step_find_farm_body"),
    ),
    (
        "02",
        t(L, "step_capture_leaf"),
        t(L, "step_capture_leaf_body"),
    ),
    (
        "03",
        t(L, "step_next_step"),
        t(L, "step_next_step_body"),
    ),
]

cols = st.columns(3)

for col, (num, title, body) in zip(cols, steps):

    with col:
        st.markdown(
            f"""
            <div class="cg-card">
                <div class="cg-eyebrow">
                    {num}
                </div>

                <h3>{title}</h3>

                <p>{body}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------
# Footer disclaimer
# ---------------------------------------------------------
st.caption(
    t(L, "footer_disclaimer")
)


# ---------------------------------------------------------
# Vercel WSGI callable
# ---------------------------------------------------------
# Vercel detects Python functions through a top-level
# WSGI/ASGI callable.
#
# The full interactive app remains Streamlit-first and is
# launched locally with:
#
#     streamlit run app.py
#
# This callable keeps Vercel's Python build contract explicit.
# ---------------------------------------------------------
def app(environ, start_response):
    body = (
        "CropGuard is a Streamlit application. "
        "Run it with `streamlit run app.py` "
        "or deploy it on a Streamlit host."
    ).encode("utf-8")

    start_response(
        "200 OK",
        [
            ("Content-Type", "text/plain; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ],
    )

    return [body]