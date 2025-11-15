#!/usr/bin/env python3
"""
LSW-3 Logger Full - Complete sensor reading for Sofar solar inverters
"""

import socket
import struct
import sys
import json
from datetime import datetime

# CRC16 MODBUS implementation
def crc16_modbus(data):
    """Calculate CRC16 MODBUS checksum"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def create_lsw3_request(serial_number, start_register, end_register):
    """Create LSW-3 request frame"""
    buf = bytearray(36)

    # Preamble
    buf[0] = 0xa5
    struct.pack_into('>H', buf, 1, 0x1700)
    struct.pack_into('>H', buf, 3, 0x1045)
    buf[5] = 0x00
    buf[6] = 0x00

    # Serial number (little-endian)
    struct.pack_into('<I', buf, 7, serial_number)

    # Control byte
    buf[11] = 0x02

    # Modbus command
    struct.pack_into('>H', buf, 26, 0x0103)

    # Start register and count (big-endian)
    struct.pack_into('>H', buf, 28, start_register)
    register_count = end_register - start_register + 1
    struct.pack_into('>H', buf, 30, register_count)

    # Modbus CRC (little-endian)
    modbus_crc = crc16_modbus(buf[26:32])
    struct.pack_into('<H', buf, 32, modbus_crc)

    # Frame checksum
    checksum = sum(buf[1:34]) & 0xFF
    buf[34] = checksum

    # End marker
    buf[35] = 0x15

    return bytes(buf)

def parse_u16(data, offset):
    """Parse unsigned 16-bit (big-endian)"""
    return struct.unpack_from('>H', data, offset)[0]

def parse_u32(data, offset):
    """Parse unsigned 32-bit (big-endian)"""
    return struct.unpack_from('>I', data, offset)[0]

def parse_i16(data, offset):
    """Parse signed 16-bit (big-endian)"""
    return struct.unpack_from('>h', data, offset)[0]

def read_registers(ip, port, serial_number, start_register, end_register):
    """Read register range from LSW-3"""
    request = create_lsw3_request(serial_number, start_register, end_register)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(5)
        sock.connect((ip, port))
        sock.sendall(request)

        response = bytearray()
        while True:
            chunk = sock.recv(2048)
            if not chunk:
                break
            response.extend(chunk)

            if len(response) >= 28:
                data_length = response[27]
                if len(response) >= 28 + data_length:
                    break

        data_length = response[27]
        return response[28:28 + data_length]

class LSW3Reader:
    """LSW-3 Solar Inverter Data Reader"""

    def __init__(self, ip, port, serial_number):
        self.ip = ip
        self.port = port
        self.serial_number = serial_number
        self.data = {}

    def read_field(self, reg_range, register, value_type, factor, name):
        """Read and parse a single field from register data"""
        offset = (register - reg_range[0]) * 2

        if value_type == "U16":
            raw = parse_u16(reg_range[2], offset)
        elif value_type == "U32":
            raw = parse_u32(reg_range[2], offset)
        elif value_type == "I16":
            raw = parse_i16(reg_range[2], offset)
        else:
            return None

        if factor:
            value = raw * float(factor)
        else:
            value = raw

        return {"raw": raw, "value": value, "type": value_type}

    def read_energy_totals(self):
        """Read energy production and consumption totals"""
        print("📊 Reading Energy Totals...")
        data = read_registers(self.ip, self.port, self.serial_number, 0x684, 0x69B)
        reg_range = (0x684, 0x69B, data)

        fields = {
            "pv_generation_today": (0x684, "U32", "0.01", "kWh"),
            "pv_generation_total": (0x686, "U32", "0.1", "kWh"),
            "load_consumption_today": (0x688, "U32", "0.01", "kWh"),
            "load_consumption_total": (0x68A, "U32", "0.1", "kWh"),
            "energy_purchase_today": (0x68C, "U32", "0.01", "kWh"),
            "energy_purchase_total": (0x68E, "U32", "0.1", "kWh"),
            "energy_selling_today": (0x690, "U32", "0.01", "kWh"),
            "energy_selling_total": (0x692, "U32", "0.1", "kWh"),
        }

        for name, (reg, vtype, factor, unit) in fields.items():
            result = self.read_field(reg_range, reg, vtype, factor, name)
            if result:
                self.data[name] = {**result, "unit": unit}

    def read_pv_output(self):
        """Read PV string voltage, current, and power"""
        print("☀️  Reading PV Output...")
        data = read_registers(self.ip, self.port, self.serial_number, 0x584, 0x589)
        reg_range = (0x584, 0x589, data)

        fields = {
            "voltage_pv1": (0x584, "U16", "0.1", "V"),
            "current_pv1": (0x585, "U16", "0.01", "A"),
            "power_pv1": (0x586, "U16", "0.01", "kW"),
            "voltage_pv2": (0x587, "U16", "0.1", "V"),
            "current_pv2": (0x588, "U16", "0.01", "A"),
            "power_pv2": (0x589, "U16", "0.01", "kW"),
        }

        for name, (reg, vtype, factor, unit) in fields.items():
            result = self.read_field(reg_range, reg, vtype, factor, name)
            if result:
                self.data[name] = {**result, "unit": unit}

    def read_grid_output(self):
        """Read grid voltage, frequency, and power"""
        print("⚡ Reading Grid Output...")
        data = read_registers(self.ip, self.port, self.serial_number, 0x484, 0x4AF)
        reg_range = (0x484, 0x4AF, data)

        fields = {
            "frequency_grid": (0x484, "U16", "0.01", "Hz"),
            "active_power_output_total": (0x485, "I16", "0.01", "kW"),
            "active_power_pcc_total": (0x488, "I16", "0.01", "kW"),
            "voltage_phase_r": (0x48D, "U16", "0.1", "V"),
            "current_output_r": (0x48E, "U16", "0.01", "A"),
            "active_power_output_r": (0x48F, "I16", "0.01", "kW"),
            "active_power_load_sys": (0x4AF, "U16", "0.01", "kW"),
        }

        for name, (reg, vtype, factor, unit) in fields.items():
            result = self.read_field(reg_range, reg, vtype, factor, name)
            if result:
                self.data[name] = {**result, "unit": unit}

    def read_system_info(self):
        """Read system temperatures and status"""
        print("🌡️  Reading System Info...")
        data = read_registers(self.ip, self.port, self.serial_number, 0x404, 0x431)
        reg_range = (0x404, 0x431, data)

        fields = {
            "sys_state": (0x404, "U16", None, ""),
            "countdown": (0x417, "U16", "1", "s"),
            "temperature_env1": (0x418, "I16", "1", "°C"),
            "temperature_heatsink1": (0x41A, "I16", "1", "°C"),
            "generation_time_today": (0x426, "U16", "1", "min"),
            "generation_time_total": (0x427, "U32", "1", "min"),
            "insulation_resistance": (0x42B, "U16", "1", "kΩ"),
        }

        for name, (reg, vtype, factor, unit) in fields.items():
            result = self.read_field(reg_range, reg, vtype, factor, name)
            if result:
                self.data[name] = {**result, "unit": unit}

    def read_all(self):
        """Read all sensor data"""
        print("\n" + "=" * 70)
        print("🌞 LSW-3 Solar Inverter - Complete Data Read")
        print("=" * 70)

        try:
            self.read_energy_totals()
            self.read_pv_output()
            self.read_grid_output()
            self.read_system_info()

            print("\n✅ All data read successfully!")
            return True
        except Exception as e:
            print(f"\n❌ Error reading data: {e}")
            import traceback
            traceback.print_exc()
            return False

    def print_summary(self):
        """Print human-readable summary"""
        print("\n" + "=" * 70)
        print("📈 SENSOR DATA SUMMARY")
        print("=" * 70)

        print("\n🔋 ENERGY PRODUCTION:")
        print(f"  Today:      {self.data.get('pv_generation_today', {}).get('value', 'N/A')} kWh")
        print(f"  Total:      {self.data.get('pv_generation_total', {}).get('value', 'N/A')} kWh")
        print(f"  Runtime:    {self.data.get('generation_time_today', {}).get('value', 'N/A')} min today")

        print("\n☀️  PV STRINGS:")
        pv1_power = self.data.get('power_pv1', {}).get('value', 0)
        pv1_voltage = self.data.get('voltage_pv1', {}).get('value', 0)
        pv1_current = self.data.get('current_pv1', {}).get('value', 0)
        print(f"  PV1:        {pv1_power} kW  ({pv1_voltage} V × {pv1_current} A)")

        pv2_power = self.data.get('power_pv2', {}).get('value', 0)
        pv2_voltage = self.data.get('voltage_pv2', {}).get('value', 0)
        pv2_current = self.data.get('current_pv2', {}).get('value', 0)
        print(f"  PV2:        {pv2_power} kW  ({pv2_voltage} V × {pv2_current} A)")

        print("\n⚡ GRID:")
        grid_power = self.data.get('active_power_output_total', {}).get('value', 0)
        grid_voltage = self.data.get('voltage_phase_r', {}).get('value', 0)
        grid_freq = self.data.get('frequency_grid', {}).get('value', 0)
        print(f"  Output:     {grid_power} kW")
        print(f"  Voltage:    {grid_voltage} V")
        print(f"  Frequency:  {grid_freq} Hz")

        load_power = self.data.get('active_power_load_sys', {}).get('value', 0)
        print(f"  Load:       {load_power} kW")

        print("\n🌡️  SYSTEM:")
        temp_env = self.data.get('temperature_env1', {}).get('value', 'N/A')
        temp_hs = self.data.get('temperature_heatsink1', {}).get('value', 'N/A')
        sys_state = self.data.get('sys_state', {}).get('value', 'N/A')
        print(f"  State:      {sys_state}")
        print(f"  Ambient:    {temp_env} °C")
        print(f"  Heatsink:   {temp_hs} °C")

        print("\n" + "=" * 70)

    def to_json(self):
        """Export data as JSON"""
        return json.dumps({
            "timestamp": datetime.now().isoformat(),
            "serial_number": self.serial_number,
            "sensors": self.data
        }, indent=2)

def main():
    # Configuration
    LSW3_IP = "10.42.1.9"
    LSW3_PORT = 8899
    SERIAL_NUMBER = 2734303872

    # Read all data
    reader = LSW3Reader(LSW3_IP, LSW3_PORT, SERIAL_NUMBER)

    if reader.read_all():
        reader.print_summary()

        # Save to JSON
        json_file = "/tmp/lsw3_data.json"
        with open(json_file, 'w') as f:
            f.write(reader.to_json())
        print(f"\n💾 Data saved to: {json_file}")

        print("\n🎉 SUCCESS!")
    else:
        print("\n❌ FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()
