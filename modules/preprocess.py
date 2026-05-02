from pathlib import Path
from typing import Dict

import pandas as pd

from config import PROCESSED_DATA_DIR
from modules.io_utils import ensure_project_dirs, load_csv, require_columns


SIAM_REQUIRED_COLUMNS = ["fecha", "tmed", "hrmed", "prec", "eto"]


def _days_since_last_rain(precipitation: pd.Series, threshold: float = 0.1) -> pd.Series:
    days = []
    counter = 0
    for value in precipitation.fillna(0):
        if float(value) > threshold:
            counter = 0
        else:
            counter += 1
        days.append(counter)
    return pd.Series(days, index=precipitation.index)


def prepare_siam_daily_csv(
    *,
    input_csv: Path,
    crop_type: str,
    soil_moisture_pct: float,
    output_prefix: str,
) -> Dict[str, Path]:
    ensure_project_dirs()
    df = load_csv(input_csv)
    require_columns(df, SIAM_REQUIRED_COLUMNS, "daily SIAM CSV")

    normalized = df.copy()
    normalized["fecha"] = pd.to_datetime(normalized["fecha"], dayfirst=True, errors="coerce")
    normalized = normalized.dropna(subset=["fecha"]).sort_values("fecha").reset_index(drop=True)

    irrigation_df = pd.DataFrame(
        {
            "date": normalized["fecha"].dt.date.astype(str),
            "temp_c": pd.to_numeric(normalized["tmed"], errors="coerce"),
            "humidity_pct": pd.to_numeric(normalized["hrmed"], errors="coerce"),
            "et0_mm": pd.to_numeric(normalized["eto"], errors="coerce"),
            "soil_moisture_pct": soil_moisture_pct,
            "rain_mm": pd.to_numeric(normalized["prec"], errors="coerce"),
            "crop_type": crop_type,
            "water_need_l_m2": pd.NA,
        }
    )

    pest_df = pd.DataFrame(
        {
            "date": normalized["fecha"].dt.date.astype(str),
            "temp_c": pd.to_numeric(normalized["tmed"], errors="coerce"),
            "humidity_pct": pd.to_numeric(normalized["hrmed"], errors="coerce"),
            "et0_mm": pd.to_numeric(normalized["eto"], errors="coerce"),
            "ndvi": pd.NA,
            "days_since_rain": _days_since_last_rain(pd.to_numeric(normalized["prec"], errors="coerce")),
            "crop_type": crop_type,
            "pest_risk_level": pd.NA,
        }
    )

    irrigation_path = PROCESSED_DATA_DIR / f"{output_prefix}_irrigation_base.csv"
    pest_path = PROCESSED_DATA_DIR / f"{output_prefix}_pest_base.csv"

    irrigation_df.to_csv(irrigation_path, index=False)
    pest_df.to_csv(pest_path, index=False)

    return {"irrigation": irrigation_path, "pest": pest_path}
