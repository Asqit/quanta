# Quanta

A Pomodoro timer built with MicroPython for ESP32 microcontrollers, featuring an OLED display, physical buttons, and web-based configuration.

## Features

- **Physical Interface**: OLED display (128x64) with two buttons for control
- **Audio Feedback**: Buzzer with different sounds for various events
- **Web Configuration**: HTTP server for remote settings management
- **Flexible Timing**: Customizable work/break durations
- **Auto-start Options**: Configurable automatic session transitions
- **Progress Tracking**: Visual progress bars and session counters

## Hardware Requirements

- ESP32 microcontroller
- SSD1306 OLED display (I2C)
- 2 push buttons (start/pause and reset)
- Buzzer/speaker
- Breadboard and jumper wires

## Pin Configuration

- **OLED Display**: SDA (Pin 21), SCL (Pin 22)
- **Start/Pause Button**: Pin 4 (with pull-up)
- **Reset Button**: Pin 2 (with pull-up)
- **Buzzer**: Pin 15 (PWM)

## Usage

1. **Start Timer**: Press start button from idle state
2. **Pause/Resume**: Press start button during active session
3. **Reset**: Press reset button to return to idle
4. **Web Config**: Connect to "pomodoro-esp32" WiFi network and send HTTP requests

## Configuration

Settings can be modified via HTTP POST to the device:

```json
{
  "timing": {
    "work": 25,
    "short_break": 5,
    "long_break": 15
  },
  "behavior": {
    "auto_start_breaks": false,
    "auto_start_work": false
  },
  "settings": {
    "sounds": true
  }
}
```
