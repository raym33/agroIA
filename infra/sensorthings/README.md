# SensorThings / FROST

This compose file starts a separate `OGC SensorThings API` environment using `FROST`.

## Why it is separate

- it avoids mixing the agronomic operational database with the internal SensorThings database
- it allows IoT interoperability tests without touching the main schema
- it makes it easy to replace or stop the SensorThings layer independently

## Start it

```bash
docker compose -f infra/docker-compose.sensorthings.yml up -d
```

## Endpoints

- HTTP: `http://localhost:8089/FROST-Server/v1.1`
- MQTT: `localhost:1884`
- FROST PostGIS: `localhost:55432`

## How it fits this project

- `connectors/sensorthings_mapper.py` normalizes field payloads
- `connectors/device_profiles.py` documents recommended hardware profiles
- `iot.sensor_nodes` and `iot.sensor_channels` act as the application-side mirror

Recommended usage:

1. A sensor or gateway publishes through `LoRaWAN`, `Modbus`, `SDI-12`, `pulse`, or `4-20 mA`.
2. A bridge or webhook transforms the payload into normalized observations.
3. The data is inserted into FROST and, when appropriate, also into the operational database.
4. The web app consumes a unified view without depending on one hardware vendor.
