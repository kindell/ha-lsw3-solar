# LSW-3 Solar Inverter Integration for Home Assistant

Custom integration for reading data from Sofar solar inverters via LSW-3 WiFi logger.

## Features

✅ **No Cloud Required** - Direct local TCP/IP communication
✅ **Complete Sensor Coverage** - Energy, Power, Voltage, Current, Temperature
✅ **Energy Dashboard Ready** - Sensors configured for HA Energy Dashboard
✅ **Serial 27 Support** - Works with problematic serial 27xxxxxxxx loggers
✅ **Auto Discovery** - All sensors automatically created

## Supported Data

### Energy
- PV Generation (Today & Total)
- Load Consumption
- Grid Import/Export

### Power
- PV String Power (PV1 & PV2)
- Active Power Output
- Load Power

### Electrical
- PV Voltage & Current (per string)
- Grid Voltage & Frequency

### System
- Ambient & Heatsink Temperature
- Generation Time
- System State

## Installation

### Method 1: Manual Installation

1. Copy the `custom_components/lsw3_solar` folder to your Home Assistant `custom_components` directory:

   ```bash
   # On your Home Assistant server:
   mkdir -p /config/custom_components
   cp -r custom_components/lsw3_solar /config/custom_components/
   ```

2. Add to your `configuration.yaml`:

   ```yaml
   lsw3_solar:
     ip_address: "10.42.1.9"          # Your LSW-3 IP address
     port: 8899                        # Default: 8899
     serial_number: 2734303872         # Your logger serial number
     scan_interval: 30                 # Update interval in seconds (default: 30)
   ```

3. Restart Home Assistant

4. Check for new sensors starting with "LSW-3"

### Method 2: Using Samba Share

If you have the Samba add-on installed:

1. Connect to `\\homeassistant.local\config`
2. Create folder `custom_components` if it doesn't exist
3. Copy the `lsw3_solar` folder into `custom_components`
4. Edit `configuration.yaml` (see above)
5. Restart Home Assistant

## Configuration

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `ip_address` | IP address of your LSW-3 logger | `10.42.1.9` |
| `serial_number` | Logger serial number (from web UI) | `2734303872` |

### Optional Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `port` | TCP port | `8899` |
| `scan_interval` | Update interval (seconds) | `30` |

## Finding Your Serial Number

1. Open http://YOUR_LSW3_IP in a browser
2. Login with `admin` / `admin`
3. Look for "Device serial number" on the status page

## Energy Dashboard Setup

After sensors are created:

1. Go to **Settings** → **Dashboards** → **Energy**
2. Click **Add Solar Production**
3. Select `sensor.lsw3_pv_generation_today`
4. Click **Add**

Optional:
- **Grid Consumption**: `sensor.lsw3_energy_purchase_today`
- **Return to Grid**: `sensor.lsw3_energy_selling_today`

## Troubleshooting

### No sensors appearing

1. Check Home Assistant logs: **Settings** → **System** → **Logs**
2. Look for errors containing "lsw3"
3. Verify LSW-3 is reachable: `ping YOUR_LSW3_IP`
4. Test connectivity: `nc -zv YOUR_LSW3_IP 8899`

### Sensors show "Unavailable"

1. Check if LSW-3 IP changed (DHCP)
2. Verify serial number is correct
3. Check that port 8899 is not blocked by firewall

### Data not updating

1. Check `scan_interval` - increase if inverter is slow
2. At night, power sensors may show 0 (expected)
3. Check Home Assistant CPU load

## Development

### Protocol Information

This integration uses the LSW-3 proprietary protocol over TCP port 8899:
- Frame-based communication with checksums
- Modbus-style register reading
- Supports registers 0x400-0x4AF, 0x580-0x589, 0x600-0x611, 0x680-0x69B

### Testing

Test the protocol implementation:

```bash
cd custom_components/lsw3_solar
python3 lsw3_protocol.py
```

## Credits

Based on research from:
- [kubaceg/Sofar-g3-lsw3-logger-reader](https://github.com/kubaceg/Sofar-g3-lsw3-logger-reader)
- [StephanJoubert/home_assistant_solarman](https://github.com/StephanJoubert/home_assistant_solarman)

## License

MIT License - See LICENSE file

## Support

For issues, please create a GitHub issue with:
- Home Assistant version
- LSW-3 firmware version
- Relevant logs
- Configuration (hide serial number)
