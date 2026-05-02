# Architecture

Recommended layers:

- `Streamlit` for the first usable UI
- `scikit-learn` baselines for irrigation and pest risk
- `DuckDB` for messy spreadsheet landing
- `PostgreSQL + PostGIS + TimescaleDB` for operational storage
- `OGC SensorThings API / FROST` for open sensor normalization
- local OpenAI-compatible LLM only for explanation and visual review

Recommended entities:

- plots
- irrigation sectors
- official parcel geometry
- sensor nodes
- sensor channels
- observations
- raster assets
- parcel daily features

Do not conflate:

- the operational agronomic database
- the SensorThings server database
- raw spreadsheet landing files
