"""Lightweight MVP checks — run: python tests/test_mvp.py"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
from PIL import Image

import database as db
from services.advisory import farmer_action_list, get_advisory
from services.disease_detection import DiseaseDetector
from services.geospatial import detect_hotspots
from services.i18n import t
from services.risk_prediction import assess_risk
from services.weather import demo_weather, fetch_weather
from utils.helpers import new_case_id


def _blank_leaf() -> Image.Image:
    arr = np.zeros((220, 220, 3), dtype=np.uint8)
    arr[..., 1] = 90
    arr[..., 0] = 40
    return Image.fromarray(arr, "RGB")


def test_demo_prediction() -> None:
    det = DiseaseDetector()
    assert det.mode in ("demo", "model")
    pred = det.predict(_blank_leaf(), "tomato")
    assert pred["disease"]
    assert 0 < pred["confidence"] <= 1
    assert pred["top3"]
    if det.mode == "demo":
        assert "Demo prediction" in (pred.get("note") or "")
        assert pred["disease"] == "Early Blight"
        assert abs(pred["confidence"] - 0.87) < 0.02


def test_weather_fallback() -> None:
    w = fetch_weather(19.99, 73.78, "Nashik", timeout=0.01)
    assert "temperature_c" in w
    assert w.get("source") in ("demo", "open-meteo")
    d = demo_weather("Nashik")
    assert d["humidity"] >= 70


def test_risk_engine() -> None:
    db.init_db()
    cases = db.list_cases()
    weather = demo_weather("Nashik")
    soil = {"soil_type": "Unknown", "moisture": "Wet", "ph": "Unknown", "drainage": "Poor"}
    high = assess_risk(
        crop="tomato",
        disease_id="tomato_early_blight",
        disease_name="Early Blight",
        growth_stage="Fruiting",
        variety="Local variety",
        weather=weather,
        soil=soil,
        cases=cases,
        district="Nashik",
        kind="disease",
    )
    low_stage = assess_risk(
        crop="tomato",
        disease_id="tomato_early_blight",
        disease_name="Early Blight",
        growth_stage="Seedling",
        variety="Hybrid",
        weather={"temperature_c": 20, "humidity": 40, "rainfall_mm": 0},
        soil={"soil_type": "Unknown", "moisture": "Dry", "ph": "Unknown", "drainage": "Good"},
        cases=cases,
        district="Solapur",
        kind="disease",
    )
    assert high["score"] >= 70
    assert high["level"] in ("High", "Critical")
    assert high["factors"]
    assert low_stage["score"] < high["score"]
    assert "Prototype risk model" in high["note"]


def test_advisory() -> None:
    adv = get_advisory("maize_fall_armyworm")
    assert "Inspect" in adv["immediate_action"]
    assert "dose" not in adv["chemical_control_category"].lower() or "no brand" in adv["safety_notes"].lower()
    assert "label" in adv["chemical_control_category"].lower()
    actions = farmer_action_list("tomato_early_blight", False)
    assert len(actions) >= 4


def test_database_roundtrip() -> None:
    db.init_db()
    cid = new_case_id()
    db.insert_case(
        {
            "case_id": cid,
            "crop": "tomato",
            "disease_prediction": "Early Blight",
            "disease_id": "tomato_early_blight",
            "confidence": 0.87,
            "latitude": 19.9975,
            "longitude": 73.7898,
            "village": "Niphad",
            "district": "Nashik",
            "risk_score": 78,
            "risk_level": "High",
            "status": "pending_review",
            "growth_stage": "Fruiting",
            "is_demo": True,
        }
    )
    row = db.get_case(cid)
    assert row and row["crop"] == "tomato"
    df = db.list_cases()
    assert not df.empty
    db.add_review(cid, "confirm", "Early Blight", "moderate", "Matches field signs.")
    row = db.get_case(cid)
    assert row["status"] == "expert_confirmed"


def test_hotspots() -> None:
    db.init_db()
    hs = detect_hotspots(db.list_cases())
    assert isinstance(hs, list)


def test_i18n() -> None:
    assert "CropGuard" in t("en", "app_name")
    assert t("hi", "submit_case")
    assert t("mr", "submit_case")


def main() -> int:
    tests = [
        test_demo_prediction,
        test_weather_fallback,
        test_risk_engine,
        test_advisory,
        test_database_roundtrip,
        test_hotspots,
        test_i18n,
    ]
    failed = 0
    for fn in tests:
        try:
            fn()
            print(f"OK  {fn.__name__}")
        except Exception as exc:
            failed += 1
            print(f"FAIL {fn.__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
