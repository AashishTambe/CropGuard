"""CropGuard login portal."""
from __future__ import annotations

import streamlit as st

from services.auth import ROLES, authenticate_user, get_current_user, logout

st.set_page_config(page_title="CropGuard · Login", page_icon="🌱", layout="wide")

from utils.ui import inject_public_layout_css

inject_public_layout_css()

if get_current_user():
    role = get_current_user()["role"]
    from services.auth import get_role_dashboard

    st.switch_page(get_role_dashboard(role))

st.markdown(
    """
    <style>
    .login-shell { max-width: 680px; width: min(680px, 94vw); margin: 0 auto; padding: 0.5rem 0 1rem; display: flex; flex-direction: column; justify-content: center; }
    .cg-login-card { background: #ffffff; border-radius: 26px; border: 1px solid #dfe9df; box-shadow: 0 18px 45px rgba(22,55,32,.08); padding: 1.6rem; }
    .brand-row { text-align: center; margin-bottom: 1rem; }
    .brand-mark { display: inline-flex; align-items: center; justify-content: center; width: 66px; height: 66px; border-radius: 18px; background: linear-gradient(135deg, #1b7f3a, #0b5d2a); color: white; font-size: 1.8rem; }
    .cg-tag { display: inline-block; background: #edf8ee; color: #13572f; border-radius: 999px; padding: 0.35rem 0.8rem; font-size: .72rem; font-weight: 700; letter-spacing: .11em; text-transform: uppercase; margin-bottom: .6rem; }
    .role-button { width: 100%; border-radius: 12px; min-height: 44px; }
    .role-button.selected { background: #1b7f3a; color: white; }
    .muted { color: #597160; }
    .helper { font-size: 0.92rem; color: #496150; }
    .main-wrap { min-height: -1vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(160deg, #f1f8ef 0%, #f8faf7 100%); }
    .login-form-wrap { margin-top: 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


if "selected_role" not in st.session_state:
    st.session_state.selected_role = "FARMER"


st.markdown('<div class="main-wrap"><div class="login-shell">', unsafe_allow_html=True)

st.markdown(
        """
        <div class="cg-login-card">
            <div class="brand-row">
                <div class="brand-mark">🌾</div>
            </div>
            <div class="brand-row"><span class="cg-tag">CropGuard</span></div>
            <h2 style="text-align:center; margin:0; color:#17351f;">Smart Crop Protection</h2>
            <p style="text-align:center; margin:.35rem 0 1rem; color:#55685a;">Protecting Crops. Empowering Farmers.</p>
            <h3 style="text-align:center; margin:0 0 1rem; color:#17351f;">Login to CropGuard</h3>
        </div>
        """,
        unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)

role_cols = st.columns(3)
for idx, role in enumerate(ROLES):
    with role_cols[idx]:
        selected = st.session_state.selected_role == role
        if st.button(
            role.title(),
            key=f"role_{role}",
            type="primary" if selected else "secondary",
            use_container_width=True,
        ):
            st.session_state.selected_role = role
            st.rerun()

st.markdown("<div class='login-form-wrap'><div class='cg-login-card'>", unsafe_allow_html=True)

selected_role = st.session_state.selected_role

if selected_role == "FARMER":
    st.markdown("### Farmer Login")
    with st.form("farmer_login_form", clear_on_submit=False):
        mobile = st.text_input("Mobile Number", placeholder="+91 98765 43210", max_chars=15)
        show_password = st.checkbox("Show password")
        pw = st.text_input("Password", type="text" if show_password else "password", placeholder="Enter your password")
        remember = st.checkbox("Remember me")
        login_btn = st.form_submit_button("Login as Farmer", use_container_width=True, type="primary", disabled=st.session_state.get("auth_busy", False))
        if login_btn:
            st.session_state.auth_busy = True
            if not mobile:
                st.error("Mobile number is required.")
            elif not pw:
                st.error("Password is required.")
            elif not any(ch.isdigit() for ch in mobile):
                st.error("Invalid mobile number.")
            else:
                with st.spinner("Logging in..."):
                    user = authenticate_user("FARMER", mobile, pw)
                if user is None:
                    st.error("Incorrect credentials. Please try again.")
                elif user.get("error") == "inactive":
                    st.error("Your account is currently inactive.")
                else:
                    st.session_state.auth_user = user
                    st.session_state.auth_busy = False
                    st.success("Login successful.")
                    st.switch_page("pages/10_Farmer_Dashboard.py")
            st.session_state.auth_busy = False

    st.markdown("<div class='helper'><a href='#' onclick=\"window.location='?page=Forgot%20Password'\">Forgot Password?</a></div>", unsafe_allow_html=True)
    st.write("Don't have an account?")
    if st.button("Register as Farmer", use_container_width=True):
        st.switch_page("pages/8_Register_Farmer.py")

elif selected_role == "ADVISOR":
    st.markdown("### Advisor Login")
    with st.form("advisor_login_form", clear_on_submit=False):
        email = st.text_input("Email", placeholder="advisor@cropguard.demo")
        show_password = st.checkbox("Show password")
        pw = st.text_input("Password", type="text" if show_password else "password")
        remember = st.checkbox("Remember me")
        login_btn = st.form_submit_button("Login as Advisor", use_container_width=True, type="primary", disabled=st.session_state.get("auth_busy", False))
        if login_btn:
            st.session_state.auth_busy = True
            if not email:
                st.error("Email is required.")
            elif "@" not in email:
                st.error("Invalid email address.")
            elif not pw:
                st.error("Password is required.")
            else:
                with st.spinner("Logging in..."):
                    user = authenticate_user("ADVISOR", email, pw)
                if user is None:
                    st.error("Incorrect credentials. Please try again.")
                elif user.get("error") == "inactive":
                    st.error("Your account is currently inactive.")
                else:
                    st.session_state.auth_user = user
                    st.session_state.auth_busy = False
                    st.success("Login successful.")
                    st.switch_page("pages/20_Advisor_Dashboard.py")
            st.session_state.auth_busy = False

    st.markdown("<div class='helper'>Forgot Password?</div>", unsafe_allow_html=True)

else:
    st.markdown("### Admin Login")
    with st.form("admin_login_form", clear_on_submit=False):
        email = st.text_input("Email", placeholder="admin@cropguard.demo")
        show_password = st.checkbox("Show password")
        pw = st.text_input("Password", type="text" if show_password else "password")
        login_btn = st.form_submit_button("Login as Admin", use_container_width=True, type="primary", disabled=st.session_state.get("auth_busy", False))
        if login_btn:
            st.session_state.auth_busy = True
            if not email:
                st.error("Email is required.")
            elif "@" not in email:
                st.error("Invalid email address.")
            elif not pw:
                st.error("Password is required.")
            else:
                with st.spinner("Logging in..."):
                    user = authenticate_user("ADMIN", email, pw)
                if user is None:
                    st.error("Incorrect credentials. Please try again.")
                elif user.get("error") == "inactive":
                    st.error("Your account is currently inactive.")
                else:
                    st.session_state.auth_user = user
                    st.session_state.auth_busy = False
                    st.success("Login successful.")
                    st.switch_page("pages/30_Admin_Dashboard.py")
            st.session_state.auth_busy = False

    st.markdown("<div class='helper'>Forgot Password?</div>", unsafe_allow_html=True)

st.markdown("</div></div></div></div>", unsafe_allow_html=True)

st.markdown("<div class='helper' style='text-align:center; margin-top:1rem;'>Demo credentials: Farmer 9876543210 / Farmer@123</div>", unsafe_allow_html=True)
