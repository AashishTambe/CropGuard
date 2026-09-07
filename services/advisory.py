"""Controlled IPM advisories from JSON. No invented pesticide doses."""
from __future__ import annotations

from typing import Any

from utils.helpers import load_json


def get_advisory(disease_id: str) -> dict[str, str]:
    data = load_json("advisories.json")
    items = data.get("items", {})
    fallback = data.get("fallback", {})
    row = items.get(disease_id) or fallback
    out = {**fallback, **row}
    out["disclaimer"] = data.get(
        "disclaimer",
        "Follow the product label and locally approved agricultural guidance.",
    )
    return out


def farmer_action_list(disease_id: str, is_healthy: bool) -> list[str]:
    if is_healthy:
        return [
            "Keep weekly scouting notes.",
            "Watch weather — humidity and rain can raise risk even if the plant looks healthy today.",
            "Do not spray 'just in case' without local advice.",
            "Contact the extension officer if new spots or insects appear suddenly.",
        ]
    adv = get_advisory(disease_id)
    return [
        "Inspect nearby plants in a zigzag walk.",
        adv.get("immediate_action", "Inspect the affected area today."),
        "Improve field sanitation and avoid conditions that keep leaves wet.",
        "Follow approved IPM guidance (monitoring → cultural → biological → chemical last).",
        adv.get("when_to_contact_officer", "Contact the agriculture extension officer if symptoms continue spreading."),
    ]


def advisory_speech_text(disease_name: str, risk_level: str, actions: list[str], lang_note: str = "") -> str:
    parts = [
        f"Likely issue: {disease_name}.",
        f"Risk level: {risk_level}.",
        "Recommended actions:",
        *actions[:5],
        "This is decision support, not a laboratory diagnosis.",
    ]
    if lang_note:
        parts.insert(0, lang_note)
    return " ".join(parts)
