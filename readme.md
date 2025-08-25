# All of the Lights

A comprehensive LED light control system for WS2801 strips with both interactive console control and REST API remote access. Perfect for home automation, music synchronization, and integration with voice assistants like Siri.

![The command light console](https://raw.githubusercontent.com/randomsgs/all_of_the_lights/master/media/controller.png)

## Features

### Interactive Control
* **Real-time control** of light patterns via keyboard
* **Tap tempo syncing** for music synchronization  
* **5 different light patterns** each with alternate modes:
  - **Pulse**: Synchronized pulsing across all lights
  - **Pixel Train**: Moving train of colored pixels
  - **Droplets**: Water droplet-like expanding effects
  - **Orbits**: Two colored lights orbiting the strip
  - **Sparks**: Random sparkling effects
* **Dynamic controls**: brightness, saturation, speed, tempo
* **Mute functions**: instant, gradual fade, or flicker effects

### REST API Control
* **Full remote control** via HTTP endpoints
* **Scene modes**: party, ambient, reading, movie, energize, sleep
* **State persistence**: settings automatically saved and restored
* **Voice assistant ready**: simple endpoints for Siri/HomeKit integration
* **Thread-safe**: handles multiple concurrent requests
* **CORS enabled**: works with web applications

### Home Assistant Integration
* **HomeKit bridge** for native Siri voice control
* **Apple Home app** integration with brightness controls
* **Advanced automations**: time-based, sensor-based triggers
* **Scene management**: save and recall custom configurations
* **Multi-assistant support**: works with Siri, Google Assistant, Alexa

### Hardware Support
* **WS2801 LED strips** on Raspberry Pi
* **Simulation mode** for development without hardware
* **Headless operation** for server deployment

## Quick Start

### Installation

```bash
git clone <repository-url>
cd all_of_the_lights
pip install -r requirements.txt
```

### Interactive Mode (Original)

```bash
# With actual LED hardware
python main.py

# Simulation mode (pygame window)
python main.py --no_lights
```

### REST API Server (New)

```bash
# Start API server with LED hardware
python api_server.py

# Start API server in simulation mode
python api_server.py --no-lights

# Custom port (default is 5000)
python api_server.py --no-lights --port 8000
```

## Hardware Setup

Wire your LED lights according to the diagram in this [blog by AndyPi](https://andypi.co.uk/2014/12/27/raspberry-pi-controlled-ws2801-rgb-leds/)

## Usage

### Interactive Controls (Console Mode)

| Key | Action |
|-----|--------|
| **space** | Tap tempo |
| **↑ ↓** | Double/half speed |
| **c** | Sync phase |
| **a/s/d/f/g** | Select pattern (pulse/pixel_train/droplets/orbits/sparks) |
| **← →** | Adjust brightness |
| **+ -** | Adjust saturation |
| **b** | Toggle alternate mode |
| **q/w/e** | Select mute type (instant/gradual/flicker) |
| **enter** | Toggle mute |

### REST API Usage

#### Basic Control
```bash
# Health check
curl http://localhost:5000/api/health

# Get current status
curl http://localhost:5000/api/status

# Set pattern to sparks
curl -X POST http://localhost:5000/api/patterns/sparks

# Set brightness to 50%
curl -X POST http://localhost:5000/api/brightness \
  -H "Content-Type: application/json" \
  -d '{"brightness": 0.5}'

# Set tempo to 120 BPM
curl -X POST http://localhost:5000/api/tempo \
  -H "Content-Type: application/json" \
  -d '{"tempo": 120}'
```

#### Scene Modes
```bash
# Simple commands perfect for voice assistants
curl -X POST http://localhost:5000/api/lights/on
curl -X POST http://localhost:5000/api/lights/off
curl -X POST http://localhost:5000/api/party-mode
curl -X POST http://localhost:5000/api/ambient-mode
curl -X POST http://localhost:5000/api/reading-mode
curl -X POST http://localhost:5000/api/movie-mode
curl -X POST http://localhost:5000/api/energize-mode
curl -X POST http://localhost:5000/api/sleep-mode
```

#### Available API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/status` | Current system status |
| GET | `/api/patterns` | List available patterns |
| POST | `/api/patterns/<name>` | Set light pattern |
| GET/POST | `/api/brightness` | Control brightness (0-1 or 0-100%) |
| GET/POST | `/api/saturation` | Control saturation (0-1 or 0-100%) |
| GET/POST | `/api/speed` | Control speed multiplier |
| GET/POST | `/api/tempo` | Control tempo (BPM) |
| GET/POST | `/api/alt-mode` | Control alternate mode |
| GET/POST/DELETE | `/api/mute` | Control mute functions |
| POST | `/api/sync` | Synchronize phase |
| GET | `/api/presets` | List all presets |
| POST | `/api/presets` | Create new preset |
| GET/POST/PUT/DELETE | `/api/presets/<id>` | Manage specific preset |
| POST | `/api/lights/on` | Turn lights on (convenience) |
| POST | `/api/lights/off` | Turn lights off (convenience) |
| POST | `/api/party-mode` | Activate party mode |
| POST | `/api/ambient-mode` | Activate ambient mode |
| POST | `/api/reading-mode` | Activate reading mode |
| POST | `/api/movie-mode` | Activate movie mode |
| POST | `/api/energize-mode` | Activate energize mode |
| POST | `/api/sleep-mode` | Activate sleep mode |

## Home Assistant Integration

For complete Home Assistant setup with Siri voice control, see [HOME_ASSISTANT_SETUP.md](HOME_ASSISTANT_SETUP.md).

### Quick Setup Summary:

1. **Install Home Assistant** (Docker recommended)
2. **Configure REST commands** pointing to your lights API
3. **Set up HomeKit bridge** with proper network configuration
4. **Pair with Apple Home** using QR code
5. **Enjoy Siri control**: "Hey Siri, turn on LED Strip"

### Example Voice Commands:
- "Hey Siri, turn on LED Strip"
- "Hey Siri, set LED Strip to 50%"  
- "Hey Siri, turn off LED Strip"

### Home Assistant Benefits:
- **Multiple voice assistants**: Siri, Google Assistant, Alexa
- **Advanced automations**: sunrise/sunset, presence detection
- **Beautiful interface**: mobile app and web dashboard
- **Integration hub**: connect with other smart home devices

## Code Architecture

### Core Components

```
all_of_the_lights/
├── api_server.py          # REST API server
├── headless_controller.py # Light controller without UI  
├── light_service.py       # Thread-safe API wrapper
├── state_manager.py       # State persistence
├── presets.py            # Preset management
├── patterns.py           # Light pattern implementations
├── colors.py             # Color utilities
├── phase.py              # Timing and phase calculations
├── mute.py               # Mute effect functions
├── pixels.py             # Hardware interface
└── constants.py          # Configuration constants
```

### Key Classes

- **`HeadlessController`**: Core light pattern engine that runs without UI
- **`APILightService`**: Thread-safe wrapper providing API methods
- **`StateManager`**: Handles automatic saving/restoring of settings
- **`PresetManager`**: Manages custom lighting configurations
- **Pattern Functions**: Individual algorithms (pulse, sparks, etc.) in `patterns.py`

### Threading Model

The system uses a multi-threaded approach:
- **Main Thread**: Flask API server handling HTTP requests
- **Light Thread**: Continuous pattern processing at 60 FPS
- **Auto-save Thread**: Periodic state persistence
- **Thread Safety**: RLock synchronization for shared state

## Integration Examples

### Siri Shortcuts (Direct)
Create iOS shortcuts that make HTTP requests to your API endpoints:
- "Turn on party lights" → `POST /api/party-mode`
- "Set lights to 25%" → `POST /api/brightness {"brightness": 0.25}`
- "Turn off lights" → `POST /api/lights/off`

### Home Assistant (Recommended)
```yaml
rest_command:
  lights_party_mode:
    url: "http://your-pi:5000/api/party-mode"
    method: POST
  
  lights_brightness:
    url: "http://your-pi:5000/api/brightness"
    method: POST
    payload: '{"brightness": {{ brightness }}}'
```

### Node-RED Integration
Use HTTP request nodes to control lights based on:
- Time of day schedules
- Music beat detection
- Home automation triggers
- Voice commands

## Deployment to Raspberry Pi

1. **Copy files** to your Raspberry Pi
2. **Install dependencies**: `pip install -r requirements.txt`  
3. **Start server**: `python api_server.py`
4. **Configure Home Assistant** to use Pi's IP address
5. **Set up HomeKit integration** for Siri voice control
6. **Enjoy automated lighting** with voice commands and schedules!

## Development

### Adding New Patterns
1. Create pattern function in `patterns.py`:
```python
def my_pattern(phase, cache, kwargs):
    # Your pattern algorithm here
    return rgb_values, cache
```

2. Add to pattern map in `constants.py`
3. Pattern automatically available via API

### Custom API Endpoints
Add new endpoints to `api_server.py`:
```python
@app.route('/api/my-endpoint', methods=['POST'])
def my_endpoint():
    # Your custom functionality
    return jsonify({'success': True})
```

## Troubleshooting

### Common Issues
- **Port 5000 in use**: Try `--port 8000` or disable macOS AirPlay Receiver
- **HomeKit "Accessory Not Found"**: Use host networking and `advertise_ip` in config
- **Permission errors**: Run with appropriate permissions for GPIO access
- **Import errors**: Ensure all dependencies installed with `pip install -r requirements.txt`

### Performance Tips
- Use headless mode (`--no-lights`) for production servers
- Adjust FPS in HeadlessController if experiencing performance issues
- Monitor CPU usage - patterns are computationally intensive

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Test both interactive and API modes
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is open source. Please check the license file for details.