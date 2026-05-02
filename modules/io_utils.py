from pathlib import Path
from typing import Iterable

import pandas as pd

from config import (
    BENCHMARKS_DIR,
    DATA_DIR,
    IMAGE_UPLOADS_DIR,
    MODELS_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    REPORTS_DIR,
    TABLE_UPLOADS_DIR,
    UPLOADS_DIR,
)


def ensure_project_dirs() -> None:
    for path in (
        DATA_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        UPLOADS_DIR,
        IMAGE_UPLOADS_DIR,
        TABLE_UPLOADS_DIR,
        MODELS_DIR,
        REPORTS_DIR,
        BENCHMARKS_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


def load_csv(path: Path) -> pd.DataFrame:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file does not exist: {csv_path}")
    return pd.read_csv(csv_path)


def require_columns(df: pd.DataFrame, required_columns: Iterable[str], dataset_name: str) -> None:
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        missing_str = ", ".join(missing)
        raise ValueError(f"Missing columns in {dataset_name}: {missing_str}")
