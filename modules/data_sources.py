from pathlib import Path

import requests

from config import RAW_DATA_DIR
from modules.io_utils import ensure_project_dirs


def download_url_to_file(url: str, output_name: str) -> Path:
    ensure_project_dirs()
    output_path = RAW_DATA_DIR / output_name

    response = requests.get(url, timeout=60)
    response.raise_for_status()
    output_path.write_bytes(response.content)
    return output_path


def fetch_aemet_api_resource(api_key: str, resource_path: str, output_name: str) -> Path:
    ensure_project_dirs()
    resource_path = resource_path.lstrip("/")
    base_url = f"https://opendata.aemet.es/opendata/api/{resource_path}"

    response = requests.get(
        base_url,
        params={"api_key": api_key},
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()

    data_url = payload.get("datos")
    if not data_url:
        raise ValueError(f"AEMET response does not include a data URL: {payload}")

    return download_url_to_file(data_url, output_name)
