---
name: agrotech-local-mvp
description: Build local-first agrotech MVPs with irrigation recommendation, pest risk, farmer spreadsheet ingestion, open sensor interoperability, satellite-ready data models, and a cautious local LLM explanation layer. Use when creating or extending agricultural decision-support apps, especially Streamlit or Python apps for plots, irrigation, pest monitoring, sensor normalization, or farmer data onboarding.
---

# Agrotech Local MVP

Use this skill when the task is to create or extend a local-first precision agriculture application.

## Default posture

- Keep the MVP narrow.
- Prioritize irrigation and tabular pest risk before advanced vision.
- Treat local LLMs as explainers, not as the primary numeric prediction engine.
- Prefer open protocols and open data sources.
- Be explicit about what is scaffolded versus field-validated.

## Recommended stack

- UI: `Streamlit`
- Tabular ML: `scikit-learn` baseline, then `CatBoost` and `XGBoost` benchmarks
- Operational DB: `PostgreSQL + PostGIS + TimescaleDB`
- Landing zone: `DuckDB + Parquet`
- IoT interoperability: `OGC SensorThings API` with `FROST`
- Local LLM: OpenAI-compatible endpoint such as `Gemma`

## Workflow

1. Read [references/mvp-scope.md](references/mvp-scope.md) to choose the narrowest viable product slice.
2. Read [references/architecture.md](references/architecture.md) to set the data platform and service boundaries.
3. Read [references/data-sources.md](references/data-sources.md) when selecting Murcia/Spain data sources.
4. Read [references/hardware.md](references/hardware.md) when the task involves sensors, weather stations, or flow meters.
5. If the user lacks real data, scaffold:
   - demo datasets
   - farmer spreadsheet template
   - farmer discovery questionnaire
   - explicit implementation gaps
6. If the task includes images:
   - keep YOLO optional unless labeled images exist
   - keep Gemma vision outputs conservative
7. End with a clear list of:
   - what is implemented
   - what is simulated or demo-only
   - what data is still missing

## Delivery rules

- Do not promise agronomic accuracy without real field labels.
- Do not make climate-only pest prediction sound production-ready.
- Prefer `SDI-12`, `Modbus RTU`, `LoRaWAN`, `pulse`, `4-20 mA`, and `0-10 V`.
- Document missing data, integration gaps, and validation risks in the repo.
- Include a benchmark path, not just one baseline model.

## Claude Code note

For Claude Code, adapt this skill by copying the guidance in [references/claude_code_adapter.md](references/claude_code_adapter.md) into the project-level `CLAUDE.md` or equivalent instruction file.
