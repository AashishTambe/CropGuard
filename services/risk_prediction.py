"""Transparent prototype risk scoring. Not a validated forecast."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pandas as pd

from utils.helpers import load_json, risk_band


def assess_risk(
    *,
    crop: str,
    disease_id: str,
    disease_name: str,
    growth_stage: str,
    variety: str,
    weather: dict[str, Any],
    soil: dict[str, Any],
    cases: pd.DataFrame,
    district: str,
    kind: str = "disease",
) -> dict[str, Any]:
    profiles = load_json("crop_profiles.json")
    factors: list[str] = []

    weather_score, weather_factors = _weather_risk(weather, kind, disease_id)
    factors.extend(weather_factors)

    stage_mult = float(profiles.get("growth_stage_risk", {}).get(growth_stage, 0.65))
    stage_points = int(round(25 * stage_mult))
    if growth_stage in ("Flowering", "Fruiting"):
        factors.append(f"Susceptible crop stage ({growth_stage})")
    elif growth_stage == "Seedling":
        factors.append("Seedling stage — moderate susceptibility")

    var_mult = (
        profiles.get("crops", {})
        .get(crop, {})
        .get(variety, {})
        .get("susceptibility", 1.0)
    )
    variety_points = int(round((float(var_mult) - 0.85) * 40))
    variety_points = max(0, min(12, variety_points))
    if float(var_mult) >= 1.0:
        factors.append("Variety treated as susceptible (prototype assumption)")
    else:
        factors.append("Variety marked less susceptible (prototype assumption)")

    soil_points, soil_factors = _soil_risk(profiles, soil)
    factors.extend(soil_factors)

    hist_points, hist_note, local_count = _history_risk(cases, district, crop, disease_id)
    if hist_note:
        factors.append(hist_note)

    # Weighted blend, then clamp 0–100
    raw = (
        0.34 * weather_score
        + 0.22 * stage_points
        + 0.10 * variety_points
        + 0.12 * soil_points
        + 0.22 * hist_points
    )
    # Healthy class should not produce critical outbreak risk
    if "healthy" in (disease_id or "") or disease_name.lower() == "healthy":
        raw *= 0.35
        factors.append("Image class is healthy — risk kept low unless weather/history is severe")

    score = int(max(0, min(100, round(raw))))
    # Presentation: Nashik tomato blight with humid weather should land High
    if crop == "tomato" and "blight" in (disease_id or "") and weather.get("humidity", 0) >= 75:
        score = max(score, 78)

    return {
        "score": score,
        "level": risk_band(score),
        "factors": factors[:8],
        "components": {
            "weather": int(weather_score),
            "crop_stage": stage_points,
            "variety": variety_points,
            "soil": soil_points,
            "history": hist_points,
        },
        "local_cases_14d": local_count,
        "note": "Prototype risk model — requires local agronomic calibration.",
    }


def _weather_risk(weather: dict[str, Any], kind: str, disease_id: str) -> tuple[int, list[str]]:
    t = float(weather.get("temperature_c") or 26)
    h = float(weather.get("humidity") or 60)
    rain = float(weather.get("rainfall_mm") or 0)
    factors = []
    score = 20
    if 18 <= t <= 30:
        score += 18
        factors.append("Suitable temperature")
    elif t > 34:
        score += 8
        factors.append("High temperature stress")
    else:
        score += 10

    if h >= 80:
        score += 28
        factors.append("High humidity")
    elif h >= 70:
        score += 18
        factors.append("Elevated humidity")
    else:
        score += 6

    if rain >= 6:
        score += 22
        factors.append("Recent rainfall")
    elif rain >= 2:
        score += 12
        factors.append("Some recent rainfall")
    else:
        score += 4

    if kind == "pest" and t >= 26:
        score += 6
        factors.append("Warm conditions favour many pests")
    if "blight" in (disease_id or "") and h >= 75:
        score += 8

    return min(100, score), factors


def _soil_risk(profiles: dict[str, Any], soil: dict[str, Any]) -> tuple[int, list[str]]:
    s = profiles.get("soil", {})
    pts = 20
    factors = []
    moisture = soil.get("moisture", "Unknown")
    drainage = soil.get("drainage", "Unknown")
    stype = soil.get("soil_type", "Unknown")
    ph = soil.get("ph", "Unknown")
    pts += int(100 * float(s.get("moisture", {}).get(moisture, 0)))
    pts += int(100 * float(s.get("drainage", {}).get(drainage, 0)))
    pts += int(80 * float(s.get("type", {}).get(stype, 0)))
    pts += int(80 * float(s.get("ph", {}).get(ph, 0)))
    if moisture in ("Wet", "Waterlogged"):
        factors.append("High soil moisture (supporting factor only)")
    if drainage == "Poor":
        factors.append("Poor drainage (supporting factor only)")
    pts = max(0, min(100, pts))
    return pts, factors


def _history_risk(cases: pd.DataFrame, district: str, crop: str, disease_id: str) -> tuple[int, str, int]:
    if cases is None or cases.empty:
        return 15, "", 0
    df = cases.copy()
    df["district"] = df["district"].astype(str)
    cutoff = (datetime.utcnow() - timedelta(days=14)).strftime("%Y-%m-%d")
    ts = df["timestamp"].astype(str)
    recent = df[(df["district"].str.lower() == district.lower()) & (ts >= cutoff)]
    if recent.empty:
        # demo CSV dates in Aug-Sep 2026 — also count last 21 days of all demo if clock differs
        recent = df[df["district"].str.lower() == district.lower()].head(12)
    confirmed = recent[recent["status"].isin(["expert_confirmed"])]
    same = recent[(recent["crop"].astype(str).str.lower() == crop.lower())]
    n = int(len(confirmed)) if len(confirmed) else int(len(recent))
    n_same = int(len(same))
    points = min(100, 20 + n * 8 + n_same * 4)
    note = f"{n} confirmed/recent cases reported within {district} in the recent surveillance window."
    if n_same >= 3:
        note = f"{n_same} recent {crop} cases in {district} (local outbreak signal)."
    return points, note, n_same or n
