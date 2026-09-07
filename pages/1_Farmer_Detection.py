"""Farmer detection workflow."""
from __future__ import annotations

import io
import json

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, UnidentifiedImageError

from database import add_referral, insert_case, list_cases
from services.advisory import advisory_speech_text, farmer_action_list, get_advisory
from services.disease_detection import get_detector
from services.i18n import t, translate_disease
from services.risk_prediction import assess_risk
from services.weather import fetch_weather, recent_rain_label
from utils.helpers import (
    DRAINAGE,
    GROWTH_STAGES,
    MAHARASHTRA_LOCATIONS,
    SOIL_MOISTURE,
    SOIL_PH,
    SOIL_TYPES,
    class_kind,
    confidence_band,
    crop_keys,
    crop_label,
    image_quality_report,
    new_case_id,
    save_upload,
    variety_options,
)
from utils.ui import lang, metric_card, sidebar_chrome, status_pill

st.set_page_config(page_title="Farmer Detection · CropGuard AI", page_icon="🌱", layout="wide")
sidebar_chrome()
L = lang()

st.title(f"👨‍🌾 {t(L, 'nav_farmer')}")
st.caption("Capture → analyze → risk → IPM action. Large buttons, short sentences.")
st.info(t(L, "simulated"))

crop_map = {crop_label(k): k for k in crop_keys()}
loc_names = list(MAHARASHTRA_LOCATIONS.keys())

with st.form("farmer_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        crop_ui = st.selectbox(t(L, "select_crop"), list(crop_map.keys()), index=list(crop_map.keys()).index("Tomato"))
        crop = crop_map[crop_ui]
        variety = st.selectbox(t(L, "select_variety"), variety_options(crop))
        stage = st.selectbox(t(L, "growth_stage"), GROWTH_STAGES, index=GROWTH_STAGES.index("Fruiting"))
    with c2:
        loc_name = st.selectbox(t(L, "location"), loc_names, index=loc_names.index("Nashik"))
        loc = MAHARASHTRA_LOCATIONS[loc_name]
        village = st.selectbox(t(L, "village"), loc["villages"])
        st.text_input(t(L, "district"), loc["district"], disabled=True)
        st.text_input(t(L, "state"), loc["state"], disabled=True)
    with c3:
        lat = st.number_input(t(L, "latitude"), value=float(loc["lat"]), format="%.4f")
        lon = st.number_input(t(L, "longitude"), value=float(loc["lon"]), format="%.4f")
        soil_type = st.selectbox(t(L, "soil_type"), SOIL_TYPES)
        moisture = st.selectbox(t(L, "soil_moisture"), SOIL_MOISTURE, index=SOIL_MOISTURE.index("Wet"))
        ph = st.selectbox(t(L, "soil_ph"), SOIL_PH)
        drainage = st.selectbox(t(L, "drainage"), DRAINAGE)

    uploaded = st.file_uploader(t(L, "upload_image"), type=["jpg", "jpeg", "png"])
    submitted = st.form_submit_button(t(L, "analyze"), use_container_width=True)

if submitted:
    if not uploaded:
        st.warning("Please upload a JPG or PNG image to continue.")
    else:
        try:
            image = Image.open(io.BytesIO(uploaded.getvalue())).convert("RGB")
        except (UnidentifiedImageError, OSError):
            st.error("This file could not be read as an image. Please try another JPG or PNG.")
            st.stop()
        quality = image_quality_report(image)
        detector = get_detector()
        pred = detector.predict(image, crop)
        weather = fetch_weather(lat, lon, loc["district"])
        st.session_state.weather_source = weather.get("source", "demo")
        cases = list_cases()
        soil = {"soil_type": soil_type, "moisture": moisture, "ph": ph, "drainage": drainage}
        risk = assess_risk(
            crop=crop,
            disease_id=pred["disease_id"],
            disease_name=pred["disease"],
            growth_stage=stage,
            variety=variety,
            weather=weather,
            soil=soil,
            cases=cases,
            district=loc["district"],
            kind=pred.get("kind") or class_kind(crop, pred["disease_id"]),
        )
        suffix = ".png" if uploaded.name.lower().endswith(".png") else ".jpg"
        fname = save_upload(uploaded.getvalue(), suffix=suffix)
        band = confidence_band(pred["confidence"])
        status = "pending_review" if band == "low" or risk["level"] in ("High", "Critical") else "suspected"
        st.session_state.last_result = {
            "image_name": fname,
            "quality": quality,
            "pred": pred,
            "weather": weather,
            "risk": risk,
            "crop": crop,
            "crop_ui": crop_ui,
            "variety": variety,
            "stage": stage,
            "village": village,
            "district": loc["district"],
            "state": loc["state"],
            "lat": lat,
            "lon": lon,
            "soil": soil,
            "status_suggest": status,
            "band": band,
        }

result = st.session_state.get("last_result")
if not result:
    st.markdown("Upload a leaf photo and press **Analyze** to run the pipeline.")
    st.stop()

pred = result["pred"]
risk = result["risk"]
weather = result["weather"]
band = result["band"]
is_healthy = pred["disease"].lower() == "healthy" or "healthy" in pred["disease_id"]
dname = translate_disease(L, pred["disease"])

img_col, out_col = st.columns((1, 1.35))
with img_col:
    try:
        from utils.helpers import UPLOAD_DIR

        st.image(str(UPLOAD_DIR / result["image_name"]), caption="Uploaded image", use_container_width=True)
    except Exception:
        st.info("Image stored for this case.")
    if result["quality"]["poor"]:
        st.error(t(L, "poor_image"))
    else:
        st.success(result["quality"]["message"])

with out_col:
    a, b = st.columns(2)
    with a:
        metric_card(
            t(L, "likely_issue"),
            f"{result['crop_ui']} — {dname}",
            t(L, "diagnosis"),
        )
    with b:
        conf_pct = f"{pred['confidence'] * 100:.0f}%"
        metric_card(t(L, "confidence"), conf_pct, f"{band.title()} confidence · {t(L, 'not_definitive')}")
    st.markdown(status_pill(risk["level"]) + f"  **{risk['score']} / 100**", unsafe_allow_html=True)
    st.caption(t(L, "risk_meaning"))
    if pred.get("mode") == "demo" or pred.get("note"):
        st.warning(pred.get("note") or t(L, "demo_pred"))
    if band == "low":
        st.error(t(L, "low_conf"))
        st.info(t(L, "lab_needed"))
    st.caption("Top 3 (screening only)")
    for item in pred.get("top3", []):
        st.write(f"- {translate_disease(L, item['name'])}: {item['confidence']*100:.0f}%")

st.divider()
w1, w2, w3, w4 = st.columns(4)
w1.metric("Temperature", f"{weather.get('temperature_c', '—')} °C")
w2.metric("Humidity", f"{weather.get('humidity', '—')}%")
w3.metric("Rainfall", f"{weather.get('rainfall_mm', '—')} mm ({recent_rain_label(float(weather.get('rainfall_mm') or 0))})")
w4.metric("Wind", f"{weather.get('wind_kmh', '—')} km/h")
st.caption(weather.get("condition", ""))
if weather.get("source") == "demo" or weather.get("fallback_reason"):
    st.warning(weather.get("fallback_reason") or t(L, "demo_weather"))

st.markdown(f"#### {t(L, 'why')}")
st.caption(t(L, "prototype_risk"))
for f in risk.get("factors", []):
    st.write(f"✓ {f}")

st.markdown(f"#### {t(L, 'advisory')}")
adv = get_advisory(pred["disease_id"])
actions = farmer_action_list(pred["disease_id"], is_healthy)
for i, act in enumerate(actions, 1):
    st.write(f"**{i}.** {act}")

ac1, ac2 = st.columns(2)
with ac1:
    st.markdown(f"**{t(L, 'immediate')}**")
    st.write(adv.get("immediate_action", ""))
    st.markdown(f"**{t(L, 'monitoring')}**")
    st.write(adv.get("monitoring", ""))
    st.markdown(f"**{t(L, 'cultural')}**")
    st.write(adv.get("cultural_control", ""))
    st.write(adv.get("mechanical_control", ""))
with ac2:
    st.markdown(f"**{t(L, 'biological')}**")
    st.write(adv.get("biological_control", ""))
    st.markdown(f"**{t(L, 'chemical')}**")
    st.write(adv.get("chemical_control_category", ""))
    st.markdown(f"**{t(L, 'safety')}**")
    st.write(adv.get("safety_notes", ""))
    st.markdown(f"**{t(L, 'escalation')}**")
    st.write(adv.get("when_to_contact_officer", ""))

speech = advisory_speech_text(f"{result['crop_ui']} {pred['disease']}", f"{risk['level']} {risk['score']}/100", actions)
if st.button(t(L, "read_aloud"), use_container_width=True):
    safe = json.dumps(speech)
    components.html(
        f"""
        <script>
        const u = new SpeechSynthesisUtterance({safe});
        u.lang = "{'hi-IN' if L=='hi' else 'mr-IN' if L=='mr' else 'en-IN'}";
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(u);
        </script>
        """,
        height=0,
    )

b1, b2, b3 = st.columns(3)
with b1:
    if st.button(t(L, "submit_case"), type="primary", use_container_width=True):
        cid = new_case_id()
        insert_case(
            {
                "case_id": cid,
                "crop": result["crop"],
                "variety": result["variety"],
                "growth_stage": result["stage"],
                "disease_prediction": pred["disease"],
                "disease_id": pred["disease_id"],
                "confidence": pred["confidence"],
                "latitude": result["lat"],
                "longitude": result["lon"],
                "village": result["village"],
                "district": result["district"],
                "state": result["state"],
                "weather": weather,
                "risk_score": risk["score"],
                "risk_level": risk["level"],
                "status": result["status_suggest"],
                "image_path": result["image_name"],
                "soil": result["soil"],
                "is_demo": pred.get("mode") == "demo",
                "farmer_id": "demo_farmer",
            }
        )
        st.session_state["last_case_id"] = cid
        st.success(f"{t(L, 'case_saved')}  ({cid})")
with b2:
    if st.button(t(L, "request_expert"), use_container_width=True):
        cid = st.session_state.get("last_case_id") or new_case_id()
        if not st.session_state.get("last_case_id"):
            insert_case(
                {
                    "case_id": cid,
                    "crop": result["crop"],
                    "variety": result["variety"],
                    "growth_stage": result["stage"],
                    "disease_prediction": pred["disease"],
                    "disease_id": pred["disease_id"],
                    "confidence": pred["confidence"],
                    "latitude": result["lat"],
                    "longitude": result["lon"],
                    "village": result["village"],
                    "district": result["district"],
                    "state": result["state"],
                    "weather": weather,
                    "risk_score": risk["score"],
                    "risk_level": risk["level"],
                    "status": "pending_review",
                    "image_path": result["image_name"],
                    "soil": result["soil"],
                    "is_demo": True,
                    "farmer_id": "demo_farmer",
                }
            )
            st.session_state["last_case_id"] = cid
        from database import update_case

        update_case(cid, status="pending_review")
        st.success(f"Routed to expert queue: {cid}")
with b3:
    if st.button(t(L, "monitor_again"), use_container_width=True):
        st.session_state.last_result = None
        st.rerun()

if band == "low" or result["status_suggest"] == "pending_review":
    if st.button(t(L, "generate_referral")):
        cid = st.session_state.get("last_case_id")
        if not cid:
            st.warning("Submit the case first, then generate a lab referral.")
        else:
            add_referral(
                cid,
                f"{result['crop_ui']} {pred['disease']}",
                f"AI confidence {pred['confidence']*100:.0f}%. Prototype referral — no live lab link.",
            )
            st.success(f"Lab referral recorded for {cid}. Not sent to a real laboratory.")
