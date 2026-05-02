from typing import List


def build_action_plan(
    *,
    water_l_m2: float,
    pest_risk: str,
    crop_type: str,
    soil_moisture_pct: float,
    rain_mm: float,
) -> List[str]:
    actions: List[str] = []

    if water_l_m2 >= 4.5:
        actions.append(
            f"Schedule a primary irrigation event today for {crop_type} and check sector uniformity."
        )
    elif water_l_m2 >= 2.5:
        actions.append(
            f"Apply a moderate irrigation event today in {crop_type}; avoid unnecessary crop stress."
        )
    else:
        actions.append(
            "Keep irrigation short or maintenance-level; estimated water demand is limited."
        )

    if soil_moisture_pct < 18:
        actions.append(
            "Declared soil moisture is low; validate it with a probe or field inspection."
        )
    elif soil_moisture_pct > 30 and water_l_m2 < 2.5:
        actions.append(
            "There is room to stay conservative with irrigation if the soil profile remains wet."
        )

    if rain_mm > 1.0:
        actions.append(
            "Recent rainfall reduces irrigation urgency; review whether the next turn can be shortened."
        )

    normalized_risk = pest_risk.upper()
    if normalized_risk == "HIGH":
        actions.append(
            "Prioritize field inspection today in the most vigorous areas and along plot edges."
        )
        actions.append(
            "If presence is confirmed, act locally and validate the decision with your agronomist."
        )
    elif normalized_risk == "MEDIUM":
        actions.append(
            "Perform a preventive review within 24-48 hours to confirm whether the risk becomes a real hotspot."
        )
    else:
        actions.append(
            "Keep normal monitoring; this reading does not show a high-priority pest signal."
        )

    actions.append(
        "Record the action taken so the model can be recalibrated with real field outcomes."
    )
    return actions
