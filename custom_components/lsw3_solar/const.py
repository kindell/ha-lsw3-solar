"""Constants for LSW-3 Solar integration."""

DOMAIN = "lsw3_solar"

# Configuration
CONF_IP_ADDRESS = "ip_address"
CONF_PORT = "port"
CONF_SERIAL_NUMBER = "serial_number"
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_PORT = 8899
DEFAULT_SCAN_INTERVAL = 30  # seconds

# Sensor types
SENSOR_TYPES = {
    # Energy
    "pv_generation_today": {
        "name": "PV Generation Today",
        "unit": "kWh",
        "icon": "mdi:solar-power",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "pv_generation_total": {
        "name": "PV Generation Total",
        "unit": "kWh",
        "icon": "mdi:solar-power",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "load_consumption_today": {
        "name": "Load Consumption Today",
        "unit": "kWh",
        "icon": "mdi:home-lightning-bolt",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "energy_purchase_today": {
        "name": "Energy Purchase Today",
        "unit": "kWh",
        "icon": "mdi:transmission-tower-import",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "energy_selling_today": {
        "name": "Energy Selling Today",
        "unit": "kWh",
        "icon": "mdi:transmission-tower-export",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    # Power
    "power_pv1": {
        "name": "PV1 Power",
        "unit": "kW",
        "icon": "mdi:solar-panel",
        "device_class": "power",
        "state_class": "measurement",
    },
    "power_pv2": {
        "name": "PV2 Power",
        "unit": "kW",
        "icon": "mdi:solar-panel",
        "device_class": "power",
        "state_class": "measurement",
    },
    "active_power_output_total": {
        "name": "Active Power Output",
        "unit": "kW",
        "icon": "mdi:flash",
        "device_class": "power",
        "state_class": "measurement",
    },
    "active_power_load_sys": {
        "name": "Load Power",
        "unit": "kW",
        "icon": "mdi:home-lightning-bolt",
        "device_class": "power",
        "state_class": "measurement",
    },
    # Voltage
    "voltage_pv1": {
        "name": "PV1 Voltage",
        "unit": "V",
        "icon": "mdi:flash",
        "device_class": "voltage",
        "state_class": "measurement",
    },
    "voltage_pv2": {
        "name": "PV2 Voltage",
        "unit": "V",
        "icon": "mdi:flash",
        "device_class": "voltage",
        "state_class": "measurement",
    },
    "voltage_phase_r": {
        "name": "Grid Voltage",
        "unit": "V",
        "icon": "mdi:transmission-tower",
        "device_class": "voltage",
        "state_class": "measurement",
    },
    # Current
    "current_pv1": {
        "name": "PV1 Current",
        "unit": "A",
        "icon": "mdi:current-dc",
        "device_class": "current",
        "state_class": "measurement",
    },
    "current_pv2": {
        "name": "PV2 Current",
        "unit": "A",
        "icon": "mdi:current-dc",
        "device_class": "current",
        "state_class": "measurement",
    },
    # Frequency
    "frequency_grid": {
        "name": "Grid Frequency",
        "unit": "Hz",
        "icon": "mdi:sine-wave",
        "device_class": "frequency",
        "state_class": "measurement",
    },
    # Temperature
    "temperature_env1": {
        "name": "Ambient Temperature",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "state_class": "measurement",
    },
    "temperature_heatsink1": {
        "name": "Heatsink Temperature",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "state_class": "measurement",
    },
    # Other
    "generation_time_today": {
        "name": "Generation Time Today",
        "unit": "min",
        "icon": "mdi:clock-outline",
        "state_class": "total_increasing",
    },
    "sys_state": {
        "name": "System State",
        "unit": "",
        "icon": "mdi:state-machine",
    },
}
