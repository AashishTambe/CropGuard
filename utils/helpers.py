"""Shared helpers for CropGuard AI."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DISCLAIMER = (
    "This prototype provides decision support and does not replace diagnosis by "
    "qualified agricultural experts or laboratories. Always follow locally approved "
    "agricultural recommendations and product labels."
)

DEMO_BANNER = "SIMULATED DEMO DATA — NOT REAL GOVERNMENT SURVEILLANCE DATA"

MAHARASHTRA_LOCATIONS = {
    "Pune": {
        "district": "Pune",
        "state": "Maharashtra",
        "lat": 18.5204,
        "lon": 73.8567,
        "villages": ["Haveli", "Baramati", "Khed", "Junnar", "Daund", "Indapur"],
    },
    "Nashik": {
        "district": "Nashik",
        "state": "Maharashtra",
        "lat": 19.9975,
        "lon": 73.7898,
        "villages": ["Niphad", "Dindori", "Sinnar", "Igatpuri", "Yeola", "Malegaon"],
    },
    "Nagpur": {
        "district": "Nagpur",
        "state": "Maharashtra",
        "lat": 21.1458,
        "lon": 79.0882,
        "villages": ["Kalmeshwar", "Katol", "Saoner", "Umred", "Ramtek", "Parseoni"],
    },
    "Amravati": {
        "district": "Amravati",
        "state": "Maharashtra",
        "lat": 20.9374,
        "lon": 77.7796,
        "villages": ["Achalpur", "Daryapur", "Morshi", "Warud", "Anjangaon", "Chandur Bazar"],
    },
    "Latur": {
        "district": "Latur",
        "state": "Maharashtra",
        "lat": 18.4088,
        "lon": 76.5604,
        "villages": ["Udgir", "Nilanga", "Ausa", "Chakur", "Ahmedpur", "Renapur"],
    },
    "Solapur": {
        "district": "Solapur",
        "state": "Maharashtra",
        "lat": 17.6599,
        "lon": 75.9064,
        "villages": ["Pandharpur", "Barshi", "Akkalkot", "Mangalvedha", "Sangola", "Mohol"],
    },
    "Kolhapur": {
        "district": "Kolhapur",
        "state": "Maharashtra",
        "lat": 16.7050,
        "lon": 74.2433,
        "villages": ["Hatkanangale", "Panhala", "Radhanagari", "Kagal", "Shirol", "Gaganbawada"],
    },
}

GROWTH_STAGES = ["Seedling", "Vegetative", "Flowering", "Fruiting", "Maturity"]
SOIL_TYPES = ["Unknown", "Black cotton", "Red", "Alluvial", "Laterite", "Sandy"]
SOIL_MOISTURE = ["Unknown", "Dry", "Adequate", "Wet", "Waterlogged"]
SOIL_PH = ["Unknown", "Acidic (<6.5)", "Neutral (6.5-7.5)", "Alkaline (>7.5)"]
DRAINAGE = ["Unknown", "Good", "Moderate", "Poor"]
OUTCOMES = ["Improved", "Stable", "Worsened", "Resolved", "Unknown"]


def load_json(name: str) -> dict[str, Any]:
    path = DATA_DIR / name
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def crop_catalog() -> dict[str, Any]:
    return load_json("diseases.json")


def crop_keys() -> list[str]:
    return list(crop_catalog()["crops"].keys())


def crop_label(crop_key: str) -> str:
    crops = crop_catalog()["crops"]
    return crops.get(crop_key, {}).get("label", crop_key.title())


def variety_options(crop_key: str) -> list[str]:
    return crop_catalog()["crops"].get(crop_key, {}).get("varieties", ["Generic/Unknown"])


def class_name(crop_key: str, class_id: str) -> str:
    for item in crop_catalog()["crops"].get(crop_key, {}).get("classes", []):
        if item["id"] == class_id:
            return item["name"]
    return class_id.replace("_", " ").title()


def class_kind(crop_key: str, class_id: str) -> str:
    for item in crop_catalog()["crops"].get(crop_key, {}).get("classes", []):
        if item["id"] == class_id:
            return item.get("kind", "disease")
    return "disease"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def new_case_id() -> str:
    return f"CG-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


def save_upload(file_bytes: bytes, suffix: str = ".jpg") -> str:
    name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{suffix}"
    dest = UPLOAD_DIR / name
    dest.write_bytes(file_bytes)
    return name


def image_quality_report(image: Image.Image) -> dict[str, Any]:
    """Blur / size check. Does not diagnose disease."""
    arr = np.array(image.convert("L"))
    h, w = arr.shape[:2]
    too_small = min(h, w) < 160
    # Laplacian-like sharpness via numpy (no OpenCV required)
    gy, gx = np.gradient(arr.astype(np.float32))
    sharpness = float(np.mean(gx**2 + gy**2))
    poor = too_small or sharpness < 18.0
    return {
        "width": int(w),
        "height": int(h),
        "sharpness": round(sharpness, 1),
        "poor": poor,
        "message": (
            "Image quality is low. Please capture a clear image of the affected leaf/plant."
            if poor
            else "Image quality looks acceptable for a first screening."
        ),
    }


def confidence_band(score: float) -> str:
    if score >= 0.85:
        return "high"
    if score >= 0.60:
        return "moderate"
    return "low"


def risk_band(score: int) -> str:
    if score <= 25:
        return "Low"
    if score <= 50:
        return "Moderate"
    if score <= 75:
        return "High"
    return "Critical"


def display_image_name(filename: str | None) -> str:
    if not filename:
        return "No image"
    return Path(filename).name
