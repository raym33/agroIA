SELECT create_hypertable(
    'iot.observations',
    by_range('observed_at'),
    if_not_exists => TRUE
);

