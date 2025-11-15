"""Sensor platform for LSW-3 Solar integration."""
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    UnitOfEnergy,
    UnitOfPower,
    UnitOfElectricPotential,
    UnitOfElectricCurrent,
    UnitOfFrequency,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: dict,
    async_add_entities: AddEntitiesCallback,
    discovery_info=None,
) -> None:
    """Set up the LSW-3 Solar sensor platform."""
    coordinator = hass.data[DOMAIN]["coordinator"]

    sensors = []
    for sensor_type in SENSOR_TYPES:
        sensors.append(LSW3Sensor(coordinator, sensor_type))

    async_add_entities(sensors, True)


class LSW3Sensor(CoordinatorEntity, SensorEntity):
    """Representation of an LSW-3 Solar Sensor."""

    def __init__(self, coordinator, sensor_type):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = f"LSW-3 {SENSOR_TYPES[sensor_type]['name']}"
        self._attr_unique_id = f"lsw3_{coordinator.serial_number}_{sensor_type}"
        self._attr_icon = SENSOR_TYPES[sensor_type].get("icon")
        self._attr_device_class = SENSOR_TYPES[sensor_type].get("device_class")
        self._attr_state_class = SENSOR_TYPES[sensor_type].get("state_class")

        # Set native unit
        unit = SENSOR_TYPES[sensor_type].get("unit", "")
        if unit == "kWh":
            self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        elif unit == "kW":
            self._attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
        elif unit == "V":
            self._attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
        elif unit == "A":
            self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
        elif unit == "Hz":
            self._attr_native_unit_of_measurement = UnitOfFrequency.HERTZ
        elif unit == "°C":
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        elif unit == "min":
            self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        else:
            self._attr_native_unit_of_measurement = unit

    @property
    def device_info(self):
        """Return device information about this LSW-3 inverter."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.serial_number)},
            "name": f"LSW-3 Solar Inverter ({self.coordinator.serial_number})",
            "manufacturer": "Solarman",
            "model": "LSW-3",
            "sw_version": "1.0.0",
        }

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data:
            sensor_data = self.coordinator.data.get(self._sensor_type)
            if sensor_data:
                return sensor_data.get("value")
        return None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
