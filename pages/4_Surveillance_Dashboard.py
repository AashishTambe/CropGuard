"""Agriculture officer surveillance dashboard."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

from database import kpi_counts, list_cases, list_referrals
from services.geospatial import build_map, detect_hotspots
from services.i18n import t
from utils.ui import lang, metric_card, sidebar_chrome, status_pill

st.set_page_config(page_title="Surveillance · CropGuard AI", page_icon="🗺️", layout="wide")
sidebar_chrome()
L = lang()
st.title(f"🗺️ {t(L, 'nav_dashboard')}")
st.error(t(L, "simulated"))
st.caption("Demo surveillance data — not official government outbreak statistics.")

df = list_cases()
k = kpi_counts()
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    metric_card("Total cases", str(k["total"]))
with c2:
    metric_card("Confirmed", str(k["confirmed"]))
with c3:
    metric_card("High-risk areas", str(k["high_risk"]))
with c4:
    metric_card("Pending reviews", str(k["pending"]))
with c5:
    metric_card("Lab referrals", str(k["lab"] + len(list_referrals())))
with c6:
    metric_card("Follow-ups", str(k["followups"]))

if df.empty:
    st.warning("Database is empty. Demo seed should load automatically — restart the app if needed.")
    st.stop()

df = df.copy()
df["date"] = pd.to_datetime(df["timestamp"], errors="coerce").dt.date.astype(str)
crops = ["All"] + sorted(df["crop"].dropna().astype(str).unique().tolist())
districts = ["All"] + sorted(df["district"].dropna().astype(str).unique().tolist())
diseases = ["All"] + sorted(df["disease_prediction"].dropna().astype(str).unique().tolist())
statuses = ["All"] + sorted(df["status"].dropna().astype(str).unique().tolist())

f1, f2, f3, f4 = st.columns(4)
crop_f = f1.selectbox("Crop", crops)
dist_f = f2.selectbox("District", districts)
dis_f = f3.selectbox("Disease / pest", diseases)
stat_f = f4.selectbox("Status", statuses)

view = df.copy()
if crop_f != "All":
    view = view[view["crop"] == crop_f]
if dist_f != "All":
    view = view[view["district"] == dist_f]
if dis_f != "All":
    view = view[view["disease_prediction"] == dis_f]
if stat_f != "All":
    view = view[view["status"] == stat_f]

hotspots = detect_hotspots(view if not view.empty else df)
h1, h2 = st.columns(2)
h1.markdown(f"### Potential hotspots: **{len(hotspots)}**")
if hotspots:
    top = hotspots[0]
    h2.markdown(f"### Highest-risk hotspot: **{top['label']}**")
    h2.caption(f"{top['count']} clustered cases · {t(L, 'hotspot')}")
else:
    h2.info("Not enough clustered cases in this filter.")

st.markdown("#### Maharashtra map")
st.caption("Colours: confirmed = dark red · suspected = orange · pending = blue · lab = purple · rejected = gray")
try:
    fmap = build_map(view, hotspots)
    st_folium(fmap, width=None, height=480)
except Exception:
    st.warning("Map library unavailable. Showing coordinates table instead.")
    st.dataframe(view[["case_id", "district", "latitude", "longitude", "disease_prediction", "status"]])

g1, g2 = st.columns(2)
with g1:
    ts = view.groupby("date").size().reset_index(name="cases")
    fig = px.line(ts, x="date", y="cases", title="Cases over time", markers=True)
    st.plotly_chart(fig, use_container_width=True)
    figc = px.bar(view.groupby("crop").size().reset_index(name="cases"), x="crop", y="cases", title="Cases by crop")
    st.plotly_chart(figc, use_container_width=True)
with g2:
    figd = px.bar(
        view.groupby("disease_prediction").size().reset_index(name="cases"),
        x="disease_prediction",
        y="cases",
        title="Cases by disease / pest",
    )
    st.plotly_chart(figd, use_container_width=True)
    figx = px.bar(view.groupby("district").size().reset_index(name="cases"), x="district", y="cases", title="Cases by district")
    st.plotly_chart(figx, use_container_width=True)

figr = px.pie(view, names="risk_level", title="Risk distribution", hole=0.35)
st.plotly_chart(figr, use_container_width=True)

st.markdown("#### Outbreak surveillance table")
table = view[
    [
        "case_id",
        "timestamp",
        "village",
        "district",
        "crop",
        "disease_prediction",
        "confidence",
        "risk_level",
        "risk_score",
        "status",
        "expert_diagnosis",
    ]
].rename(
    columns={
        "case_id": "Case ID",
        "timestamp": "Date",
        "village": "Village",
        "district": "District",
        "crop": "Crop",
        "disease_prediction": "Disease/Pest",
        "confidence": "AI Confidence",
        "risk_level": "Risk",
        "risk_score": "Score",
        "status": "Status",
        "expert_diagnosis": "Expert Validation",
    }
)
st.dataframe(table, use_container_width=True, hide_index=True)
