"""Authentication, role checks, and secure session helpers for CropGuard."""
from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Any

import streamlit as st

from database import connect, hash_password, init_db, verify_password

ROLES = ("FARMER", "ADVISOR", "ADMIN")


def normalize_value(value: Any) -> str:
    return (str(value or "")).strip()


def verify_phone(value: Any) -> bool:
    phone = re.sub(r"\D", "", normalize_value(value))
    return len(phone) == 10 and phone.startswith(("6", "7", "8", "9")) and phone != "0000000000"


def verify_email(value: Any) -> bool:
    email = normalize_value(value)
    return bool(re.fullmatch(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email))


def get_current_user() -> dict[str, Any] | None:
    session_user = st.session_state.get("auth_user")
    if not session_user:
        return None
    if isinstance(session_user, dict):
        return session_user
    return None


def logout() -> None:
    st.session_state.pop("auth_user", None)
    st.session_state.pop("auth_token", None)
    st.session_state.pop("user_role", None)
    st.session_state.pop("last_login_error", None)


def require_auth(required_role: str | None = None) -> dict[str, Any] | None:
    user = get_current_user()
    if user is None:
        st.warning("Please log in to continue.")
        st.switch_page("pages/0_Login.py")
        st.stop()

    if required_role and user.get("role") != required_role:
        role_name = user.get("role", "USER").title()
        st.error(f"You don't have permission to access this page.")
        if user.get("role") == "FARMER":
            st.switch_page("pages/10_Farmer_Dashboard.py")
        elif user.get("role") == "ADVISOR":
            st.switch_page("pages/20_Advisor_Dashboard.py")
        elif user.get("role") == "ADMIN":
            st.switch_page("pages/30_Admin_Dashboard.py")
        else:
            st.switch_page("pages/0_Login.py")
        st.stop()

    return user


def require_role(role: str) -> dict[str, Any] | None:
    return require_auth(role)


def _serialize_user(row: Any) -> dict[str, Any] | None:
    if row is None:
        return None
    data = dict(row)
    data.pop("password_hash", None)
    return data


def fetch_user_by_role(role: str, identifier: str) -> dict[str, Any] | None:
    if role not in ROLES:
        return None
    identifier = normalize_value(identifier)
    if not identifier:
        return None

    init_db()
    conn = connect()
    try:
        if role == "FARMER":
            if not verify_phone(identifier):
                return None
            row = conn.execute(
                "SELECT * FROM users WHERE role = ? AND phone = ? LIMIT 1",
                (role, identifier),
            ).fetchone()
        else:
            if not verify_email(identifier):
                return None
            row = conn.execute(
                "SELECT * FROM users WHERE role = ? AND email = ? LIMIT 1",
                (role, identifier),
            ).fetchone()
        return _serialize_user(row)
    finally:
        conn.close()


def authenticate_user(role: str, identifier: str, password: str) -> dict[str, Any] | None:
    role = (role or "").upper()
    identifier = normalize_value(identifier)
    password = str(password or "")

    if role not in ROLES or not identifier or not password:
        return None

    if role == "FARMER":
        if not verify_phone(identifier):
            return None
        query = "SELECT * FROM users WHERE role = ? AND phone = ? LIMIT 1"
        params = (role, identifier)
    else:
        if not verify_email(identifier):
            return None
        query = "SELECT * FROM users WHERE role = ? AND email = ? LIMIT 1"
        params = (role, identifier)

    init_db()
    conn = connect()
    try:
        row = conn.execute(query, params).fetchone()
        if row is None:
            return None
        if row["status"] != "ACTIVE":
            return {
                "id": row["id"],
                "name": row["name"],
                "role": row["role"],
                "status": row["status"],
                "error": "inactive",
            }
        if not verify_password(password, row["password_hash"]):
            return None
        user = dict(row)
        user.pop("password_hash", None)
        return user
    finally:
        conn.close()


def get_role_dashboard(role: str) -> str:
    mapping = {
        "FARMER": "pages/10_Farmer_Dashboard.py",
        "ADVISOR": "pages/20_Advisor_Dashboard.py",
        "ADMIN": "pages/30_Admin_Dashboard.py",
    }
    return mapping.get(role, "pages/0_Login.py")


def create_farmer_account(payload: dict[str, Any]) -> dict[str, Any]:
    name = normalize_value(payload.get("full_name") or payload.get("name"))
    phone = normalize_value(payload.get("phone"))
    password = str(payload.get("password") or "")
    if not name or not verify_phone(phone):
        raise ValueError("Valid personal details and a valid Indian mobile number are required.")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")

    init_db()
    conn = connect()
    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE phone = ? OR email = ? LIMIT 1",
            (phone, normalize_value(payload.get("email") or "")),
        ).fetchone()
        if existing is not None:
            raise ValueError("A user with this mobile number already exists.")

        user_id = conn.execute(
            """
            INSERT INTO users (name, email, phone, password_hash, role, status, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                name,
                normalize_value(payload.get("email") or ""),
                phone,
                hash_password(password),
                "FARMER",
                "ACTIVE",
                datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            ),
        ).lastrowid

        conn.execute(
            """
            INSERT INTO farmer_profiles (user_id, full_name, age, gender, farmer_type, farmer_category, state, district, taluka, village, address, pin_code, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                user_id,
                name,
                int(payload.get("age") or 0) or None,
                normalize_value(payload.get("gender") or ""),
                normalize_value(payload.get("farmer_type") or ""),
                normalize_value(payload.get("farmer_category") or ""),
                normalize_value(payload.get("state") or ""),
                normalize_value(payload.get("district") or ""),
                normalize_value(payload.get("taluka") or ""),
                normalize_value(payload.get("village") or ""),
                normalize_value(payload.get("address") or ""),
                normalize_value(payload.get("pin_code") or ""),
                datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            ),
        )

        farms = payload.get("farms") or []
        for idx, farm in enumerate(farms, 1):
            farm_name = normalize_value(farm.get("farm_name") or f"Farm {idx}")
            if not farm_name:
                continue
            farm_id = normalize_value(farm.get("farm_id") or f"FG-{uuid.uuid4().hex[:8].upper()}")
            conn.execute(
                """
                INSERT INTO farms (user_id, farm_name, farm_id, state, district, taluka, village, farm_address, survey_number, land_area, land_unit, ownership_type, soil_type, irrigation_type, main_crop, crop_variety, sowing_date, expected_harvest_date, latitude, longitude, image_path, created_at, updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    user_id,
                    farm_name,
                    farm_id,
                    normalize_value(farm.get("state") or ""),
                    normalize_value(farm.get("district") or ""),
                    normalize_value(farm.get("taluka") or ""),
                    normalize_value(farm.get("village") or ""),
                    normalize_value(farm.get("farm_address") or ""),
                    normalize_value(farm.get("survey_number") or ""),
                    float(farm.get("land_area") or 0.0) if str(farm.get("land_area") or "").strip() else 0.0,
                    normalize_value(farm.get("land_unit") or "acre"),
                    normalize_value(farm.get("ownership_type") or "Owned"),
                    normalize_value(farm.get("soil_type") or "Unknown"),
                    normalize_value(farm.get("irrigation_type") or "Drip"),
                    normalize_value(farm.get("main_crop") or ""),
                    normalize_value(farm.get("crop_variety") or ""),
                    normalize_value(farm.get("sowing_date") or ""),
                    normalize_value(farm.get("expected_harvest_date") or ""),
                    float(farm.get("latitude") or 0.0) if str(farm.get("latitude") or "").strip() else None,
                    float(farm.get("longitude") or 0.0) if str(farm.get("longitude") or "").strip() else None,
                    normalize_value(farm.get("image_path") or ""),
                    datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                ),
            )

            crop_name = normalize_value(farm.get("main_crop") or "")
            if crop_name:
                conn.execute(
                    "INSERT INTO farm_crops (farm_id, crop_name, crop_variety, sowing_date, expected_harvest_date, created_at) VALUES ((SELECT id FROM farms WHERE farm_id = ?), ?, ?, ?, ?, ?)",
                    (
                        farm_id,
                        crop_name,
                        normalize_value(farm.get("crop_variety") or ""),
                        normalize_value(farm.get("sowing_date") or ""),
                        normalize_value(farm.get("expected_harvest_date") or ""),
                        datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    ),
                )

        conn.commit()
        created = conn.execute("SELECT * FROM users WHERE id = ? LIMIT 1", (user_id,)).fetchone()
        return dict(created)
    finally:
        conn.close()
