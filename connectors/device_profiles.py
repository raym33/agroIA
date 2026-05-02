from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceProfile:
    category: str
    vendor: str
    model: str
    field_protocol: str
    backhaul_protocol: str
    bridge_recommendation: str
    notes: str


RECOMMENDED_DEVICE_PROFILES = [
    DeviceProfile(
        category="soil_probe",
        vendor="METER Group",
        model="TEROS 12",
        field_protocol="SDI-12",
        backhaul_protocol="wired logger or protocol bridge",
        bridge_recommendation="SDI-12 logger or RS-485/LoRaWAN bridge",
        notes="Robust probe for soil moisture, temperature, and EC. Good option when measurement quality matters most.",
    ),
    DeviceProfile(
        category="soil_probe",
        vendor="Milesight",
        model="EM500-SMTC",
        field_protocol="embedded",
        backhaul_protocol="LoRaWAN",
        bridge_recommendation="The Things Stack MQTT -> SensorThings mapper",
        notes="Easy to deploy in the field when you do not want cabling or a dedicated logger.",
    ),
    DeviceProfile(
        category="soil_probe",
        vendor="Dragino",
        model="LSE01",
        field_protocol="embedded",
        backhaul_protocol="LoRaWAN",
        bridge_recommendation="LoRaWAN gateway + MQTT/webhook normalization",
        notes="Budget-friendly option to start with soil moisture, temperature, and EC.",
    ),
    DeviceProfile(
        category="weather_station",
        vendor="Campbell Scientific",
        model="ClimaVue 50 G2",
        field_protocol="SDI-12",
        backhaul_protocol="wired logger or edge device",
        bridge_recommendation="SDI-12 edge device -> MQTT/SensorThings",
        notes="Strong option when you want a compact weather station with an open protocol.",
    ),
    DeviceProfile(
        category="weather_station",
        vendor="Milesight",
        model="WTS506",
        field_protocol="embedded",
        backhaul_protocol="LoRaWAN",
        bridge_recommendation="LoRaWAN gateway + MQTT/webhook normalization",
        notes="Solar-powered all-in-one LoRaWAN station for fast deployments.",
    ),
    DeviceProfile(
        category="flow_meter",
        vendor="Valley",
        model="3000 Flowmeter",
        field_protocol="pulse or 4-20mA",
        backhaul_protocol="wired or bridged",
        bridge_recommendation="Pulse counter or analog input bridge",
        notes="Fits well when the focus is agricultural irrigation and flow telemetry.",
    ),
    DeviceProfile(
        category="flow_meter",
        vendor="Badger Meter",
        model="ModMAG M2000",
        field_protocol="RS485 Modbus RTU / Modbus TCP / pulse ecosystem",
        backhaul_protocol="industrial network",
        bridge_recommendation="Modbus RTU bridge or direct industrial ingest",
        notes="More industrial and robust when the flow meter is a critical component.",
    ),
    DeviceProfile(
        category="flow_meter",
        vendor="Dragino",
        model="SW3L",
        field_protocol="embedded",
        backhaul_protocol="LoRaWAN",
        bridge_recommendation="LoRaWAN gateway + MQTT/webhook normalization",
        notes="Useful for pilots where you want accumulated volume without much PLC complexity.",
    ),
    DeviceProfile(
        category="bridge",
        vendor="Milesight",
        model="UC300",
        field_protocol="Pulse / RS485 Modbus / 4-20mA / 0-10V",
        backhaul_protocol="LoRaWAN or 4G",
        bridge_recommendation="Normalize to SensorThings entities",
        notes="Very useful bridge when the farmer already has installed counters or wired sensors.",
    ),
]
