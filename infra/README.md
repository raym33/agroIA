# Infrastructure

This folder prepares the recommended stack for the next two weeks of practical implementation:

- `PostgreSQL + PostGIS + TimescaleDB` for spatial and time-series data
- `DuckDB + Parquet` for messy spreadsheet landing and cleanup
- `OGC SensorThings` as an open normalization layer for field sensors
- `FROST` as a separate compose stack for SensorThings experimentation

## Start the operational data stack

```bash
cd "/Users/c/Desktop/carpeta sin título 2/agricultura/infra"
docker compose -f docker-compose.agro-stack.yml up -d
```

Available services:

- PostgreSQL/Timescale/PostGIS: `127.0.0.1:5432`
- Adminer: `http://127.0.0.1:8088`

## Start the optional SensorThings stack

```bash
cd "/Users/c/Desktop/carpeta sin título 2/agricultura/infra"
docker compose -f docker-compose.sensorthings.yml up -d
```

Available services:

- FROST HTTP: `http://127.0.0.1:8089/FROST-Server/v1.1`
- FROST MQTT: `127.0.0.1:1884`
- Internal PostGIS for FROST: `127.0.0.1:55432`

## Intentionally missing

- Real ETL from SIGPAC, SIAM, AEMET, or Sentinel-2
- Authentication or network hardening for FROST
- Production deployment configuration

## Recommended next steps

1. Load real plots.
2. Map them to official SIGPAC recintos.
3. Add a DuckDB importer for messy spreadsheets.
4. Connect one real sensor or gateway.
