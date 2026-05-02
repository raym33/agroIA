INSERT INTO iot.sensor_channels (
    sensor_channel_id,
    sensor_node_id,
    observed_property_key,
    observed_property_name,
    unit_symbol,
    source_field,
    datatype,
    datastream_name,
    metadata_json
)
SELECT
    'template_' || observed_property_key,
    'template_node',
    observed_property_key,
    observed_property_name,
    unit_symbol,
    source_field,
    datatype,
    datastream_name,
    metadata_json
FROM (
    VALUES
        ('soil_moisture_pct', 'Soil Moisture', '%', 'soil_moisture', 'numeric', 'Soil Moisture', '{"category":"soil"}'::jsonb),
        ('soil_ec_us_cm', 'Conductividad electrica del suelo', 'uS/cm', 'soil_ec', 'numeric', 'Soil EC', '{"category":"soil"}'::jsonb),
        ('soil_temp_c', 'Temperatura del suelo', 'C', 'soil_temp', 'numeric', 'Soil Temperature', '{"category":"soil"}'::jsonb),
        ('air_temp_c', 'Temperatura del aire', 'C', 'air_temp', 'numeric', 'Air Temperature', '{"category":"weather"}'::jsonb),
        ('air_humidity_pct', 'Air Relative Humidity', '%', 'air_humidity', 'numeric', 'Air Humidity', '{"category":"weather"}'::jsonb),
        ('rain_mm', 'Precipitacion', 'mm', 'rainfall', 'numeric', 'Rainfall', '{"category":"weather"}'::jsonb),
        ('wind_speed_ms', 'Velocidad del viento', 'm/s', 'wind_speed', 'numeric', 'Wind Speed', '{"category":"weather"}'::jsonb),
        ('wind_direction_deg', 'Direccion del viento', 'deg', 'wind_direction', 'numeric', 'Wind Direction', '{"category":"weather"}'::jsonb),
        ('barometric_pressure_hpa', 'Presion atmosferica', 'hPa', 'pressure', 'numeric', 'Barometric Pressure', '{"category":"weather"}'::jsonb),
        ('flow_rate_m3_h', 'Caudal instantaneo', 'm3/h', 'flow_rate', 'numeric', 'Flow Rate', '{"category":"flow"}'::jsonb),
        ('flow_total_m3', 'Volumen acumulado', 'm3', 'flow_total', 'numeric', 'Flow Total', '{"category":"flow"}'::jsonb)
) AS seed(observed_property_key, observed_property_name, unit_symbol, source_field, datatype, datastream_name, metadata_json)
WHERE NOT EXISTS (
    SELECT 1
    FROM iot.sensor_channels existing
    WHERE existing.sensor_channel_id = 'template_' || seed.observed_property_key
);
