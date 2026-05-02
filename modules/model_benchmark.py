from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

from config import BENCHMARKS_DIR
from modules.io_utils import load_csv, require_columns
from modules.irrigation import IRRIGATION_FEATURES, IRRIGATION_TARGET
from modules.pest_risk import PEST_FEATURES, PEST_TARGET


@dataclass(frozen=True)
class BenchmarkRow:
    task: str
    model: str
    status: str
    primary_metric: float | None
    secondary_metric: float | None
    primary_metric_name: str
    secondary_metric_name: str
    notes: str = ""


def _build_preprocessor(
    numeric_features: list[str], categorical_features: list[str]
) -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), numeric_features),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                categorical_features,
            ),
        ]
    )


def _save_rows(task: str, rows: list[BenchmarkRow]) -> Path:
    BENCHMARKS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = BENCHMARKS_DIR / f"{task}_benchmark.json"
    payload = [asdict(row) for row in rows]
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True))
    return output_path


def _optional_regressors() -> list[tuple[str, Callable[[], Any]]]:
    def make_random_forest() -> RandomForestRegressor:
        return RandomForestRegressor(
            n_estimators=300,
            max_depth=14,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        )

    def make_catboost() -> Any:
        from catboost import CatBoostRegressor

        return CatBoostRegressor(
            iterations=500,
            depth=8,
            learning_rate=0.05,
            loss_function="MAE",
            verbose=False,
            random_seed=42,
        )

    def make_xgboost() -> Any:
        from xgboost import XGBRegressor

        return XGBRegressor(
            n_estimators=400,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="reg:squarederror",
            random_state=42,
            n_jobs=-1,
        )

    return [
        ("RandomForest", make_random_forest),
        ("CatBoost", make_catboost),
        ("XGBoost", make_xgboost),
    ]


def _optional_classifiers(num_classes: int) -> list[tuple[str, Callable[[], Any]]]:
    def make_random_forest() -> RandomForestClassifier:
        return RandomForestClassifier(
            n_estimators=350,
            max_depth=12,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )

    def make_catboost() -> Any:
        from catboost import CatBoostClassifier

        return CatBoostClassifier(
            iterations=500,
            depth=8,
            learning_rate=0.05,
            loss_function="MultiClass",
            auto_class_weights="Balanced",
            verbose=False,
            random_seed=42,
        )

    def make_xgboost() -> Any:
        from xgboost import XGBClassifier

        return XGBClassifier(
            n_estimators=400,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="multi:softprob",
            num_class=num_classes,
            random_state=42,
            n_jobs=-1,
        )

    return [
        ("RandomForest", make_random_forest),
        ("CatBoost", make_catboost),
        ("XGBoost", make_xgboost),
    ]


def benchmark_irrigation_models(csv_path: Path) -> dict[str, Any]:
    df = load_csv(Path(csv_path))
    require_columns(df, IRRIGATION_FEATURES + [IRRIGATION_TARGET], "irrigation dataset")

    x = df[IRRIGATION_FEATURES].copy()
    y = df[IRRIGATION_TARGET].copy()
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )

    preprocessor = _build_preprocessor(
        numeric_features=[
            "temp_c",
            "humidity_pct",
            "et0_mm",
            "soil_moisture_pct",
            "rain_mm",
        ],
        categorical_features=["crop_type"],
    )
    x_train_ready = preprocessor.fit_transform(x_train)
    x_test_ready = preprocessor.transform(x_test)

    rows: list[BenchmarkRow] = []
    for model_name, builder in _optional_regressors():
        try:
            model = builder()
        except ImportError as exc:
            rows.append(
                BenchmarkRow(
                    task="irrigation",
                    model=model_name,
                    status="skipped_missing_dependency",
                    primary_metric=None,
                    secondary_metric=None,
                    primary_metric_name="mae",
                    secondary_metric_name="r2",
                    notes=str(exc),
                )
            )
            continue

        model.fit(x_train_ready, y_train)
        predictions = model.predict(x_test_ready)
        rows.append(
            BenchmarkRow(
                task="irrigation",
                model=model_name,
                status="ok",
                primary_metric=float(mean_absolute_error(y_test, predictions)),
                secondary_metric=float(r2_score(y_test, predictions)),
                primary_metric_name="mae",
                secondary_metric_name="r2",
            )
        )

    output_path = _save_rows("irrigation", rows)
    return {"output_path": str(output_path), "rows": [asdict(row) for row in rows]}


def benchmark_pest_models(csv_path: Path) -> dict[str, Any]:
    df = load_csv(Path(csv_path))
    require_columns(df, PEST_FEATURES + [PEST_TARGET], "pest dataset")

    x = df[PEST_FEATURES].copy()
    y = df[PEST_TARGET].astype(str).str.lower().copy()
    x_train, x_test, y_train_raw, y_test_raw = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    preprocessor = _build_preprocessor(
        numeric_features=[
            "temp_c",
            "humidity_pct",
            "et0_mm",
            "ndvi",
            "days_since_rain",
        ],
        categorical_features=["crop_type"],
    )
    x_train_ready = preprocessor.fit_transform(x_train)
    x_test_ready = preprocessor.transform(x_test)

    label_encoder = LabelEncoder()
    y_train = label_encoder.fit_transform(y_train_raw)
    y_test = label_encoder.transform(y_test_raw)

    rows: list[BenchmarkRow] = []
    for model_name, builder in _optional_classifiers(num_classes=len(label_encoder.classes_)):
        try:
            model = builder()
        except ImportError as exc:
            rows.append(
                BenchmarkRow(
                    task="pests",
                    model=model_name,
                    status="skipped_missing_dependency",
                    primary_metric=None,
                    secondary_metric=None,
                    primary_metric_name="accuracy",
                    secondary_metric_name="macro_f1",
                    notes=str(exc),
                )
            )
            continue

        model.fit(x_train_ready, y_train)
        predictions = model.predict(x_test_ready)
        rows.append(
            BenchmarkRow(
                task="pests",
                model=model_name,
                status="ok",
                primary_metric=float(accuracy_score(y_test, predictions)),
                secondary_metric=float(f1_score(y_test, predictions, average="macro")),
                primary_metric_name="accuracy",
                secondary_metric_name="macro_f1",
            )
        )

    output_path = _save_rows("pests", rows)
    return {"output_path": str(output_path), "rows": [asdict(row) for row in rows]}
