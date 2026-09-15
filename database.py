"""SQLite storage for cases, expert reviews, follow-ups, and lab referrals."""
from __future__ import annotations

import hashlib
import json
import secrets
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

from utils.helpers import DATA_DIR, utc_now

DB_PATH = DATA_DIR / "cropguard.db"


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty.")
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200000,
    )
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str | None) -> bool:
    if not password or not stored_hash or not stored_hash.startswith("pbkdf2_sha256$"):
        return False
    try:
        _, salt, expected_hex = stored_hash.split("$", 2)
    except ValueError:
        return False
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200000,
    )
    return digest.hex() == expected_hex


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = connect()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            timestamp TEXT,
            farmer_id TEXT,
            crop TEXT,
            variety TEXT,
            growth_stage TEXT,
            disease_prediction TEXT,
            disease_id TEXT,
            confidence REAL,
            latitude REAL,
            longitude REAL,
            village TEXT,
            district TEXT,
            state TEXT,
            weather_json TEXT,
            risk_score INTEGER,
            risk_level TEXT,
            status TEXT,
            image_path TEXT,
            expert_diagnosis TEXT,
            soil_json TEXT,
            notes TEXT,
            is_demo INTEGER DEFAULT 0,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS expert_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT,
            action TEXT,
            correct_diagnosis TEXT,
            severity TEXT,
            notes TEXT,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS followups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT,
            followup_date TEXT,
            severity TEXT,
            outcome TEXT,
            notes TEXT,
            image_path TEXT,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS lab_referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT,
            suspected_issue TEXT,
            notes TEXT,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ACTIVE',
            created_at TEXT,
            updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS farmer_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            full_name TEXT,
            age INTEGER,
            gender TEXT,
            farmer_type TEXT,
            farmer_category TEXT,
            state TEXT,
            district TEXT,
            taluka TEXT,
            village TEXT,
            address TEXT,
            pin_code TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS farms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            farm_name TEXT NOT NULL,
            farm_id TEXT NOT NULL UNIQUE,
            state TEXT,
            district TEXT,
            taluka TEXT,
            village TEXT,
            farm_address TEXT,
            survey_number TEXT,
            land_area REAL,
            land_unit TEXT,
            ownership_type TEXT,
            soil_type TEXT,
            irrigation_type TEXT,
            main_crop TEXT,
            crop_variety TEXT,
            sowing_date TEXT,
            expected_harvest_date TEXT,
            latitude REAL,
            longitude REAL,
            image_path TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS farm_crops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farm_id INTEGER NOT NULL,
            crop_name TEXT NOT NULL,
            crop_variety TEXT,
            sowing_date TEXT,
            expected_harvest_date TEXT,
            created_at TEXT,
            FOREIGN KEY(farm_id) REFERENCES farms(id)
        );
        """
    )
    conn.commit()
    _seed_if_empty(conn)
    seed_demo_users()
    conn.close()


def _seed_if_empty(conn: sqlite3.Connection) -> None:
    n = conn.execute("SELECT COUNT(*) AS n FROM cases").fetchone()["n"]
    if n > 0:
        return
    csv_path = DATA_DIR / "demo_cases.csv"
    if not csv_path.exists():
        return
    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        weather = {
            "temperature_c": 26.0,
            "humidity": 78,
            "rainfall_mm": 6.5,
            "wind_kmh": 9.0,
            "condition": "Humid / partly cloudy",
            "source": "demo",
        }
        conn.execute(
            """
            INSERT INTO cases (
                case_id, timestamp, farmer_id, crop, variety, growth_stage,
                disease_prediction, disease_id, confidence, latitude, longitude,
                village, district, state, weather_json, risk_score, risk_level,
                status, image_path, expert_diagnosis, soil_json, notes, is_demo, created_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                row["case_id"],
                f"{row['date']}T09:00:00Z",
                "demo_farmer",
                str(row["crop"]).lower(),
                "Generic/Unknown",
                row.get("growth_stage", "Vegetative"),
                row["disease"],
                row["disease_id"],
                float(row["confidence"]),
                float(row["latitude"]),
                float(row["longitude"]),
                row["village"],
                row["district"],
                "Maharashtra",
                json.dumps(weather),
                int(row["risk_score"]),
                _level(int(row["risk_score"])),
                row["status"],
                "",
                row["disease"] if int(row["confirmed_by_expert"]) == 1 else "",
                json.dumps({"soil_type": "Unknown", "moisture": "Unknown", "ph": "Unknown", "drainage": "Unknown"}),
                "Seeded simulated demo case",
                1,
                utc_now(),
            ),
        )
    conn.commit()


def seed_demo_users() -> None:
    conn = connect()
    existing = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]
    if existing > 0:
        conn.close()
        return

    now = utc_now()
    user_rows = [
        (
            "Farmer Demo",
            "",
            "9876543210",
            hash_password("Farmer@123"),
            "FARMER",
            "ACTIVE",
            now,
            now,
        ),
        (
            "Advisor Demo",
            "advisor@cropguard.demo",
            "",
            hash_password("Advisor@123"),
            "ADVISOR",
            "ACTIVE",
            now,
            now,
        ),
        (
            "Admin Demo",
            "admin@cropguard.demo",
            "",
            hash_password("Admin@123"),
            "ADMIN",
            "ACTIVE",
            now,
            now,
        ),
    ]
    conn.executemany(
        """
        INSERT INTO users (name, email, phone, password_hash, role, status, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?)
        """,
        user_rows,
    )
    conn.commit()

    farmer_user = conn.execute("SELECT id FROM users WHERE role = 'FARMER' AND phone = '9876543210'").fetchone()
    advisor_user = conn.execute("SELECT id FROM users WHERE role = 'ADVISOR' AND email = 'advisor@cropguard.demo'").fetchone()
    admin_user = conn.execute("SELECT id FROM users WHERE role = 'ADMIN' AND email = 'admin@cropguard.demo'").fetchone()

    if farmer_user:
        conn.execute(
            """
            INSERT INTO farmer_profiles (user_id, full_name, age, gender, farmer_type, farmer_category, state, district, taluka, village, address, pin_code, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                farmer_user["id"],
                "Farmer Demo",
                42,
                "Male",
                "Smallholder",
                "General",
                "Maharashtra",
                "Nashik",
                "Niphad",
                "Pimpalgaon",
                "Demo farm address",
                "422001",
                now,
                now,
            ),
        )
        conn.execute(
            """
            INSERT INTO farms (user_id, farm_name, farm_id, state, district, taluka, village, farm_address, survey_number, land_area, land_unit, ownership_type, soil_type, irrigation_type, main_crop, crop_variety, sowing_date, expected_harvest_date, latitude, longitude, image_path, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                farmer_user["id"],
                "Demo Farm 1",
                "FG-1001",
                "Maharashtra",
                "Nashik",
                "Niphad",
                "Pimpalgaon",
                "Demo farm address 1",
                "42/5A",
                4.5,
                "acre",
                "Owned",
                "Black cotton",
                "Drip",
                "Tomato",
                "Hybrid",
                "2026-06-15",
                "2026-10-05",
                19.9975,
                73.7898,
                "",
                now,
                now,
            ),
        )
        conn.execute(
            """
            INSERT INTO farms (user_id, farm_name, farm_id, state, district, taluka, village, farm_address, survey_number, land_area, land_unit, ownership_type, soil_type, irrigation_type, main_crop, crop_variety, sowing_date, expected_harvest_date, latitude, longitude, image_path, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                farmer_user["id"],
                "Demo Farm 2",
                "FG-1002",
                "Maharashtra",
                "Nashik",
                "Niphad",
                "Pimpalgaon",
                "Demo farm address 2",
                "82/8",
                6.2,
                "acre",
                "Leased",
                "Red",
                "Sprinkler",
                "Cotton",
                "Local",
                "2026-07-01",
                "2026-11-18",
                20.0123,
                73.8100,
                "",
                now,
                now,
            ),
        )
    conn.commit()
    conn.close()


def _level(score: int) -> str:
    if score <= 25:
        return "Low"
    if score <= 50:
        return "Moderate"
    if score <= 75:
        return "High"
    return "Critical"


def insert_case(payload: dict[str, Any]) -> str:
    conn = connect()
    conn.execute(
        """
        INSERT INTO cases (
            case_id, timestamp, farmer_id, crop, variety, growth_stage,
            disease_prediction, disease_id, confidence, latitude, longitude,
            village, district, state, weather_json, risk_score, risk_level,
            status, image_path, expert_diagnosis, soil_json, notes, is_demo, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            payload["case_id"],
            payload.get("timestamp", utc_now()),
            payload.get("farmer_id", "demo_farmer"),
            payload["crop"],
            payload.get("variety", "Generic/Unknown"),
            payload.get("growth_stage", "Vegetative"),
            payload.get("disease_prediction", ""),
            payload.get("disease_id", ""),
            payload.get("confidence", 0.0),
            payload.get("latitude"),
            payload.get("longitude"),
            payload.get("village", ""),
            payload.get("district", ""),
            payload.get("state", "Maharashtra"),
            json.dumps(payload.get("weather") or {}),
            payload.get("risk_score", 0),
            payload.get("risk_level", "Low"),
            payload.get("status", "suspected"),
            payload.get("image_path", ""),
            payload.get("expert_diagnosis", ""),
            json.dumps(payload.get("soil") or {}),
            payload.get("notes", ""),
            1 if payload.get("is_demo") else 0,
            utc_now(),
        ),
    )
    conn.commit()
    conn.close()
    return payload["case_id"]


def list_cases() -> pd.DataFrame:
    conn = connect()
    df = pd.read_sql_query("SELECT * FROM cases ORDER BY timestamp DESC", conn)
    conn.close()
    return df


def get_case(case_id: str) -> dict[str, Any] | None:
    conn = connect()
    row = conn.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_case(case_id: str, **fields: Any) -> None:
    if not fields:
        return
    allowed = {
        "status",
        "expert_diagnosis",
        "notes",
        "disease_prediction",
        "disease_id",
        "risk_score",
        "risk_level",
    }
    sets = []
    vals = []
    for k, v in fields.items():
        if k in allowed:
            sets.append(f"{k} = ?")
            vals.append(v)
    if not sets:
        return
    vals.append(case_id)
    conn = connect()
    conn.execute(f"UPDATE cases SET {', '.join(sets)} WHERE case_id = ?", vals)
    conn.commit()
    conn.close()


def pending_expert_cases() -> pd.DataFrame:
    conn = connect()
    df = pd.read_sql_query(
        """
        SELECT * FROM cases
        WHERE status IN ('pending_review', 'suspected', 'lab_referred')
        ORDER BY CASE WHEN status = 'pending_review' THEN 0 ELSE 1 END, timestamp DESC
        """,
        conn,
    )
    conn.close()
    return df


def add_review(case_id: str, action: str, diagnosis: str, severity: str, notes: str) -> None:
    conn = connect()
    conn.execute(
        """
        INSERT INTO expert_reviews (case_id, action, correct_diagnosis, severity, notes, created_at)
        VALUES (?,?,?,?,?,?)
        """,
        (case_id, action, diagnosis, severity, notes, utc_now()),
    )
    conn.commit()
    conn.close()
    status_map = {
        "confirm": "expert_confirmed",
        "reject": "rejected",
        "needs_lab": "lab_referred",
    }
    update_case(
        case_id,
        status=status_map.get(action, "pending_review"),
        expert_diagnosis=diagnosis,
        notes=notes,
    )


def add_followup(case_id: str, date: str, severity: str, outcome: str, notes: str, image_path: str = "") -> None:
    conn = connect()
    conn.execute(
        """
        INSERT INTO followups (case_id, followup_date, severity, outcome, notes, image_path, created_at)
        VALUES (?,?,?,?,?,?,?)
        """,
        (case_id, date, severity, outcome, notes, image_path, utc_now()),
    )
    conn.commit()
    conn.close()


def list_followups(case_id: str | None = None) -> pd.DataFrame:
    conn = connect()
    if case_id:
        df = pd.read_sql_query(
            "SELECT * FROM followups WHERE case_id = ? ORDER BY followup_date, id",
            conn,
            params=(case_id,),
        )
    else:
        df = pd.read_sql_query("SELECT * FROM followups ORDER BY created_at DESC", conn)
    conn.close()
    return df


def add_referral(case_id: str, suspected: str, notes: str) -> None:
    conn = connect()
    conn.execute(
        """
        INSERT INTO lab_referrals (case_id, suspected_issue, notes, created_at)
        VALUES (?,?,?,?)
        """,
        (case_id, suspected, notes, utc_now()),
    )
    conn.commit()
    conn.close()
    update_case(case_id, status="lab_referred")


def list_referrals() -> pd.DataFrame:
    conn = connect()
    df = pd.read_sql_query("SELECT * FROM lab_referrals ORDER BY created_at DESC", conn)
    conn.close()
    return df


def kpi_counts() -> dict[str, int]:
    df = list_cases()
    if df.empty:
        return {
            "total": 0,
            "confirmed": 0,
            "pending": 0,
            "lab": 0,
            "high_risk": 0,
            "followups": 0,
        }
    follow = list_followups()
    return {
        "total": int(len(df)),
        "confirmed": int((df["status"] == "expert_confirmed").sum()),
        "pending": int(df["status"].isin(["pending_review", "suspected"]).sum()),
        "lab": int((df["status"] == "lab_referred").sum()),
        "high_risk": int(df["risk_level"].isin(["High", "Critical"]).sum()),
        "followups": int(len(follow)),
    }


def learning_loop_stats() -> dict[str, Any]:
    df = list_cases()
    reviews = pd.DataFrame()
    conn = connect()
    reviews = pd.read_sql_query("SELECT * FROM expert_reviews", conn)
    conn.close()
    total = int(len(df))
    confirmed = int((df["status"] == "expert_confirmed").sum()) if total else 0
    pending = int((df["status"] == "pending_review").sum()) if total else 0
    corrections = 0
    if not reviews.empty:
        corrections = int((reviews["action"] == "reject").sum())
    rate = round(100 * corrections / max(len(reviews), 1), 1) if not reviews.empty else 0.0
    return {
        "total_predictions": total,
        "expert_confirmed": confirmed,
        "correction_rate": rate,
        "pending_review": pending,
    }
