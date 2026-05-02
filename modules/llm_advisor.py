import base64
import mimetypes
from pathlib import Path
from typing import Any, Dict, List

import requests

from config import (
    LOCAL_LLM_BASE_URL,
    LOCAL_LLM_MODEL,
    LOCAL_LLM_TIMEOUT_SECONDS,
)


def _post_chat_completion(base_url: str, payload: Dict[str, Any], timeout: int) -> requests.Response:
    candidate_paths = ["/v1/chat/completions", "/chat/completions"]
    last_response: requests.Response | None = None

    for path in candidate_paths:
        response = requests.post(
            f"{base_url.rstrip('/')}{path}",
            json=payload,
            timeout=timeout,
        )
        if response.status_code != 404:
            return response
        last_response = response

    if last_response is not None:
        return last_response
    raise RuntimeError("No compatible chat endpoint could be resolved.")


def list_local_models(base_url: str = LOCAL_LLM_BASE_URL, timeout: int = 10) -> List[str]:
    response = requests.get(f"{base_url.rstrip('/')}/v1/models", timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    return [item["id"] for item in payload.get("data", []) if "id" in item]


def get_local_llm_status(base_url: str = LOCAL_LLM_BASE_URL) -> Dict[str, Any]:
    try:
        models = list_local_models(base_url=base_url)
        return {"ok": True, "models": models}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "models": []}


def generate_daily_advice(
    *,
    parcel_id: str,
    crop_type: str,
    water_l_m2: float,
    pest_risk: str,
    temp_c: float,
    humidity_pct: float,
    et0_mm: float,
    soil_moisture_pct: float,
    rain_mm: float,
    ndvi: float,
    days_since_rain: int,
    base_url: str = LOCAL_LLM_BASE_URL,
    model: str = LOCAL_LLM_MODEL,
    timeout: int = LOCAL_LLM_TIMEOUT_SECONDS,
) -> str:
    system_prompt = (
        "You are a local agricultural assistant for Murcia. "
        "Explain field recommendations in clear, concise English. "
        "Do not invent data, cite fake regulations, or prescribe specific pesticide products or doses. "
        "Keep the answer to 4-5 short sentences and prioritize operational actions."
    )
    user_prompt = f"""
Summarize this daily recommendation for one plot:

- Plot: {parcel_id}
- Crop: {crop_type}
- Recommended water: {water_l_m2:.2f} L/m2
- Pest risk: {pest_risk}
- Temperature: {temp_c:.1f} C
- Relative humidity: {humidity_pct:.1f} %
- ET0: {et0_mm:.2f} mm
- Soil moisture: {soil_moisture_pct:.1f} %
- Rainfall: {rain_mm:.2f} mm
- NDVI: {ndvi:.2f}
- Days since rain: {days_since_rain}

Provide a short reading of the plot condition, today's priority, and one cautious field-validation warning.
"""

    response = _post_chat_completion(
        base_url=base_url,
        payload={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 140,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["choices"][0]["message"]["content"].strip()


def generate_visual_advice(
    *,
    image_path: Path,
    crop_type: str,
    image_context: str,
    base_url: str = LOCAL_LLM_BASE_URL,
    model: str = LOCAL_LLM_MODEL,
    timeout: int = LOCAL_LLM_TIMEOUT_SECONDS,
) -> str:
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image does not exist: {image_path}")

    mime_type = mimetypes.guess_type(str(image_path))[0] or "image/jpeg"
    encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    data_url = f"data:{mime_type};base64,{encoded}"

    system_prompt = (
        "You are a visual agriculture assistant. "
        "Describe only what is reasonable to observe in the image. "
        "Do not diagnose pests or diseases with certainty and do not prescribe products. "
        "Respond in English with 4-6 operational sentences."
    )
    user_prompt = (
        f"Analyze this agricultural image. Crop: {crop_type}. "
        f"Context: {image_context}. "
        "Point out visible signs of stress, damage, vigor, uniformity, or potential problems. "
        "Close with a cautious recommendation for field validation."
    )

    response = _post_chat_completion(
        base_url=base_url,
        payload={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
            "temperature": 0.2,
            "max_tokens": 180,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["choices"][0]["message"]["content"].strip()
