"""Mobile-first farmer scan workflow."""
from __future__ import annotations
import io, json
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, UnidentifiedImageError
from database import add_referral, insert_case, list_cases
from services.advisory import advisory_speech_text, farmer_action_list, get_advisory
from services.disease_detection import get_detector
from services.i18n import t, translate_disease
from services.risk_prediction import assess_risk
from services.weather import fetch_weather, recent_rain_label
from utils.helpers import DRAINAGE, GROWTH_STAGES, MAHARASHTRA_LOCATIONS, SOIL_MOISTURE, SOIL_PH, SOIL_TYPES, class_kind, confidence_band, crop_keys, crop_label, image_quality_report, new_case_id, save_upload, variety_options
from utils.ui import inject_css, lang, metric_card, sidebar_chrome, status_pill

st.set_page_config(page_title="CropGuard · Scan crop", page_icon="🌱", layout="wide")
sidebar_chrome(); inject_css(); L=lang()
st.markdown('<div class="cg-eyebrow">CROP SCANNER</div><h1>Scan your crop</h1><p>Take a clear photo of an affected leaf. CropGuard combines the image with local conditions for an early screening.</p>', unsafe_allow_html=True)
st.info(t(L,"simulated"))

crop_map={crop_label(k):k for k in crop_keys()}; loc_names=list(MAHARASHTRA_LOCATIONS)
with st.expander("Farm details", expanded=False):
    c1,c2,c3=st.columns(3)
    with c1: crop_ui=st.selectbox("Crop",list(crop_map),index=list(crop_map).index("Tomato")); crop=crop_map[crop_ui]; variety=st.selectbox("Variety",variety_options(crop)); stage=st.selectbox("Growth stage",GROWTH_STAGES,index=GROWTH_STAGES.index("Fruiting"))
    with c2: loc_name=st.selectbox("Location",loc_names,index=loc_names.index("Nashik")); loc=MAHARASHTRA_LOCATIONS[loc_name]; village=st.selectbox("Village",loc["villages"]); st.caption(f"{loc['district']}, {loc['state']} · location is a fallback when device location is unavailable")
    with c3: soil_type=st.selectbox("Soil type",SOIL_TYPES); moisture=st.selectbox("Soil moisture",SOIL_MOISTURE,index=SOIL_MOISTURE.index("Wet")); ph=st.selectbox("Soil pH",SOIL_PH); drainage=st.selectbox("Drainage",DRAINAGE)

st.markdown("### 1. Capture a leaf photo")
photo=st.camera_input("Use your phone camera", help="Place the affected leaf inside the frame. Use good lighting and avoid blurry images.")
with st.expander("Use a photo from your device instead"):
    uploaded=st.file_uploader("Choose JPG or PNG",type=["jpg","jpeg","png"])
source=photo or uploaded
if source is None:
    st.caption("Camera is the recommended option on mobile. A gallery upload is available as a fallback.")
    st.stop()

if st.button("Analyze crop", type="primary", use_container_width=True):
    try: image=Image.open(io.BytesIO(source.getvalue())).convert("RGB")
    except (UnidentifiedImageError,OSError): st.error("We couldn't read that image. Please try another photo."); st.stop()
    quality=image_quality_report(image)
    if quality["poor"]: st.warning("Image may be unclear. You can continue, but a brighter and steadier photo may improve screening.")
    with st.status("CropGuard AI is analyzing your crop...", expanded=True) as progress:
        st.write("Image received"); st.write("Analyzing leaf"); detector=get_detector(); pred=detector.predict(image,crop); st.write("Preparing recommendations")
        weather=fetch_weather(float(loc["lat"]),float(loc["lon"]),loc["district"]); progress.update(label="Analysis complete",state="complete",expanded=False)
    soil={"soil_type":soil_type,"moisture":moisture,"ph":ph,"drainage":drainage}; risk=assess_risk(crop=crop,disease_id=pred["disease_id"],disease_name=pred["disease"],growth_stage=stage,variety=variety,weather=weather,soil=soil,cases=list_cases(),district=loc["district"],kind=pred.get("kind") or class_kind(crop,pred["disease_id"]))
    fname=save_upload(source.getvalue(),suffix=".png" if getattr(source,"name","").lower().endswith(".png") else ".jpg"); band=confidence_band(pred["confidence"])
    st.session_state.last_result={"image_name":fname,"quality":quality,"pred":pred,"weather":weather,"risk":risk,"crop":crop,"crop_ui":crop_ui,"variety":variety,"stage":stage,"village":village,"district":loc["district"],"state":loc["state"],"lat":loc["lat"],"lon":loc["lon"],"soil":soil,"status_suggest":"pending_review" if band=="low" or risk["level"] in ("High","Critical") else "suspected","band":band}
    st.rerun()

result=st.session_state.get("last_result")
if not result: st.stop()
pred=result["pred"]; risk=result["risk"]; weather=result["weather"]; band=result["band"]; healthy=pred["disease"].lower()=="healthy" or "healthy" in pred["disease_id"]; dname=translate_disease(L,pred["disease"])
st.divider(); st.markdown("### 2. AI diagnosis")
img_col,out_col=st.columns((.9,1.2),gap="large")
with img_col:
    st.image(str(__import__('utils.helpers',fromlist=['UPLOAD_DIR']).UPLOAD_DIR/result["image_name"]),caption="Captured crop image",use_container_width=True)
    st.caption(result["quality"]["message"])
with out_col:
    if healthy: st.success("Your crop appears healthy. Continue regular monitoring.")
    a,b=st.columns(2)
    with a: metric_card("Likely issue",f"{result['crop_ui']} — {dname}","AI screening")
    with b: metric_card("AI confidence",f"{pred['confidence']*100:.0f}%",f"{band.title()} confidence")
    st.markdown(status_pill(risk["level"])+f"  **{risk['score']} / 100**",unsafe_allow_html=True); st.caption("Risk is a decision-support signal, not a definitive diagnosis.")
    for item in pred.get("top3",[]): st.write(f"{translate_disease(L,item['name'])}: {item['confidence']*100:.0f}%")
    if pred.get("mode")=="demo" or pred.get("note"): st.warning(pred.get("note") or t(L,"demo_pred"))

st.markdown("### Local conditions")
w1,w2,w3,w4=st.columns(4); w1.metric("Temperature",f"{weather.get('temperature_c','—')} °C"); w2.metric("Humidity",f"{weather.get('humidity','—')}%"); w3.metric("Rainfall",f"{weather.get('rainfall_mm','—')} mm ({recent_rain_label(float(weather.get('rainfall_mm') or 0))})"); w4.metric("Wind",f"{weather.get('wind_kmh','—')} km/h"); st.caption(weather.get("condition",""))
if weather.get("source")=="demo": st.caption(weather.get("fallback_reason") or "Showing demo weather data.")

st.markdown("### Recommended next steps"); adv=get_advisory(pred["disease_id"]); actions=farmer_action_list(pred["disease_id"],healthy)
for i,act in enumerate(actions,1): st.write(f"**{i}.** {act}")
with st.expander("Treatment, prevention and safety guidance"):
    for label,key in [("Immediate action","immediate_action"),("Monitoring","monitoring"),("Cultural control","cultural_control"),("Biological control","biological_control"),("Chemical guidance","chemical_control_category"),("Safety","safety_notes"),("When to contact an officer","when_to_contact_officer")]: st.markdown(f"**{label}**"); st.write(adv.get(key,""))

if st.button("Read recommendations aloud",use_container_width=True):
    safe=json.dumps(advisory_speech_text(f"{result['crop_ui']} {pred['disease']}",f"{risk['level']} {risk['score']} out of 100",actions)); components.html(f'<script>const u=new SpeechSynthesisUtterance({safe});u.lang="en-IN";window.speechSynthesis.cancel();window.speechSynthesis.speak(u);</script>',height=0)

b1,b2,b3=st.columns(3)
with b1:
    if st.button("Save scan",type="primary",use_container_width=True):
        cid=new_case_id(); insert_case({"case_id":cid,"crop":result["crop"],"variety":result["variety"],"growth_stage":result["stage"],"disease_prediction":pred["disease"],"disease_id":pred["disease_id"],"confidence":pred["confidence"],"latitude":result["lat"],"longitude":result["lon"],"village":result["village"],"district":result["district"],"state":result["state"],"weather":weather,"risk_score":risk["score"],"risk_level":risk["level"],"status":result["status_suggest"],"image_path":result["image_name"],"soil":result["soil"],"is_demo":pred.get("mode")=="demo","farmer_id":"demo_farmer"}); st.session_state["last_case_id"]=cid; st.success(f"Scan saved: {cid}")
with b2:
    if st.button("Request expert review",use_container_width=True): st.info("Save the scan first, then route it from the expert review page.")
with b3:
    if st.button("Start another scan",use_container_width=True): st.session_state.last_result=None; st.rerun()
if band=="low":
    if st.button("Create lab referral"): st.info("Save the scan first to create a referral record.")
