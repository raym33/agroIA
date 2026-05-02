# Compatible sensors and hardware

## Compatibility rule

Do not optimize for “works with this app” as a marketing claim. Optimize for open or bridgeable field protocols:

- `SDI-12`
- `RS485 / Modbus RTU`
- `LoRaWAN`
- `pulse`
- `4-20 mA`
- `0-10 V`

If a device speaks one of those interfaces cleanly, it can usually be integrated without locking the project to a vendor cloud.

## Recommended devices by type

### Soil probes

#### Robust wired option

- `METER TEROS 12`
  - Protocol: `SDI-12`
  - Measures: soil water content, temperature, and EC
  - Best for:
    - higher quality measurements
    - long-term deployments
    - projects that can support a logger or wired edge device

#### Fast LoRaWAN option

- `Milesight EM500-SMTC`
  - Protocol: `LoRaWAN`
  - Measures: soil moisture, temperature, and conductivity
  - Best for:
    - quick pilots
    - remote plots
    - low-civil-work deployments

#### Budget LoRaWAN option

- `Dragino LSE01`
  - Protocol: `LoRaWAN`
  - Measures: soil moisture, temperature, and conductivity
  - Best for:
    - proof-of-concept deployments
    - small budgets

### Weather stations

#### Compact open-protocol station

- `Campbell Scientific ClimaVue 50 G2`
  - Protocol: `SDI-12`
  - Measures: compact all-in-one weather variables
  - Best for:
    - open, more technical stacks
    - own edge device or logger ownership

#### All-in-one LoRaWAN station

- `Milesight WTS506`
  - Protocol: `LoRaWAN`
  - Measures: temperature, humidity, wind, pressure, and rainfall
  - Best for:
    - fast deployment
    - teams that prefer not to manage a separate logger

### Flow meters

#### Irrigation-oriented standard outputs

- `Valley 3000 Flowmeter`
  - Useful outputs: `pulse`, `4-20 mA`
  - Best for:
    - irrigation infrastructure
    - pivots and agricultural water monitoring

#### More industrial environment

- `Badger Meter ModMAG M2000`
  - Useful outputs: `RS485 Modbus RTU`, `Modbus TCP/IP`, `RS232`
  - Best for:
    - wells, pumping stations, or critical head-end installations
    - sites that already run PLC or industrial networks

#### Fast LoRaWAN pilot

- `Dragino SW3L`
  - Protocol: `LoRaWAN`
  - Provides: water flow / volume depending on configuration
  - Best for:
    - quick pilots
    - low-complexity deployments without PLCs

## Bridges and adapters

### For existing farmer hardware

- `Milesight UC300`
  - Handles: `pulse`, `RS485 Modbus`, `4-20 mA`, `0-10 V`
  - Best when:
    - the farmer already has counters or wired sensors
    - replacing installed hardware would be wasteful

- `Milesight UC100`
  - Handles: `RS485 Modbus RTU -> LoRaWAN`
  - Best when:
    - the field device is Modbus
    - long cable runs are undesirable

## Practical buying rules

### Buy against lock-in

Prefer devices with:

- documented protocols
- exportable payloads
- simple backhaul paths

Avoid:

- mandatory proprietary clouds
- apps with no export path
- devices with undocumented payloads or black-box integrations

### What to choose by phase

- Phase 1, pilot:
  - `LoRaWAN` and low-friction hardware
- Phase 2, serious operation:
  - strong soil probes
  - a reliable weather station
  - a standard-output flow meter
- Phase 3, scale:
  - mixed `SDI-12`, `Modbus`, and `LoRaWAN` behind a single SensorThings layer
