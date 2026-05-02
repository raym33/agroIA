from pathlib import Path
from typing import List

from config import YOLO_MODEL_PATH


def detect_pests_in_image(image_path: Path, confidence: float = 0.5) -> List[dict]:
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image does not exist: {image_path}")
    if not YOLO_MODEL_PATH.exists():
        raise FileNotFoundError(
            "models/pest_detector.pt does not exist. Train or download a local YOLO model first."
        )

    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise ImportError("Install ultralytics to use visual detection.") from exc

    model = YOLO(str(YOLO_MODEL_PATH))
    results = model(str(image_path), conf=confidence)

    detections: List[dict] = []
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            detections.append(
                {
                    "label": model.names[class_id],
                    "confidence": round(float(box.conf[0]), 3),
                }
            )
    return detections
