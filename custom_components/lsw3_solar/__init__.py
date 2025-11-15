"""LSW-3 Solar Inverter integration for Home Assistant."""
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, CONF_IP_ADDRESS, CONF_PORT, CONF_SERIAL_NUMBER, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
from .lsw3_protocol import LSW3Reader

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the LSW-3 Solar component from YAML configuration."""
    hass.data.setdefault(DOMAIN, {})

    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]

    ip_address = conf[CONF_IP_ADDRESS]
    port = conf.get(CONF_PORT, 8899)
    serial_number = conf[CONF_SERIAL_NUMBER]
    scan_interval = conf.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    coordinator = LSW3DataUpdateCoordinator(
        hass,
        ip_address=ip_address,
        port=port,
        serial_number=serial_number,
        scan_interval=scan_interval,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN]["coordinator"] = coordinator

    # Forward setup to sensor platform
    await hass.helpers.discovery.async_load_platform(Platform.SENSOR, DOMAIN, {}, config)

    return True


class LSW3DataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching LSW-3 data."""

    def __init__(
        self,
        hass: HomeAssistant,
        ip_address: str,
        port: int,
        serial_number: int,
        scan_interval: int,
    ) -> None:
        """Initialize."""
        self.ip_address = ip_address
        self.port = port
        self.serial_number = serial_number
        self.reader = LSW3Reader(ip_address, port, serial_number)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self):
        """Fetch data from LSW-3."""
        try:
            # Run blocking IO in executor
            success = await self.hass.async_add_executor_job(
                self.reader.read_all
            )

            if not success:
                raise UpdateFailed("Failed to read data from LSW-3")

            return self.reader.data

        except Exception as err:
            raise UpdateFailed(f"Error communicating with LSW-3: {err}") from err
