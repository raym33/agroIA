from pathlib import Path
from typing import Dict

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from config import PEST_RISK_MODEL_PATH
from modules.io_utils import load_csv, require_columns


PEST_FEATURES = [
    "temp_c",
    "humidity_pct",
    "et0_mm",
    "ndvi",
    "days_since_rain",
    "crop_type",
]
PEST_TARGET = "pest_risk_level"


def _build_pest_pipeline() -> Pipeline:
    numeric_features = [
        "temp_c",
        "humidity_pct",
        "et0_mm",
        "ndvi",
        "days_since_rain",
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
                RandomForestClassifier(
                    n_estimators=350,
                    max_depth=12,
                    min_samples_leaf=2,
                    class_weight="balanced",
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def train_pest_risk_model(csv_path: Path) -> Dict[str, float]:
    df = load_csv(Path(csv_path))
    require_columns(df, PEST_FEATURES + [PEST_TARGET], "pest dataset")

    x = df[PEST_FEATURES].copy()
    y = df[PEST_TARGET].astype(str).str.lower().copy()

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    pipeline = _build_pest_pipeline()
    pipeline.fit(x_train, y_train)

    predictions = pipeline.predict(x_test)
    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "macro_f1": float(f1_score(y_test, predictions, average="macro")),
    }

    joblib.dump(pipeline, PEST_RISK_MODEL_PATH)
    return metrics


def predict_pest_risk(
    *,
    temp_c: float,
    humidity_pct: float,
    et0_mm: float,
    ndvi: float,
    days_since_rain: int,
    crop_type: str,
) -> str:
    if not PEST_RISK_MODEL_PATH.exists():
        raise FileNotFoundError(
            "The pest model does not exist. Run `python3 main.py train-pests` first."
        )

    model = joblib.load(PEST_RISK_MODEL_PATH)
    sample = pd.DataFrame(
        [
            {
                "temp_c": temp_c,
                "humidity_pct": humidity_pct,
                "et0_mm": et0_mm,
                "ndvi": ndvi,
                "days_since_rain": days_since_rain,
                "crop_type": crop_type,
            }
        ]
    )
    prediction = str(model.predict(sample)[0]).lower()
    if prediction not in {"low", "medium", "high"}:
        return prediction
    return prediction.upper()
