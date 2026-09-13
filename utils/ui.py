"""Shared Streamlit chrome and CropGuard visual system."""
from __future__ import annotations

import streamlit as st

from database import init_db, kpi_counts
from services.disease_detection import get_detector
from services.i18n import LANGS, t
from utils.helpers import DISCLAIMER

CSS = """
<style>
:root { --cg-ink:#17351f; --cg-muted:#617064; --cg-green:#21613b; --cg-lime:#b9d96d; --cg-cream:#f7f8f2; --cg-line:#dfe7dc; }
.block-container {max-width:1180px; padding:2rem 2.2rem 4rem;}
[data-testid="stAppViewContainer"] {background:var(--cg-cream);}
.cg-hero {display:flex; justify-content:space-between; align-items:center; gap:1rem; background:linear-gradient(120deg,#173d28,#286644); color:#fff; border-radius:24px; padding:2.1rem 2.3rem; margin-bottom:1.2rem; box-shadow:0 12px 30px rgba(30,75,45,.15);}
.cg-hero h1 {margin:.2rem 0 .4rem; font-size:clamp(2rem,4vw,3.7rem); letter-spacing:-.04em; color:#fff;}
.cg-hero p {max-width:620px; margin:0; color:#e7f1e4; font-size:1.05rem;}
.cg-hero-mark {display:grid; place-items:center; width:72px; height:72px; border:1px solid rgba(255,255,255,.35); border-radius:22px; color:#d9ec9b; font-weight:800; letter-spacing:.08em;}
.cg-eyebrow,.cg-kicker {font-size:.72rem; text-transform:uppercase; letter-spacing:.12em; font-weight:800; color:#70816f;}
.cg-card,.cg-cta-card,.cg-location {background:#fff; border:1px solid var(--cg-line); border-radius:18px; padding:1.2rem 1.3rem; box-shadow:0 4px 14px rgba(25,65,35,.05); height:100%;}
.cg-card h3,.cg-cta-card h2 {margin:.4rem 0; color:var(--cg-ink);}
.cg-card p,.cg-cta-card p,.cg-location span {color:var(--cg-muted);}
.cg-cta-card {background:#e8f0d5; border-color:#d4e5b1;}
.cg-cta-card .cg-eyebrow {color:#557036;}
.cg-location {display:flex; align-items:center; gap:.75rem; margin-bottom:1rem; padding:1rem 1.2rem;}
.cg-location-dot {color:#e2a52d; font-size:1.2rem;}
.cg-scan-row {display:flex; justify-content:space-between; align-items:center; gap:1rem; padding:.9rem 0; border-bottom:1px solid var(--cg-line); color:var(--cg-ink);}
.cg-scan-row span {color:var(--cg-muted); font-size:.88rem;}
.cg-value {font-size:1.45rem; font-weight:800; color:var(--cg-ink); margin:.25rem 0;}
.cg-muted {color:var(--cg-muted); font-size:.88rem;}
.cg-pill {display:inline-block; padding:.2rem .65rem; border-radius:999px; font-size:.76rem; font-weight:700;}
.pill-ok {background:#e5f2dd;color:#2d6539}.pill-warn {background:#fff0c9;color:#85630e}.pill-high {background:#ffe0c7;color:#a34816}.pill-crit {background:#f6d2d2;color:#9e2525}.pill-demo {background:#fff0c9;color:#85630e}
.stButton>button {min-height:2.9rem; border-radius:12px; font-weight:750;}
.stButton>button[kind="primary"] {background:#21613b; border-color:#21613b;}
div[data-testid="stSidebar"] {background:#edf3e8;}
@media (max-width:700px){.block-container{padding:1rem .9rem 3rem}.cg-hero{padding:1.5rem;border-radius:18px}.cg-hero-mark{display:none}.cg-hero h1{font-size:2.2rem}.cg-card{padding:1rem}.cg-scan-row{align-items:flex-start}}
</style>
"""

def inject_css() -> None: st.markdown(CSS, unsafe_allow_html=True)
def init_session() -> None:
    init_db(); st.session_state.setdefault("lang", "en"); st.session_state.setdefault("demo_mode", True); st.session_state.setdefault("last_result", None); st.session_state.setdefault("weather_source", "demo")
def lang() -> str: return st.session_state.get("lang", "en")
def sidebar_chrome() -> None:
    init_session(); inject_css(); L=lang()
    with st.sidebar:
        st.markdown("## CropGuard")
        st.caption(t(L,"subtitle"))
        choice=st.radio("Language / भाषा", options=list(LANGS.keys()), format_func=lambda x: LANGS[x], index=list(LANGS.keys()).index(st.session_state.lang), horizontal=True)
        st.session_state.lang=choice; L=choice
        st.markdown(f'<span class="cg-pill pill-demo">{t(L,"demo_on")}</span>', unsafe_allow_html=True)
        st.divider(); st.page_link("app.py", label="Home"); st.page_link("pages/1_Farmer_Detection.py", label="Scan crop"); st.page_link("pages/2_Risk_Analysis.py", label="Risk analysis"); st.page_link("pages/3_Expert_Review.py", label="Expert review"); st.page_link("pages/4_Surveillance_Dashboard.py", label="Surveillance")
        st.divider(); det=get_detector(); k=kpi_counts(); st.caption(f"AI: {det.status_label()}"); st.caption(f"Cases: {k['total']} · Pending: {k['pending']}")
    st.caption(DISCLAIMER)
def status_pill(level: str) -> str:
    lv=(level or "").lower(); cls="pill-ok" if lv not in ("moderate","medium","high","critical") else {"moderate":"pill-warn","medium":"pill-warn","high":"pill-high","critical":"pill-crit"}[lv]; return f'<span class="cg-pill {cls}">{level}</span>'
def metric_card(title: str, value: str, sub: str = "") -> None:
    st.markdown(f'<div class="cg-card"><div class="cg-kicker">{title}</div><div class="cg-value">{value}</div><div class="cg-muted">{sub}</div></div>', unsafe_allow_html=True)
