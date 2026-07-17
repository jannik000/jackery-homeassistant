> **Known issue:** Some Jackery account variants or regions may expose a different device model set than expected.

# Jackery Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

This is a vibe-code adaptation of https://github.com/theak/jackery-homeassistant, changing the backend from the original implementation to socketry from https://github.com/jlopez/socketry. The goal was simple: not only read values from a Jackery power station, but also control it from Home Assistant.

The integration exposes monitoring entities as well as controllable entities where the device supports them, including AC/DC switching and configuration options.

## Features

- 🔋 **Battery and power monitoring** for charge level, input/output power, temperatures, and runtime estimates
- 🔌 **Output and input control** through switches for AC/DC/USB/car outputs and input modes
- ⚙️ **Configuration-style controls** for light mode, charge speed, battery protection, auto shutdown, energy saving, and screen timeout
- 🧭 **Diagnostics and status entities** such as battery state, error codes, and system status

## Supported entities

### Sensors

| Entity | Description | Unit |
| ------ | ----------- | ---- |
| Battery | Remaining battery percentage | % |
| Battery temperature | Device temperature reading | °C |
| Battery state | Idle / charging / discharging | - |
| Input power | Current input power | W |
| Output power | Current output power | W |
| Time to full | Estimated time to full charge | h |
| Time remaining | Estimated runtime remaining | h |
| AC input power | AC-side input power | W |
| Car input power | Car-input power | W |
| AC voltage | AC output voltage | V |
| AC frequency | AC output frequency | Hz |
| AC power | AC power reading | W |
| AC power (secondary) | Secondary AC power reading | W |
| AC socket power | AC socket power reading | W |
| Error code | Diagnostic error code | - |
| Power mode battery | Battery-related power mode info | - |
| Total temperature | Additional temperature reading | °C |
| System status | Diagnostic system status | - |

### Binary sensors

| Entity | Description |
| ------ | ----------- |
| Wireless charging | Indicates wireless charging state |
| Temperature alarm | Indicates a temperature alarm |
| Power alarm | Indicates a power alarm |

### Switches

| Entity | Description |
| ------ | ----------- |
| AC output | Toggle AC output |
| DC output | Toggle DC output |
| USB output | Toggle USB output |
| Car output | Toggle car output |
| AC input | Toggle AC input |
| DC input | Toggle DC input |
| Super fast charge | Toggle super fast charge |
| UPS mode | Toggle UPS mode |

### Selects

| Entity | Description |
| ------ | ----------- |
| Light mode | Select light mode |
| Charge speed | Select charge speed |
| Battery protection | Select battery protection |

### Numbers

| Entity | Description |
| ------ | ----------- |
| Auto shutdown | Set auto shutdown time |
| Energy saving | Set energy saving time |
| Screen timeout | Set screen timeout |

> Note: The exact set of entities available depends on the Jackery device model and what the backend exposes for that device.

## Installation

### Option 1: HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Add this repository as a custom repository in HACS
3. Search for "Jackery" in the integrations section
4. Click "Download" and restart Home Assistant

### Option 2: Manual Installation

1. Download or clone this repository
2. Copy the `jackery` folder to your `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Jackery" and select it
4. Enter your Jackery account credentials:
   - **Username**: Your Jackery account email/username
   - **Password**: Your Jackery account password
5. Click **Submit**

The integration will automatically discover your Jackery devices and create sensors for each one.

## Usage

Once configured, you'll find your Jackery devices and their sensors in:

- **Settings** → **Devices & Services** → **Entities**
- Each device will have its own set of sensors

You can use these sensors in:

- **Dashboards**: Create custom dashboards to monitor your power station
- **Automations**: Set up automations based on battery level, power status, etc.
- **Templates**: Use sensor values in templates for custom calculations

### Example Automations

```yaml
# Low battery alert
automation:
  - alias: "Low Battery Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.jackery_device_remaining_battery
      below: 20
    action:
      - service: notify.mobile_app
        data:
          message: "Jackery battery is low: {{ states('sensor.jackery_device_remaining_battery') }}%"

  # AC output turned on notification
  - alias: "Jackery AC Output On"
    trigger:
      platform: state
      entity_id: binary_sensor.jackery_device_ac_output
      to: "on"
    action:
      - service: notify.mobile_app
        data:
          message: "Jackery AC output has been turned on"
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify your Jackery account credentials
   - Ensure your account is active and not locked

2. **No Devices Found**
   - Make sure your Jackery device is connected to the internet
   - Verify the device is registered to your account

3. **Sensors Not Updating**
   - Check the Home Assistant logs for errors
   - Verify your device has internet connectivity

### Logs

To enable debug logging, add this to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.jackery: debug
```

## Requirements

- Home Assistant 2023.8.0 or newer
- Python 3.10 or newer

## Dependencies

- `socketry>=0.2.4`

## Contributing

Pull Requests are encouraged and welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Based heavily on code from https://qiita.com/Hsky16/items/c163137265a87186ac39
- Thanks to the Home Assistant community for the excellent framework
- Special thanks to all contributors and users who provide feedback

---

**Note**: This is a community-driven integration and is not officially affiliated with Jackery. Use at your own risk.
