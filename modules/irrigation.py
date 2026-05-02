from pathlib import Path
from typing import Any, Dict

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from config import IRRIGATION_MODEL_PATH
from modules.io_utils import load_csv, require_columns


IRRIGATION_FEATURES = [
    "temp_c",
    "humidity_pct",
    "et0_mm",
    "soil_moisture_pct",
    "rain_mm",
    "crop_type",
]
IRRIGATION_TARGET = "water_need_l_m2"


def _build_irrigation_pipeline() -> Pipeline:
    numeric_features = [
        "temp_c",
        "humidity_pct",
        "et0_mm",
        "soil_moisture_pct",
        "rain_mm",
    ]
    categorical_features = ["crop_type"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), numeric_features),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_features,
            ),
        ]
    )

    return Pipeline(
        steps=[
            ("preprocess", preprocessor),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=300,
                    max_depth=14,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def train_irrigation_model(csv_path: Path) -> Dict[str, float]:
    df = load_csv(Path(csv_path))
    require_columns(df, IRRIGATION_FEATURES + [IRRIGATION_TARGET], "irrigation dataset")

    x = df[IRRIGATION_FEATURES].copy()
    y = df[IRRIGATION_TARGET].copy()

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )

    pipeline = _build_irrigation_pipeline()
    pipeline.fit(x_train, y_train)

    predictions = pipeline.predict(x_test)
    metrics = {
        "mae": float(mean_absolute_error(y_test, predictions)),
        "r2": float(r2_score(y_test, predictions)),
    }

    joblib.dump(pipeline, IRRIGATION_MODEL_PATH)
    return metrics


def predict_irrigation(
    *,
    temp_c: float,
    humidity_pct: float,
    et0_mm: float,
    soil_moisture_pct: float,
    rain_mm: float,
    crop_type: str,
) -> float:
    if not IRRIGATION_MODEL_PATH.exists():
        raise FileNotFoundError(
            "The irrigation model does not exist. Run `python3 main.py train-irrigation` first."
        )

    model = joblib.load(IRRIGATION_MODEL_PATH)
    sample = pd.DataFrame(
        [
            {
                "temp_c": temp_c,
                "humidity_pct": humidity_pct,
                "et0_mm": et0_mm,
                "soil_moisture_pct": soil_moisture_pct,
                "rain_mm": rain_mm,
                "crop_type": crop_type,
            }
        ]
    )
    prediction = model.predict(sample)[0]
    return max(0.0, float(prediction))
