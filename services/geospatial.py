"""Simple hotspot clustering for the Maharashtra demo map."""
from __future__ import annotations

from typing import Any

import folium
import pandas as pd

try:
    from sklearn.cluster import DBSCAN
except Exception:  # pragma: no cover
    DBSCAN = None


STATUS_COLORS = {
    "expert_confirmed": "darkred",
    "suspected": "orange",
    "pending_review": "blue",
    "lab_referred": "purple",
    "rejected": "gray",
}

RISK_COLORS = {
    "Low": "green",
    "Moderate": "orange",
    "High": "red",
    "Critical": "darkred",
}


def detect_hotspots(df: pd.DataFrame, eps_deg: float = 0.35, min_samples: int = 3) -> list[dict[str, Any]]:
    if df is None or df.empty or len(df) < min_samples:
        return []
    work = df.dropna(subset=["latitude", "longitude"]).copy()
    if work.empty:
        return []
    work["crop"] = work["crop"].astype(str).str.lower()
    work["disease_prediction"] = work["disease_prediction"].astype(str)
    hotspots: list[dict[str, Any]] = []
    grouped = work.groupby(["crop", "disease_prediction"], dropna=False)
    for (crop, disease), g in grouped:
        if len(g) < min_samples:
            continue
        coords = g[["latitude", "longitude"]].astype(float).values
        if DBSCAN is None:
            # District fallback
            for district, gd in g.groupby("district"):
                if len(gd) >= min_samples:
                    hotspots.append(
                        {
                            "crop": crop,
                            "disease": disease,
                            "district": str(district),
                            "count": int(len(gd)),
                            "lat": float(gd["latitude"].mean()),
                            "lon": float(gd["longitude"].mean()),
                            "label": f"{district} — {str(crop).title()} — {disease}",
                        }
                    )
            continue
        labels = DBSCAN(eps=eps_deg, min_samples=min_samples).fit_predict(coords)
        g = g.copy()
        g["cluster"] = labels
        for cid, cg in g.groupby("cluster"):
            if int(cid) < 0:
                continue
            district = str(cg["district"].mode().iloc[0]) if not cg["district"].mode().empty else ""
            hotspots.append(
                {
                    "crop": crop,
                    "disease": disease,
                    "district": district,
                    "count": int(len(cg)),
                    "lat": float(cg["latitude"].mean()),
                    "lon": float(cg["longitude"].mean()),
                    "label": f"{district} — {str(crop).title()} — {disease}",
                }
            )
    hotspots.sort(key=lambda x: x["count"], reverse=True)
    return hotspots


def build_map(df: pd.DataFrame, hotspots: list[dict[str, Any]] | None = None) -> folium.Map:
    center = [19.75, 75.7]
    fmap = folium.Map(location=center, zoom_start=6, tiles="CartoDB positron")
    folium.Marker(
        [19.0, 76.5],
        icon=folium.DivIcon(
            html='<div style="font-size:11px;color:#7a1f1f;background:#fff3cd;padding:4px 8px;border:1px solid #c9a227;border-radius:4px;">Demo surveillance data</div>'
        ),
    ).add_to(fmap)
    if df is None or df.empty:
        return fmap
    work = df.dropna(subset=["latitude", "longitude"])
    for _, row in work.iterrows():
        color = STATUS_COLORS.get(str(row.get("status")), "cadetblue")
        popup = (
            f"<b>{row.get('case_id')}</b><br>"
            f"{row.get('crop')} — {row.get('disease_prediction')}<br>"
            f"{row.get('village')}, {row.get('district')}<br>"
            f"Status: {row.get('status')}<br>"
            f"Risk: {row.get('risk_level')} ({row.get('risk_score')})"
        )
        folium.CircleMarker(
            location=[float(row["latitude"]), float(row["longitude"])],
            radius=7,
            color=color,
            fill=True,
            fill_opacity=0.85,
            popup=popup,
            tooltip=f"{row.get('district')} | {row.get('disease_prediction')}",
        ).add_to(fmap)
    for hs in hotspots or []:
        folium.Circle(
            location=[hs["lat"], hs["lon"]],
            radius=18000,
            color="#b71c1c",
            fill=True,
            fill_opacity=0.08,
            popup=f"Potential hotspot: {hs['label']} ({hs['count']} cases)",
        ).add_to(fmap)
    return fmap
