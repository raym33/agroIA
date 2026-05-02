CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS iot;
CREATE SCHEMA IF NOT EXISTS stage;
CREATE SCHEMA IF NOT EXISTS eo;

CREATE TABLE IF NOT EXISTS core.parcels (
    parcel_id TEXT PRIMARY KEY,
    farmer_code TEXT,
    name TEXT NOT NULL,
    crop_type TEXT NOT NULL,
    municipality TEXT,
    area_ha NUMERIC(10, 2),
    irrigation_type TEXT,
    sigpac_province_code TEXT,
    sigpac_municipality_code TEXT,
    sigpac_polygon TEXT,
    sigpac_parcel TEXT,
    geom geometry(MultiPolygon, 4326),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_parcels_geom
    ON core.parcels
    USING GIST (geom);

CREATE TABLE IF NOT EXISTS core.sectors (
    sector_id TEXT PRIMARY KEY,
    parcel_id TEXT NOT NULL REFERENCES core.parcels(parcel_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    valve_code TEXT,
    area_ha NUMERIC(10, 2),
    geom geometry(MultiPolygon, 4326),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sectors_geom
    ON core.sectors
    USING GIST (geom);

CREATE TABLE IF NOT EXISTS core.sigpac_recintos (
    recinto_id BIGSERIAL PRIMARY KEY,
    parcel_id TEXT REFERENCES core.parcels(parcel_id) ON DELETE SET NULL,
    source_year INTEGER,
    province_code TEXT,
    municipality_code TEXT,
    polygon_code TEXT,
    parcel_code TEXT,
    recinto_code TEXT,
    uso_sigpac TEXT,
    slope_avg NUMERIC(8, 3),
    irrigation_coefficient NUMERIC(8, 3),
    admissibility_coefficient NUMERIC(8, 3),
    geom geometry(MultiPolygon, 4326),
    imported_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sigpac_recintos_geom
    ON core.sigpac_recintos
    USING GIST (geom);

CREATE TABLE IF NOT EXISTS iot.sensor_nodes (
    sensor_node_id TEXT PRIMARY KEY,
    parcel_id TEXT REFERENCES core.parcels(parcel_id) ON DELETE SET NULL,
    sector_id TEXT REFERENCES core.sectors(sector_id) ON DELETE SET NULL,
    vendor TEXT,
    model TEXT,
    device_class TEXT NOT NULL,
    protocol_family TEXT NOT NULL,
    connectivity_protocol TEXT NOT NULL,
    bridge_type TEXT NOT NULL,
    serial_number TEXT,
    location_note TEXT,
    thing_name TEXT,
    geom geometry(Point, 4326),
    installed_at TIMESTAMPTZ,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_sensor_nodes_geom
    ON iot.sensor_nodes
    USING GIST (geom);

CREATE TABLE IF NOT EXISTS iot.sensor_channels (
    sensor_channel_id TEXT PRIMARY KEY,
    sensor_node_id TEXT NOT NULL REFERENCES iot.sensor_nodes(sensor_node_id) ON DELETE CASCADE,
    observed_property_key TEXT NOT NULL,
    observed_property_name TEXT NOT NULL,
    unit_symbol TEXT,
    source_field TEXT,
    datatype TEXT NOT NULL DEFAULT 'numeric',
    datastream_name TEXT,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_sensor_channels_unique_node_property
    ON iot.sensor_channels(sensor_node_id, observed_property_key);

CREATE TABLE IF NOT EXISTS iot.observations (
    observation_id BIGSERIAL,
    observed_at TIMESTAMPTZ NOT NULL,
    sensor_channel_id TEXT NOT NULL REFERENCES iot.sensor_channels(sensor_channel_id) ON DELETE CASCADE,
    parcel_id TEXT REFERENCES core.parcels(parcel_id) ON DELETE SET NULL,
    sector_id TEXT REFERENCES core.sectors(sector_id) ON DELETE SET NULL,
    numeric_value DOUBLE PRECISION,
    text_value TEXT,
    quality_flag TEXT,
    source_protocol TEXT NOT NULL,
    ingestion_batch_id TEXT,
    source_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (observation_id, observed_at)
);

CREATE INDEX IF NOT EXISTS idx_observations_channel_time
    ON iot.observations(sensor_channel_id, observed_at DESC);

CREATE INDEX IF NOT EXISTS idx_observations_parcel_time
    ON iot.observations(parcel_id, observed_at DESC);

CREATE TABLE IF NOT EXISTS stage.file_imports (
    file_import_id BIGSERIAL PRIMARY KEY,
    file_name TEXT NOT NULL,
    file_kind TEXT NOT NULL,
    source_origin TEXT NOT NULL,
    uploaded_by TEXT,
    status TEXT NOT NULL DEFAULT 'received',
    row_count INTEGER,
    column_names JSONB NOT NULL DEFAULT '[]'::jsonb,
    notes TEXT,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS stage.excel_rows (
    excel_row_id BIGSERIAL PRIMARY KEY,
    file_import_id BIGINT NOT NULL REFERENCES stage.file_imports(file_import_id) ON DELETE CASCADE,
    sheet_name TEXT,
    row_number INTEGER NOT NULL,
    row_payload JSONB NOT NULL,
    normalized BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS eo.raster_assets (
    raster_asset_id BIGSERIAL PRIMARY KEY,
    parcel_id TEXT REFERENCES core.parcels(parcel_id) ON DELETE SET NULL,
    asset_type TEXT NOT NULL,
    acquisition_date DATE NOT NULL,
    provider TEXT NOT NULL,
    local_path TEXT,
    cloud_uri TEXT,
    bbox geometry(Polygon, 4326),
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_raster_assets_bbox
    ON eo.raster_assets
    USING GIST (bbox);

CREATE TABLE IF NOT EXISTS eo.parcel_daily_features (
    feature_id BIGSERIAL PRIMARY KEY,
    parcel_id TEXT NOT NULL REFERENCES core.parcels(parcel_id) ON DELETE CASCADE,
    feature_date DATE NOT NULL,
    ndvi DOUBLE PRECISION,
    ndmi DOUBLE PRECISION,
    evapotranspiration_mm DOUBLE PRECISION,
    source_asset_id BIGINT REFERENCES eo.raster_assets(raster_asset_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (parcel_id, feature_date)
);
