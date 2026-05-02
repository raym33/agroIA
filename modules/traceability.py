import sqlite3
from datetime import datetime, timezone
from typing import List

from config import DB_PATH


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                parcel_id TEXT NOT NULL,
                crop_type TEXT NOT NULL,
                water_recommended_l_m2 REAL NOT NULL,
                pest_risk TEXT NOT NULL,
                notes TEXT,
                data_source TEXT
            )
            """
        )


def log_decision(
    *,
    parcel_id: str,
    crop_type: str,
    water_recommended_l_m2: float,
    pest_risk: str,
    notes: str = "",
    data_source: str = "",
) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO decisions (
                created_at,
                parcel_id,
                crop_type,
                water_recommended_l_m2,
                pest_risk,
                notes,
                data_source
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                parcel_id,
                crop_type,
                water_recommended_l_m2,
                pest_risk,
                notes,
                data_source,
            ),
        )


def list_recent_decisions(limit: int = 10) -> List[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT created_at, parcel_id, crop_type, water_recommended_l_m2, pest_risk, notes
            FROM decisions
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
