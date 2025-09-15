# BT Scan - Bluetooth Presence Scanner for Home Assistant

A simple Bluetooth scanner designed to work with Home Assistant, providing more control over device presence detection than the standard Home Assistant BT presence sensor.

## Reasoning

I created this project because a simple Home Assistant BT presence sensor won't allow me to scan for a device when I want to. It is also able to scan for a device longer (for example when you are on your way home), providing more reliable presence detection for your smart home automation.

## Features

- **On-demand scanning**: Trigger Bluetooth scans manually via MQTT commands
- **Automatic scanning**: Configurable periodic scanning of all devices
- **Individual device scanning**: Scan specific devices independently
- **Home Assistant integration**: Automatic discovery and device tracker entities
- **Configurable timeouts**: Adjust scan duration for different scenarios
- **MQTT-based control**: Full integration with Home Assistant via MQTT

## Installation

### Prerequisites

- Python 3.8 or higher
- Bluetooth adapter with BLE support
- MQTT broker (e.g., Mosquitto)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/mihaiLambru/bluetooth-presence-service.git
cd bt_scan
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

4. Configure the application (see Configuration section below)

5. Run the application:
```bash
python main.py
```

## Configuration

The application is configured via the `config.json` file. Here's a detailed breakdown of each configuration option:

### config.json Structure

```json
{
    "devices_list": [
        "AC:DF:A1:C3:80:E3"
    ],
    "automatic_scan": 60,
    "scan_timeout": 600,
    "mqtt_host": "localhost",
    "mqtt_port": 1883,
    "mqtt_username": "user",
    "mqtt_password": "plain_password"
}
```

### Configuration Options

#### `devices_list` (array of strings)
- **Description**: List of Bluetooth device MAC addresses to scan for
- **Format**: MAC addresses in format `XX:XX:XX:XX:XX:XX`
- **Example**: `["AC:DF:A1:C3:80:E3", "12:34:56:78:90:AB"]`
- **Required**: Yes

#### `automatic_scan` (integer)
- **Description**: Interval in seconds for automatic scanning of all devices
- **Default**: 60 seconds
- **Special values**:
  - `0`: Disable automatic scanning (manual control only)
  - `> 0`: Scan all devices every N seconds
- **Example**: `60` (scan every minute)

#### `scan_timeout` (integer)
- **Description**: Maximum time in seconds to wait for each device during scanning. This can be overwritten by Home Assistance
- **Default**: 60 seconds
- **Recommended**: 300-600 seconds for reliable detection
- **Example**: `600` (10 minutes timeout)

#### `mqtt_host` (string)
- **Description**: MQTT broker hostname or IP address
- **Format**: `mqtt://hostname` or `mqtt://ip_address`
- **Example**: `"mqtt://192.168.1.100"` or `"mqtt://homeassistant.local"`

#### `mqtt_port` (integer)
- **Description**: MQTT broker port number
- **Default**: 1883 (standard MQTT port)
- **Example**: `1883`

#### `mqtt_username` (string)
- **Description**: Username for MQTT broker authentication
- **Example**: `"mqtt_user"`

#### `mqtt_password` (string)
- **Description**: Password for MQTT broker authentication
- **⚠️ Security Warning**: Currently stored in plain text
- **Future Enhancement**: Encrypted password support planned
- **Example**: `"your_secure_password"`

### Security Considerations

**⚠️ Important Security Notice**: The current version stores the MQTT password in plain text within the `config.json` file. Please be careful with the current configuration:

1. **File Permissions**: Ensure `config.json` has restrictive file permissions:
   ```bash
   chmod 600 config.json
   ```

2. **Access Control**: Limit access to the configuration file to authorized users only

3. **Network Security**: Use MQTT over TLS (port 8883) when possible for encrypted communication

4. **Future Enhancement**: The project will support encrypted password storage in future versions to improve security

## Home Assistant Integration

The application automatically integrates with Home Assistant through MQTT discovery:

### Device Trackers
- Each device in `devices_list` becomes a device tracker entity
- States: `home` (device found) or `not_home` (device not found)
- Entity naming: `device_tracker.XX_XX_XX_XX_XX_XX`

### Control Entities

#### Scan All Button
- **Entity**: `button.scan_all`
- **Function**: Triggers scanning of all configured devices
- **Topic**: `homeassistant/button/scan_all_button/command`

#### Individual Device Scan Buttons
- **Entity**: `button.scan_XX_XX_XX_XX_XX_XX`
- **Function**: Triggers scanning of a specific device
- **Topic**: `homeassistant/button/scan_device_button_XX_XX_XX_XX_XX_XX/command`

#### Scan Timeout Number
- **Entity**: `number.scan_timeout`
- **Function**: Adjusts the scan timeout duration
- **Topic**: `homeassistant/number/scan_timeout/command`

## Usage

### Automatic Mode
When `automatic_scan` is set to a value greater than 0, the application will:
1. Start automatically
2. Scan all devices every N seconds
3. Update Home Assistant device tracker states
4. Continue running until stopped

### Manual Mode
When `automatic_scan` is set to 0, the application will:
1. Start and wait for MQTT commands
2. Only scan when triggered via Home Assistant buttons
3. Provide full manual control over scanning

### Home Assistant Automation Examples

```yaml
# Automatically scan when arriving home
- alias: "Scan devices when arriving home"
  trigger:
    - platform: state
      entity_id: device_tracker.person_phone
      to: 'home'
  action:
    - service: button.press
      entity_id: button.scan_all

# Scan specific device when motion detected
- alias: "Scan phone when motion detected"
  trigger:
    - platform: state
      entity_id: binary_sensor.motion_sensor
      to: 'on'
  action:
    - service: button.press
      entity_id: button.scan_AC_DF_A1_C3_80_E3
```

## Troubleshooting

### Common Issues

1. **Device not found**: Increase `scan_timeout` value
2. **MQTT connection failed**: Check broker credentials and network connectivity
3. **Permission denied**: Ensure proper file permissions on `config.json`
4. **Bluetooth errors**: Verify Bluetooth adapter is working and has BLE support

### Logs
The application provides detailed console output for debugging:
- Configuration loading status
- MQTT connection status
- Device scanning results
- Error messages

## Development

## License

This project is licensed under the terms specified in the LICENSE file.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Support

For support and questions, please open an issue in the project repository.
