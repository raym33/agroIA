from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
UPLOADS_DIR = DATA_DIR / "uploads"
IMAGE_UPLOADS_DIR = UPLOADS_DIR / "images"
TABLE_UPLOADS_DIR = UPLOADS_DIR / "tables"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
BENCHMARKS_DIR = REPORTS_DIR / "benchmarks"
DB_PATH = DATA_DIR / "traceability.db"

IRRIGATION_MODEL_PATH = MODELS_DIR / "irrigation_model.pkl"
PEST_RISK_MODEL_PATH = MODELS_DIR / "pest_risk_model.pkl"
YOLO_MODEL_PATH = MODELS_DIR / "pest_detector.pt"

DEMO_IRRIGATION_CSV = RAW_DATA_DIR / "demo_irrigation_dataset.csv"
DEMO_PEST_RISK_CSV = RAW_DATA_DIR / "demo_pest_risk_dataset.csv"

LOCAL_LLM_BASE_URL = os.getenv("LOCAL_LLM_BASE_URL", "http://127.0.0.1:8000")
LOCAL_LLM_MODEL = os.getenv(
    "LOCAL_LLM_MODEL",
    "mlx-community/gemma-4-26b-a4b-it-4bit",
)
LOCAL_LLM_TIMEOUT_SECONDS = int(os.getenv("LOCAL_LLM_TIMEOUT_SECONDS", "300"))
