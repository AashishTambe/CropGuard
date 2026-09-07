"""Shared Streamlit chrome."""
from __future__ import annotations

import streamlit as st

from database import init_db, kpi_counts
from services.disease_detection import get_detector
from services.i18n import LANGS, t
from utils.helpers import DISCLAIMER

CSS = """
<style>
.block-container {padding-top: 1.2rem; max-width: 1200px;}
.cg-banner {
  background: linear-gradient(110deg, #1b5e20 0%, #2e7d32 45%, #558b2f 100%);
  color: #fff; padding: 1.4rem 1.6rem; border-radius: 14px; margin-bottom: 1rem;
}
.cg-banner h1 {margin: 0; font-size: 2rem; letter-spacing: .02em;}
.cg-banner p {margin: .35rem 0 0 0; opacity: .95;}
.cg-card {
  background: #ffffff; border: 1px solid #d7e3d0; border-radius: 12px;
  padding: 1rem 1.1rem; box-shadow: 0 1px 4px rgba(27,94,32,.06); height: 100%;
}
.cg-kicker {font-size: .75rem; text-transform: uppercase; letter-spacing: .08em; color: #4e6a46; margin: 0;}
.cg-value {font-size: 1.35rem; font-weight: 700; color: #1b3d18; margin: .2rem 0;}
.cg-muted {color: #5b6758; font-size: .9rem;}
.cg-pill {
  display: inline-block; padding: .15rem .6rem; border-radius: 999px;
  font-size: .8rem; font-weight: 600; margin-right: .3rem;
}
.pill-demo {background: #fff3cd; color: #7a5b00; border: 1px solid #e6c35c;}
.pill-ok {background: #e8f5e9; color: #1b5e20; border: 1px solid #a5d6a7;}
.pill-warn {background: #ffe0b2; color: #e65100;}
.pill-high {background: #ffcdd2; color: #b71c1c;}
.pill-crit {background: #b71c1c; color: #fff;}
.stButton>button {
  min-height: 2.6rem; font-weight: 600; border-radius: 10px;
}
div[data-testid="stSidebar"] {background: #eef5ea;}
.cg-step {
  background: #fff; border-radius: 12px; padding: .9rem; text-align: center;
  border: 1px solid #d7e3d0;
}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def init_session() -> None:
    init_db()
    st.session_state.setdefault("lang", "en")
    st.session_state.setdefault("demo_mode", True)
    st.session_state.setdefault("last_result", None)
    st.session_state.setdefault("weather_source", "demo")


def lang() -> str:
    return st.session_state.get("lang", "en")


def sidebar_chrome() -> None:
    init_session()
    inject_css()
    L = lang()
    with st.sidebar:
        st.markdown("### 🌱 CropGuard AI")
        st.caption(t(L, "subtitle"))
        choice = st.radio(
            "Language / भाषा / भाषा",
            options=list(LANGS.keys()),
            format_func=lambda x: LANGS[x],
            index=list(LANGS.keys()).index(st.session_state.lang),
            horizontal=True,
        )
        st.session_state.lang = choice
        L = choice
        st.markdown(f'<span class="cg-pill pill-demo">{t(L, "demo_on")}</span>', unsafe_allow_html=True)
        det = get_detector()
        weather_lbl = t(L, "demo") if st.session_state.get("weather_source") == "demo" else t(L, "connected")
        st.write("")
        st.markdown(f"**{t(L, 'ai_ready')}:** {det.status_label()}")
        st.markdown(f"**{t(L, 'weather_status')}:** {weather_lbl}")
        st.markdown(f"**{t(L, 'db_status')}:** {t(L, 'connected')} (SQLite)")
        k = kpi_counts()
        st.divider()
        st.caption("Live prototype counts")
        st.write(f"Cases: **{k['total']}** · Pending review: **{k['pending']}**")
        st.caption(t(L, "simulated"))
    st.caption(DISCLAIMER)


def status_pill(level: str) -> str:
    lv = (level or "").lower()
    cls = "pill-ok"
    if lv in ("moderate", "medium"):
        cls = "pill-warn"
    elif lv == "high":
        cls = "pill-high"
    elif lv == "critical":
        cls = "pill-crit"
    return f'<span class="cg-pill {cls}">{level}</span>'


def metric_card(title: str, value: str, sub: str = "") -> None:
    st.markdown(
        f'<div class="cg-card"><p class="cg-kicker">{title}</p>'
        f'<p class="cg-value">{value}</p><p class="cg-muted">{sub}</p></div>',
        unsafe_allow_html=True,
    )
