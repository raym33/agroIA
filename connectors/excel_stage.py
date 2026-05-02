from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExcelMappingProfile:
    logical_name: str
    required_columns: list[str]
    optional_columns: list[str]
    destination_table: str


RIEGO_PROFILE = ExcelMappingProfile(
    logical_name="irrigation_labeled",
    required_columns=[
        "fecha",
        "parcel_id",
        "temp_c",
        "humidity_pct",
        "et0_mm",
        "rain_mm",
        "crop_type",
        "water_need_l_m2",
    ],
    optional_columns=["soil_moisture_pct", "notes", "production_kg"],
    destination_table="stage.excel_rows -> training irrigation dataset",
)


PLAGAS_PROFILE = ExcelMappingProfile(
    logical_name="pest_labeled",
    required_columns=[
        "fecha",
        "parcel_id",
        "temp_c",
        "humidity_pct",
        "et0_mm",
        "ndvi",
        "days_since_rain",
        "crop_type",
        "pest_risk_level",
    ],
    optional_columns=["pest_observed", "notes", "production_kg"],
    destination_table="stage.excel_rows -> training pest dataset",
)


def suggest_profile(columns: list[str]) -> ExcelMappingProfile | None:
    normalized = {column.strip().lower() for column in columns}
    for profile in (RIEGO_PROFILE, PLAGAS_PROFILE):
        if all(required in normalized for required in profile.required_columns):
            return profile
    return None


def parquet_target_path(base_dir: Path, import_name: str) -> Path:
    return base_dir / f"{import_name}.parquet"
