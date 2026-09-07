"""About CropGuard AI — SIH 2026 prototype."""
from __future__ import annotations

import streamlit as st

from services.i18n import t
from utils.helpers import DISCLAIMER
from utils.ui import lang, sidebar_chrome

st.set_page_config(page_title="About · CropGuard AI", page_icon="ℹ️", layout="wide")
sidebar_chrome()
L = lang()
st.title(f"ℹ️ {t(L, 'nav_about')}")
st.caption("Built as a prototype for Smart India Hackathon 2026.")
st.warning("This app is **not** a government system, is **not** officially approved, and does **not** display live government surveillance feeds.")

st.markdown("### Problem")
st.write(
    "Farmers often notice crop disease and pests only after damage has spread. "
    "Extension officers cannot visit every field. Weather, crop stage, variety and local history "
    "all change outbreak risk. Incorrect pesticide use raises cost and residue concerns. "
    "Authorities also lack a simple geographic picture of emerging problems."
)

st.markdown("### Solution")
st.write(
    "CropGuard AI is a local decision-support prototype: image screening, weather-aware risk, "
    "IPM advisories from a controlled knowledge base, expert validation, follow-up, and a district map."
)

st.markdown("### Technology (this MVP)")
st.write(
    "Python, Streamlit, optional PyTorch/MobileNetV2, OpenCV/NumPy image checks, "
    "scikit-learn DBSCAN hotspots, Plotly charts, Folium maps, Open-Meteo (with demo fallback), SQLite."
)

st.markdown("### AI pipeline (intended)")
st.write(
    "Image → quality check → classifier (or labelled demo predictor) → confidence band → "
    "risk engine (weather + stage + soil + history) → IPM JSON advisory → SQLite case → map / expert queue."
)

st.markdown("### IPM")
st.write(
    "Advisories always start with monitoring, sanitation and non-chemical options. "
    "The app never invents pesticide brands, doses, concentrations or spray schedules. "
    "Chemical text is generic: use only locally registered products and the product label."
)

st.markdown("### Government surveillance (concept)")
st.write(
    "The dashboard shows how a district officer *could* see hotspots and pending reviews. "
    "All mapped points in this build are **simulated demo data** unless a farmer case was just submitted on this machine."
)

st.markdown("### Future scale vs this MVP")
st.code(
    """Farmer app
  → API gateway
    → image processing → computer vision model
    → risk engine ← weather + crop + soil + history
    → PostGIS / database → GIS hotspot engine
    → advisory engine
    → expert validation
    → agriculture dashboard
""",
    language="text",
)
st.caption("Everything above is collapsed into one Streamlit process for the hackathon.")

st.markdown("### Architecture (mermaid)")
st.markdown(
    """
```mermaid
flowchart TD
  F[Farmer capture] --> I[Image screening]
  I --> M[CV model or demo predictor]
  M --> R[Risk engine]
  W[Weather API / fallback] --> R
  H[Local case history] --> R
  R --> A[IPM advisory JSON]
  A --> DB[(SQLite cases)]
  DB --> X[Expert validation]
  X --> DB
  DB --> MAP[Hotspot map]
  DB --> DASH[Officer dashboard]
  DB --> FU[Follow-up]
```
"""
)

st.markdown("### Limitations")
st.write(
    "- Demo predictor is not a trained field model unless you add `models/cropguard.pt`.\n"
    "- Risk weights are prototype assumptions.\n"
    "- No real lab, SMS, or government data feed.\n"
    "- Multilingual UI covers core screens; long advisory text remains English for safety.\n"
    "- Look-alike stresses (nutrient, water, heat, chemical injury) need expert/lab confirmation."
)

st.markdown("### Safety")
st.info(DISCLAIMER)
