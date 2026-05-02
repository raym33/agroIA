from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class NormalizedObservation:
    sensor_node_id: str
    sensor_channel_id: str
    observed_at: datetime
    value: float | str
    source_protocol: str
    source_payload: dict[str, Any]


def make_sensorthings_datastream_name(parcel_id: str, observed_property_name: str) -> str:
    return f"{parcel_id} :: {observed_property_name}"


def normalize_lorawan_measurement(
    *,
    sensor_node_id: str,
    sensor_channel_id: str,
    source_protocol: str,
    source_payload: dict[str, Any],
    value_field: str,
    observed_at_field: str | None = None,
) -> NormalizedObservation:
    if value_field not in source_payload:
        raise KeyError(f"Falta el campo de valor '{value_field}' en el payload")

    observed_at = datetime.now(timezone.utc)
    if observed_at_field and source_payload.get(observed_at_field):
        observed_at = datetime.fromisoformat(str(source_payload[observed_at_field]))

    return NormalizedObservation(
        sensor_node_id=sensor_node_id,
        sensor_channel_id=sensor_channel_id,
        observed_at=observed_at,
        value=source_payload[value_field],
        source_protocol=source_protocol,
        source_payload=source_payload,
    )


def build_frost_observation_payload(datastream_id: int, observation: NormalizedObservation) -> dict[str, Any]:
    return {
        "phenomenonTime": observation.observed_at.isoformat(),
        "result": observation.value,
        "Datastream": {"@iot.id": datastream_id},
        "parameters": {
            "sensor_node_id": observation.sensor_node_id,
            "sensor_channel_id": observation.sensor_channel_id,
            "source_protocol": observation.source_protocol,
        },
    }
