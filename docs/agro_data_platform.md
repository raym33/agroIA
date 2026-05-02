# Recommended agrotech data platform

## Goal

Build a platform that:

- does not depend on a single sensor vendor
- can join `plots + time + satellite + sensors + historical spreadsheets`
- can scale without a full redesign when time-series density increases

## Architecture

### 1. Operational database

- `PostgreSQL`
- `PostGIS`
- `TimescaleDB`

What it stores:

- plots and irrigation sectors
- official SIGPAC recintos
- sensor nodes and channels
- time-series observations
- parcel-level daily EO features

### 2. Landing zone

- `DuckDB`
- `Parquet`

What it solves:

- importing messy Excel and CSV files
- profiling column names and types
- cleaning before loading into the operational database

### 3. Open IoT interoperability layer

- `OGC SensorThings API`
- `FROST` as the recommended open-source implementation

What it solves:

- normalizing heterogeneous sensors into one model
- decoupling hardware from the application backend
- exposing observations and metadata through an open standard

Local references:

- [infra/docker-compose.sensorthings.yml](/Users/c/Desktop/carpeta sin título 2/agricultura/infra/docker-compose.sensorthings.yml)
- [infra/sensorthings/README.md](/Users/c/Desktop/carpeta sin título 2/agricultura/infra/sensorthings/README.md)

### 4. Agronomic data sources to integrate

- `SIGPAC` for official parcel geometry
- `SIAM-IMIDA` for Murcia agroclimate
- `AEMET OpenData` for national climate fallback
- `Sentinel-2` for NDVI and vegetation vigor

### 5. Prediction stack

Current baseline:

- `RandomForestRegressor` for irrigation
- `RandomForestClassifier` for pest risk

Next benchmark:

- `CatBoost`
- `XGBoost`

### 6. Role of Gemma

Gemma should remain:

- an explainer for farmers or technicians
- a cautious visual reviewer
- a local copilot that summarizes recommendations

It should not be the primary engine for irrigation liters or pest class prediction.

## Recommended flow

1. Import Excel or CSV files into DuckDB.
2. Clean and export to Parquet.
3. Load plots, recintos, and observations into PostgreSQL.
4. Register sensors as logical `Thing + Datastream` entities.
5. Train and version models.
6. Expose recommendations in the web app.
