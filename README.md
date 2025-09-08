# BLE Scanner with MQTT Integration

A Python tool for scanning Bluetooth Low Energy (BLE) devices in parallel and publishing results to MQTT brokers. Perfect for Home Assistant integration and IoT monitoring.

## Features

- 🚀 **Parallel scanning** - Scan multiple BLE devices simultaneously
- 📡 **MQTT integration** - Publish results to MQTT brokers
- ⏱️ **Configurable timeouts** - Set custom scan timeouts
- 🏠 **Home Assistant ready** - Compatible with HA MQTT discovery
- 🔄 **Real-time updates** - Individual device results published as they arrive
- 📊 **Summary reports** - Overall scan statistics

## Installation

```bash
pip install -e .
```

## Quick Start

### Basic Usage (No MQTT)

```python
import asyncio
from bt_scan import scan_devices

# Scan devices without MQTT
devices = ["AA:BB:CC:DD:EE:FF", "11:22:33:44:55:66"]
asyncio.run(scan_devices(devices, timeout=30))
```

### With MQTT Integration

```python
import asyncio
from bt_scan import scan_devices, MQTTConfig

# Configure MQTT
mqtt_config = MQTTConfig(
    broker="192.168.1.100",
    port=1883,
    username="mqtt_user",
    password="mqtt_pass",
    topic_prefix="home/bt_scan"
)

# Scan with MQTT publishing
devices = ["AA:BB:CC:DD:EE:FF", "11:22:33:44:55:66"]
asyncio.run(scan_devices(devices, timeout=30, mqtt_config=mqtt_config))
```

### Command Line Usage

```bash
# Run with default settings
bt-scan

# Or run examples
python examples.py
```

## MQTT Topics

The scanner publishes to two types of topics:

### Individual Device Results
**Topic:** `{topic_prefix}/device/{mac_address}`
**Payload:**
```json
{
  "address": "AA:BB:CC:DD:EE:FF",
  "found": true,
  "timestamp": 1703123456.789,
  "name": "My Device",
  "rssi": -45
}
```

### Scan Summary
**Topic:** `{topic_prefix}/summary`
**Payload:**
```json
{
  "total_devices": 5,
  "found_count": 3,
  "found_devices": ["AA:BB:CC:DD:EE:FF", "11:22:33:44:55:66"],
  "scan_time": 12.34,
  "timestamp": 1703123456.789
}
```

## Configuration

### Environment Variables

Set these environment variables for automatic MQTT configuration:

```bash
export MQTT_BROKER="192.168.1.100"
export MQTT_PORT="1883"
export MQTT_USERNAME="your_username"
export MQTT_PASSWORD="your_password"
export MQTT_TOPIC_PREFIX="home/bt_scan"
```

### Programmatic Configuration

```python
from bt_scan import MQTTConfig

config = MQTTConfig(
    broker="localhost",
    port=1883,
    username=None,  # Optional
    password=None,  # Optional
    topic_prefix="bt_scan"
)
```

## Home Assistant Integration

### MQTT Sensor Configuration

Add to your `configuration.yaml`:

```yaml
mqtt:
  sensor:
    - name: "BLE Device Scanner"
      state_topic: "home/bt_scan/summary"
      value_template: "{{ value_json.found_count }}"
      json_attributes_topic: "home/bt_scan/summary"
      unit_of_measurement: "devices"
      icon: "mdi:bluetooth"
    
    - name: "My BLE Device"
      state_topic: "home/bt_scan/device/AA_BB_CC_DD_EE_FF"
      value_template: "{{ 'home' if value_json.found else 'away' }}"
      json_attributes_topic: "home/bt_scan/device/AA_BB_CC_DD_EE_FF"
      icon: "mdi:bluetooth-connect"
```

### Automation Example

```yaml
automation:
  - alias: "BLE Device Presence"
    trigger:
      - platform: mqtt
        topic: "home/bt_scan/device/+"
    condition:
      - condition: template
        value_template: "{{ trigger.payload_json.found }}"
    action:
      - service: notify.mobile_app
        data:
          message: "Device {{ trigger.payload_json.name }} is present"
```

## Command Line Usage

```bash
# Basic scan
python bt_scan.py

# With environment variables for MQTT
MQTT_BROKER=192.168.1.100 python bt_scan.py
```

## Performance

- **Sequential scanning**: 5 devices × 30s timeout = 150s total
- **Parallel scanning**: 5 devices × 30s timeout = ~30s total (5x faster!)

## Error Handling

The scanner gracefully handles:
- Device not found
- Connection timeouts
- MQTT broker unavailable
- Network interruptions

## Troubleshooting

### Common Issues

1. **Permission denied on Linux**:
   ```bash
   sudo setcap cap_net_raw+eip $(which python3)
   ```

2. **MQTT connection fails**:
   - Check broker IP and port
   - Verify credentials
   - Ensure firewall allows connection

3. **No devices found**:
   - Verify MAC addresses are correct
   - Check if devices are in range
   - Ensure devices are advertising

### Debug Mode

Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
