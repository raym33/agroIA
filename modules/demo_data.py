from pathlib import Path

import numpy as np
import pandas as pd

from config import DEMO_IRRIGATION_CSV, DEMO_PEST_RISK_CSV
from modules.io_utils import ensure_project_dirs


def _bounded(values: np.ndarray, low: float, high: float) -> np.ndarray:
    return np.clip(values, low, high)


def generate_demo_datasets(rows: int = 240, seed: int = 42) -> None:
    ensure_project_dirs()
    rng = np.random.default_rng(seed)

    crop_types = np.array(["vegetables", "citrus", "orchard"])
    crop_pick = rng.choice(crop_types, size=rows, p=[0.45, 0.3, 0.25])

    temp_c = _bounded(rng.normal(26.5, 5.0, rows), 10, 42)
    humidity_pct = _bounded(rng.normal(51.0, 12.0, rows), 15, 95)
    et0_mm = _bounded(rng.normal(5.1, 1.3, rows), 1.2, 9.5)
    soil_moisture_pct = _bounded(rng.normal(24.0, 7.0, rows), 6, 45)
    rain_mm = _bounded(rng.exponential(1.3, rows) - 0.6, 0, 18)
    ndvi = _bounded(rng.normal(0.69, 0.11, rows), 0.2, 0.92)
    days_since_rain = _bounded(rng.integers(0, 20, rows), 0, 20)

    crop_factor = np.select(
        [crop_pick == "vegetables", crop_pick == "citrus", crop_pick == "orchard"],
        [1.05, 0.9, 1.0],
        default=1.0,
    )

    water_need_l_m2 = (
        0.37 * et0_mm
        + 0.05 * temp_c
        - 0.03 * humidity_pct
        - 0.06 * soil_moisture_pct
        - 0.08 * rain_mm
    ) * crop_factor + rng.normal(2.3, 0.35, rows)
    water_need_l_m2 = _bounded(water_need_l_m2, 0.4, 8.2)

    pest_score = (
        0.08 * temp_c
        - 0.02 * humidity_pct
        + 0.22 * et0_mm
        - 1.4 * ndvi
        + 0.08 * days_since_rain
        + np.where(crop_pick == "vegetables", 0.45, 0)
        + rng.normal(0, 0.4, rows)
    )
    pest_risk_level = np.where(
        pest_score >= 2.1,
        "high",
        np.where(pest_score >= 1.1, "medium", "low"),
    )

    irrigation_df = pd.DataFrame(
        {
            "temp_c": np.round(temp_c, 2),
            "humidity_pct": np.round(humidity_pct, 2),
            "et0_mm": np.round(et0_mm, 2),
            "soil_moisture_pct": np.round(soil_moisture_pct, 2),
            "rain_mm": np.round(rain_mm, 2),
            "crop_type": crop_pick,
            "water_need_l_m2": np.round(water_need_l_m2, 2),
        }
    )

    pest_df = pd.DataFrame(
        {
            "temp_c": np.round(temp_c, 2),
            "humidity_pct": np.round(humidity_pct, 2),
            "et0_mm": np.round(et0_mm, 2),
            "ndvi": np.round(ndvi, 3),
            "days_since_rain": days_since_rain.astype(int),
            "crop_type": crop_pick,
            "pest_risk_level": pest_risk_level,
        }
    )

    irrigation_df.to_csv(Path(DEMO_IRRIGATION_CSV), index=False)
    pest_df.to_csv(Path(DEMO_PEST_RISK_CSV), index=False)
