# AgroIA

AgroIA is a local-first precision agriculture MVP focused on the two highest-value workflows for an early deployment:

1. Daily irrigation recommendation per plot
2. Early pest risk assessment before losses escalate

The project is designed to run locally, avoid mandatory cloud dependencies, and stay modular enough to grow into a fuller agrotech platform with sensors, satellite features, visual inspection, and farmer data imports.

## Current scope

- Local irrigation model with `scikit-learn`
- Local tabular pest risk model with `scikit-learn`
- Optional local YOLO detector hook for field or drone images
- SQLite traceability log for recommendations and actions
- Streamlit web app for daily use
- Local LLM integration for explanation and visual review
- PostgreSQL/PostGIS/TimescaleDB data platform scaffold
- SensorThings/FROST interoperability scaffold
- Farmer Excel template and discovery questionnaire
- Reproducible benchmark entrypoint for `RandomForest`, `CatBoost`, and `XGBoost`

## Why this architecture

The product should not start as “AI for everything”. The practical path is:

- Predict daily irrigation using weather, ET0, soil moisture, rain, and crop type
- Estimate pest risk using weather, vegetation indicators, and crop context
- Keep an explainable local UI for farmers and technicians
- Add image-based inspection only after real labeled field photos exist

Large multimodal models such as Gemma are useful here as a local explainer and visual copilot, not as the primary engine for liters of irrigation or pest risk classes.

## Repository structure

```text
agroIA/
├── config.py
├── main.py
├── streamlit_app.py
├── modules/
├── connectors/
├── configs/
├── docs/
├── infra/
├── scripts/
├── templates/
├── models/
├── data/
└── requirements.txt
```

## Core models

Current production-style baselines:

- `RandomForestRegressor` for irrigation
- `RandomForestClassifier` for pest risk

Benchmark candidates already scaffolded:

- `CatBoost`
- `XGBoost`

Optional visual layer:

- `YOLO` for image detection once labeled images exist

Optional language/vision layer:

- `Gemma 4 26B A4B` or another OpenAI-compatible local endpoint for explanation and cautious visual review

## Quick start

```bash
cd "/Users/c/Desktop/carpeta sin título 2/agricultura"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py init-demo-data
python3 main.py train-all
streamlit run streamlit_app.py
```

## CLI

Generate demo datasets:

```bash
python3 main.py init-demo-data
```

Train both baseline models:

```bash
python3 main.py train-all
```

Run a local prediction:

```bash
python3 main.py predict \
  --parcel-id PLOT-001 \
  --crop-type vegetables \
  --temp-c 28 \
  --humidity-pct 47 \
  --et0-mm 5.9 \
  --soil-moisture-pct 21 \
  --rain-mm 0 \
  --ndvi 0.72 \
  --days-since-rain 11 \
  --save
```

Benchmark model families:

```bash
python3 main.py benchmark-models --task all
```

Prepare a daily SIAM CSV into base training tables:

```bash
python3 main.py prepare-siam \
  --input-csv data/raw/murcia_ca52.csv \
  --crop-type vegetables \
  --soil-moisture-pct 22 \
  --output-prefix ca52
```

## Streamlit app

Start the web app:

```bash
streamlit run streamlit_app.py
```

The UI currently includes:

- `Prediction`
- `Photos`
- `Historical spreadsheets`
- `History`

## Local LLM setup

Default endpoint:

- base URL: `http://127.0.0.1:8000`
- model: `mlx-community/gemma-4-26b-a4b-it-4bit`

You can override both:

```bash
export LOCAL_LLM_BASE_URL="http://127.0.0.1:8000"
export LOCAL_LLM_MODEL="mlx-community/gemma-4-26b-a4b-it-4bit"
streamlit run streamlit_app.py
```

## Data sources

Start with Murcia and Spain-specific sources before expanding scope.

### Agroclimate and irrigation

- SIAM-IMIDA: [https://siam.imida.es/](https://siam.imida.es/)
- Murcia open data portal: [https://datosabiertos.regiondemurcia.es/](https://datosabiertos.regiondemurcia.es/)
- Example CSV: [https://datosabiertos.carm.es/odata/Agricultura/IMIDA_Diario_CA52.csv](https://datosabiertos.carm.es/odata/Agricultura/IMIDA_Diario_CA52.csv)
- AEMET OpenData: [https://www.aemet.es/es/datos_abiertos/AEMET_OpenData](https://www.aemet.es/es/datos_abiertos/AEMET_OpenData)

### Satellite imagery and vegetation indicators

- Copernicus Sentinel-2: [https://dataspace.copernicus.eu/explore-data/data-collections/sentinel-data/sentinel-2](https://dataspace.copernicus.eu/explore-data/data-collections/sentinel-data/sentinel-2)

### Parcel geometry

- SIGPAC official parcels/recintos: [https://datos.gob.es/es/catalogo/e0dat0002-recintos-del-sistema-de-informacion-geografica-de-parcelas-agricolas-sigpac](https://datos.gob.es/es/catalogo/e0dat0002-recintos-del-sistema-de-informacion-geografica-de-parcelas-agricolas-sigpac)

### Pest vision datasets

- IP102: [https://github.com/xpwu95/IP102](https://github.com/xpwu95/IP102)
- AgroPest-12: [https://www.kaggle.com/datasets/rupankarmajumdar/crop-pests-dataset](https://www.kaggle.com/datasets/rupankarmajumdar/crop-pests-dataset)

### Agronomic reference context

- FAO AquaCrop: [https://www.fao.org/aquacrop/overview/en](https://www.fao.org/aquacrop/overview/en)
- MAPA plant health and sustainable pesticide use: [https://servicio.mapa.gob.es/es/agricultura/temas/sanidad-vegetal/productos-fitosanitarios/uso-sostenible-de-productos-fitosanitarios/default.aspx](https://servicio.mapa.gob.es/es/agricultura/temas/sanidad-vegetal/productos-fitosanitarios/uso-sostenible-de-productos-fitosanitarios/default.aspx)

## Sensors and hardware

Recommended protocol-first hardware profiles are documented in:

- [docs/compatible_hardware.md](/Users/c/Desktop/carpeta sin título 2/agricultura/docs/compatible_hardware.md)

Practical guidance:

- Prefer `SDI-12`, `RS485/Modbus RTU`, `LoRaWAN`, `pulse`, `4-20 mA`, or `0-10 V`
- Avoid mandatory vendor clouds and undocumented payloads
- Use bridges when the farmer already has installed hardware

## Data platform

The repo already includes a scaffold for:

- `PostgreSQL + PostGIS + TimescaleDB`
- `DuckDB + Parquet`
- `OGC SensorThings API` with `FROST`

See:

- [docs/agro_data_platform.md](/Users/c/Desktop/carpeta sin título 2/agricultura/docs/agro_data_platform.md)
- [infra/README.md](/Users/c/Desktop/carpeta sin título 2/agricultura/infra/README.md)

## Open gaps before a serious pilot

The repository includes a working scaffold, not a finished production product. The main missing pieces are tracked in:

- [docs/implementation_gaps.md](/Users/c/Desktop/carpeta sin título 2/agricultura/docs/implementation_gaps.md)
- [docs/sources_and_datasets.md](/Users/c/Desktop/carpeta sin título 2/agricultura/docs/sources_and_datasets.md)

High-priority gaps:

- Real labeled farmer datasets
- Real plot geometry import from SIGPAC
- Sensor ingestion adapters for actual field devices
- Labeled field images for visual detection
- Authentication, user roles, and auditability
- Production deployment and operations hardening

## Farmer onboarding assets

- Excel template: `templates/farmer_data_template_mvp.xlsx`
- Interview questionnaire: [docs/farmer_discovery_questionnaire.md](/Users/c/Desktop/carpeta sin título 2/agricultura/docs/farmer_discovery_questionnaire.md)

## Reusable skill

This repo also includes a reusable Codex/Claude-style skill to accelerate future projects of the same type:

- [skills/agrotech-local-mvp/SKILL.md](/Users/c/Desktop/carpeta sin título 2/agricultura/skills/agrotech-local-mvp/SKILL.md)

## License

MIT. See [LICENSE](/Users/c/Desktop/carpeta sin título 2/agricultura/LICENSE).
