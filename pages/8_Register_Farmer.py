"""Farmer registration page."""
from __future__ import annotations

import streamlit as st

from services.auth import create_farmer_account

st.set_page_config(page_title="CropGuard · Register Farmer", page_icon="🌱", layout="wide")

from utils.ui import inject_public_layout_css

inject_public_layout_css()

st.markdown(
    """
    <style>
    .reg-card { background: white; border-radius: 24px; border:1px solid #dfe9df; padding: 1.6rem; box-shadow: 0 16px 35px rgba(20,55,30,.06); }
    .section-title { font-weight: 800; color: #17351f; margin-top: 1.2rem; }
    .reg-card .stForm { margin-top: 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="reg-card">', unsafe_allow_html=True)
st.title("Farmer Registration")
st.caption("Create your CropGuard farmer account and register your farms.")

if "farm_count" not in st.session_state:
    st.session_state.farm_count = 1

form_cols = st.columns(2)
with form_cols[0]:
    full_name = st.text_input("Full Name *")
    phone = st.text_input("Mobile Number *", placeholder="9876543210")
    age = st.number_input("Age", min_value=0, max_value=100, value=30, step=1)
    gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
with form_cols[1]:
    email = st.text_input("Email (optional)", placeholder="you@example.com")
    farmer_type = st.selectbox("Farmer Type", ["Smallholder", "Commercial", "Tenant", "Cooperative"])
    farmer_category = st.selectbox("Farmer Category", ["General", "SC", "ST", "OBC", "Minority", "Women Farmer"])
    show_password = st.checkbox("Show password")
    password = st.text_input("Create Password *", type="text" if show_password else "password")

res_cols = st.columns(2)
with res_cols[0]:
    state = st.text_input("State")
    district = st.text_input("District")
    taluka = st.text_input("Taluka/Sub-District")
    village = st.text_input("Village/Town")
with res_cols[1]:
    address = st.text_area("Address", height=120)
    pin_code = st.text_input("PIN Code")

st.markdown('<div class="section-title">Farm Details</div>', unsafe_allow_html=True)

farms = []
for farm_index in range(st.session_state.farm_count):
    st.markdown(f"### Farm {farm_index + 1}")
    farm_cols = st.columns(2)
    farm_data = {}
    with farm_cols[0]:
        farm_data["farm_name"] = st.text_input(f"Farm Name {farm_index + 1}", key=f"farm_name_{farm_index}")
        farm_data["state"] = st.text_input("Farm State", key=f"farm_state_{farm_index}")
        farm_data["district"] = st.text_input("Farm District", key=f"farm_district_{farm_index}")
        farm_data["taluka"] = st.text_input("Taluka", key=f"farm_taluka_{farm_index}")
        farm_data["village"] = st.text_input("Village", key=f"farm_village_{farm_index}")
        farm_data["farm_address"] = st.text_area("Farm Address", height=90, key=f"farm_address_{farm_index}")
    with farm_cols[1]:
        farm_data["survey_number"] = st.text_input("Survey/Plot Number", key=f"survey_{farm_index}")
        farm_data["land_area"] = st.number_input("Land Area", min_value=0.0, value=2.0, step=0.5, key=f"area_{farm_index}")
        farm_data["land_unit"] = st.selectbox("Unit", ["acre", "hectare"], key=f"unit_{farm_index}")
        farm_data["ownership_type"] = st.selectbox("Ownership Type", ["Owned", "Leased", "Shared"], key=f"owner_{farm_index}")
        farm_data["soil_type"] = st.selectbox("Soil Type", ["Black cotton", "Red", "Alluvial", "Laterite", "Sandy", "Unknown"], key=f"soil_{farm_index}")
        farm_data["irrigation_type"] = st.selectbox("Irrigation Type", ["Drip", "Sprinkler", "Flood", "Rainfed", "Well"], key=f"irrigation_{farm_index}")
        farm_data["main_crop"] = st.text_input("Main Crop", key=f"main_crop_{farm_index}")
        farm_data["crop_variety"] = st.text_input("Crop Variety", key=f"crop_variety_{farm_index}")
        farm_data["sowing_date"] = st.date_input("Sowing Date", key=f"sowing_{farm_index}")
        farm_data["expected_harvest_date"] = st.date_input("Expected Harvest Date", key=f"harvest_{farm_index}")
        farm_data["latitude"] = st.number_input("Latitude", value=19.9975, format="%.6f", key=f"lat_{farm_index}")
        farm_data["longitude"] = st.number_input("Longitude", value=73.7898, format="%.6f", key=f"lon_{farm_index}")
    farms.append(farm_data)

if st.button("+ Add Another Farm"):
    st.session_state.farm_count += 1
    st.rerun()

submitted = st.button("Create Farmer Account", type="primary", use_container_width=True)
if submitted:
    payload = {
        "full_name": full_name,
        "name": full_name,
        "phone": phone,
        "email": email,
        "password": password,
        "age": age,
        "gender": gender,
        "farmer_type": farmer_type,
        "farmer_category": farmer_category,
        "state": state,
        "district": district,
        "taluka": taluka,
        "village": village,
        "address": address,
        "pin_code": pin_code,
        "farms": farms,
    }
    try:
        user = create_farmer_account(payload)
        st.success("Farmer account created successfully. You can now log in with your mobile number and password.")
        st.session_state.auth_user = user
        if st.button("Go to farmer dashboard"):
            st.switch_page("pages/10_Farmer_Dashboard.py")
    except ValueError as exc:
        st.error(str(exc))

if st.button("Back to login"):
    st.switch_page("pages/0_Login.py")

st.markdown("</div>", unsafe_allow_html=True)
