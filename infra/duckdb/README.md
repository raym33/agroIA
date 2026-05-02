# DuckDB landing zone

Use DuckDB as the landing zone for messy historical data:

- farmer spreadsheets
- cooperative exports
- ad-hoc CSV files
- partial historical records

Recommended pattern:

1. ingest raw Excel or CSV files
2. profile columns and detect candidate mappings
3. map fields into the agricultural schema
4. export normalized `Parquet`
5. load only cleaned tables into the operational database

This prevents malformed spreadsheets from polluting the main PostgreSQL/PostGIS database.
