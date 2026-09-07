"""SQLite storage for cases, expert reviews, follow-ups, and lab referrals."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

from utils.helpers import DATA_DIR, utc_now

DB_PATH = DATA_DIR / "cropguard.db"


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
        """
    )
    conn.commit()
    _seed_if_empty(conn)
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
