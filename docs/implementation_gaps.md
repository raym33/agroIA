# What is still missing

This repository is intentionally ahead on structure and behind on real agricultural data. That is normal for an MVP, but it should be made explicit.

## Highest-priority gaps

### 1. Real labeled field data

The current models are useful as scaffolds and demos, not as validated agronomic products.

Still needed:

- irrigation history per plot
- real applied water
- yield or quality outcomes
- observed pest labels or scouting records
- plot-level timestamps and stable identifiers

### 2. Plot geometry and spatial joins

Still needed:

- actual SIGPAC ingestion
- farmer plot mapping to official recintos
- sector-level geometry when irrigation sectors differ from plot boundaries

### 3. Sensor ingestion

Still needed:

- production adapters for real gateways or devices
- payload normalization per vendor
- sensor health monitoring
- calibration and quality flags

### 4. Visual pipeline

Still needed:

- labeled field photos
- local YOLO weights trained on relevant crop/pest classes
- conservative UX around false positives

### 5. Product hardening

Still needed:

- authentication and user roles
- secure secrets handling
- deployment profiles
- backups and migrations
- better observability and logging

## Important model caveats

### Pest risk

Climate-only pest prediction is weak without plot-level labels. Weather helps, but real field scouting data is necessary to make the model worth trusting.

### Irrigation

Irrigation is the strongest first use case, but still needs:

- plot-specific crop coefficients or proxies
- better soil information
- real applied water outcomes
- operational validation with farmers or agronomists

## Recommended next steps

1. Interview 3-5 farmers or technicians.
2. Collect 1-3 real spreadsheets.
3. Normalize plot identifiers.
4. Build one repeatable ingestion path.
5. Benchmark on real data before adding more model complexity.
