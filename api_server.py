#!/usr/bin/env python3
"""
Comprehensive REST API server for controlling LED lights with full pattern support.
Provides endpoints for all light patterns, controls, and system management.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import argparse
import atexit
import os
from light_service import get_light_service
from state_manager import StateManager, AutoStateManager
from presets import PresetManager

app = Flask(__name__)
CORS(app)  # Enable CORS for web client access

# Global instances
light_service = None
state_manager = None
auto_state_manager = None
preset_manager = None


def initialize_services(use_lights=True, n_pixels=50, show_animation=False):
    """Initialize all services"""
    global light_service, state_manager, auto_state_manager, preset_manager
    
    # Initialize light service
    light_service = get_light_service(use_lights=use_lights, n_pixels=n_pixels, show_animation=show_animation)
    if not light_service.initialize():
        raise RuntimeError("Failed to initialize light service")
    
    # Initialize state management
    state_manager = StateManager()
    
    # Try to restore previous state
    if state_manager.state_exists():
        result = state_manager.apply_state_to_service(light_service)
        print(f"State restoration: {result.get('message', 'Unknown result')}")
    
    # Start automatic state saving
    auto_state_manager = AutoStateManager(light_service, state_manager)
    auto_state_manager.start()
    
    # Initialize preset management
    preset_manager = PresetManager()
    
    print("Light API services initialized successfully")


def shutdown_services():
    """Shutdown all services"""
    global auto_state_manager, light_service
    
    if auto_state_manager:
        auto_state_manager.force_save()  # Save final state
        auto_state_manager.stop()
    
    if light_service:
        light_service.shutdown()
    
    print("Light API services shut down")


# Register shutdown handler
atexit.register(shutdown_services)


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500


# Health and info endpoints
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'Light API is running',
        'service_running': light_service.is_running() if light_service else False
    })


@app.route('/api/info', methods=['GET'])
def get_info():
    """Get API information and capabilities"""
    return jsonify({
        'success': True,
        'api_version': '1.0.0',
        'description': 'All of the Lights REST API',
        'endpoints': {
            'patterns': '/api/patterns',
            'brightness': '/api/brightness',
            'saturation': '/api/saturation',
            'speed': '/api/speed',
            'tempo': '/api/tempo',
            'alt_mode': '/api/alt-mode',
            'mute': '/api/mute',
            'sync': '/api/sync',
            'status': '/api/status',
            'presets': '/api/presets'
        }
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current system status"""
    if not light_service:
        return jsonify({'success': False, 'message': 'Service not initialized'}), 500
    
    status = light_service.get_status()
    return jsonify({'success': True, 'status': status})


# Pattern control endpoints
@app.route('/api/patterns', methods=['GET'])
def get_patterns():
    """Get available light patterns"""
    if not light_service:
        return jsonify({'success': False, 'message': 'Service not initialized'}), 500
    
    return jsonify(light_service.get_available_patterns())


@app.route('/api/patterns/<pattern_name>', methods=['POST'])
def set_pattern(pattern_name):
    """Set the current light pattern"""
    if not light_service:
        return jsonify({'success': False, 'message': 'Service not initialized'}), 500
    
    result = light_service.set_pattern(pattern_name)
    status_code = 200 if result['success'] else 400
    
    # Log the pattern change for visibility
    if result['success']:
        print(f"🎨 Pattern changed to: {pattern_name}", flush=True)
        # Small delay to prevent race conditions with rapid successive calls
        import time
        time.sleep(0.05)
    else:
        print(f"❌ Failed to set pattern: {pattern_name}", flush=True)
    
    return jsonify(result), status_code


# Control endpoints
@app.route('/api/brightness', methods=['GET', 'POST'])
def brightness_control():
    """Get or set brightness level"""
    if not light_service:
        return jsonify({'success': False, 'message': 'Service not initialized'}), 500
    
    if request.method == 'GET':
        status = light_service.get_status()
        return jsonify({
            'success': True,
            'brightness': status.get('brightness', 0),
            'brightness_percent': int(status.get('brightness', 0) * 100)
        })
    
    # POST request
    data = request.get_json() or {}
    brightness = data.get('brightness', data.get('value'))
    
    if brightness is None:
        return jsonify({'success': False, 'message': 'brightness value required'}), 400
    
    try:
        result = light_service.set_brightness(float(brightness))
        if result['success']:
            print(f"💡 Brightness set to: {result['brightness_percent']}%", flush=True)
        return jsonify(result)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid brightness value'}), 400


@app.route('/api/saturation', methods=['GET', 'POST'])
def saturation_control():
    """Get or set color saturation"""
    if not light_service:
        return jsonify({'success': False, 'message': 'Service not initialized'}), 500
    
    if request.method == 'GET':
        status = light_service.get_status()
        return jsonify({
            'success': True,
            'saturation': status.get('saturation', 0),
            'saturation_percent': int(status.get('saturation', 0) * 100)
        })
    
    # POST request
    data = request.get_json() or {}
    saturation = data.get('saturation', data.get('value'))
    
    if saturation is None:
        return jsonify({'success': False, 'message': 'saturation value required'}), 400
    
    try:
        result = light_service.set_saturation(float(saturation))
        return jsonify(result)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid saturation value'}), 400


@app.route('/api/hue', methods=['GET', 'POST'])
def hue_control():
    """Get or set color hue"""
    if not light_service:
        return jsonify({'success': False, 'message': 'Service not initialized'}), 500
    
    if request.method == 'GET':
        status = light_service.get_status()
        return jsonify({
            'success': True,
            'hue': status.get('hue', 0),
            'hue_degrees': int(status.get('hue', 0))
        })
    
    # POST request
    data = request.get_json() or {}
    hue = data.get('hue', data.get('value'))
    
    if hue is None:
        return jsonify({'success': False, 'message': 'hue value required'}), 400
    
    try:
        result = light_service.set_hue(float(hue))
        return jsonify(result)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid hue value'}), 400


@app.route('/api/speed', methods=['GET', 'POST'])
def speed_control():
    """Get or set animation speed"""
    if not light_service:
        return jsonify({'success': False, 'message': 'Service not initialized'}), 500
    
    if request.method == 'GET':
        status = light_service.get_status()
        return jsonify({
            'success': True,
            'speed_factor': status.get('speed_factor', 1.0)
        })
    
    # POST request
    data = request.get_json() or {}
    speed = data.get('speed', data.get('speed_factor', data.get('value')))
    
    if speed is None:
        return jsonify({'success': False, 'message': 'speed value required'}), 400
    
    try:
        result = light_service.set_speed(float(speed))
        return jsonify(result)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid speed value'}), 400


@app.route('/api/tempo', methods=['GET', 'POST'])
def tempo_control():
    """Get or set tempo in BPM"""
    if not light_service:
        return jsonify({'success': False, 'message': 'Service not initialized'}), 500
    
    if request.method == 'GET':
        status = light_service.get_status()
        return jsonify({
            'success': True,
            'tempo': status.get('tempo', 60)
        })
    
    # POST request
    data = request.get_json() or {}
    tempo = data.get('tempo', data.get('bpm', data.get('value')))
    
    if tempo is None:
        return jsonify({'success': False, 'message': 'tempo value required'}), 400
    
    try:
        result = light_service.set_tempo(int(tempo))
        return jsonify(result)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid tempo value'}), 400


@app.route('/api/alt-mode', methods=['GET', 'POST'])
def alt_mode_control():
    """Get or toggle alternate mode"""
    if not light_service:
        return jsonify({'success': False, 'message': 'Service not initialized'}), 500
    
    if request.method == 'GET':
        status = light_service.get_status()
        return jsonify({
            'success': True,
            'alt_mode': status.get('alt_mode', False)
        })
    
    # POST request - toggle alt mode
    result = light_service.toggle_alt_mode()
    return jsonify(result)


@app.route('/api/mute', methods=['GET', 'POST', 'DELETE'])
def mute_control():
    """Get mute status, enable mute, or disable mute"""
    if not light_service:
        return jsonify({'success': False, 'message': 'Service not initialized'}), 500
    
    if request.method == 'GET':
        status = light_service.get_status()
        mute_types = light_service.get_available_mute_types()
        return jsonify({
            'success': True,
            'mute': status.get('mute', False),
            'mute_type': status.get('mute_type', 'instant'),
            'available_types': mute_types['mute_types']
        })
    
    elif request.method == 'POST':
        # Enable mute
        data = request.get_json() or {}
        mute_type = data.get('type', data.get('mute_type', 'instant'))
        
        result = light_service.set_mute(True, mute_type)
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
    
    elif request.method == 'DELETE':
        # Disable mute
        result = light_service.set_mute(False)
        return jsonify(result)


@app.route('/api/sync', methods=['POST'])
def sync_phase():
    """Synchronize animation phase"""
    if not light_service:
        return jsonify({'success': False, 'message': 'Service not initialized'}), 500
    
    result = light_service.sync_phase()
    return jsonify(result)


# State management endpoints
@app.route('/api/state/save', methods=['POST'])
def save_state():
    """Manually save current state"""
    if not light_service or not state_manager:
        return jsonify({'success': False, 'message': 'Services not initialized'}), 500
    
    status = light_service.get_status()
    success = state_manager.save_state(status, {'manual_save': True})
    
    if success:
        return jsonify({'success': True, 'message': 'State saved successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to save state'}), 500


@app.route('/api/state/restore', methods=['POST'])
def restore_state():
    """Restore saved state"""
    if not light_service or not state_manager:
        return jsonify({'success': False, 'message': 'Services not initialized'}), 500
    
    result = state_manager.apply_state_to_service(light_service)
    status_code = 200 if result['success'] else 500
    return jsonify(result), status_code


@app.route('/api/state/reset', methods=['POST'])
def reset_to_default():
    """Reset to default state"""
    if not light_service or not state_manager:
        return jsonify({'success': False, 'message': 'Services not initialized'}), 500
    
    default_state = state_manager.create_default_state()
    result = state_manager.apply_state_to_service(light_service, default_state)
    status_code = 200 if result['success'] else 500
    return jsonify(result), status_code


# Preset management endpoints
@app.route('/api/presets', methods=['GET'])
def list_presets():
    """Get all available presets"""
    if not preset_manager:
        return jsonify({'success': False, 'message': 'Preset manager not initialized'}), 500
    
    result = preset_manager.list_presets()
    return jsonify(result)


@app.route('/api/presets', methods=['POST'])
def create_preset():
    """Create a new preset from current state"""
    if not light_service or not preset_manager:
        return jsonify({'success': False, 'message': 'Services not initialized'}), 500
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Request body required'}), 400
    
    preset_id = data.get('id')
    name = data.get('name')
    description = data.get('description', '')
    metadata = data.get('metadata', {})
    
    if not preset_id or not name:
        return jsonify({'success': False, 'message': 'id and name are required'}), 400
    
    result = preset_manager.save_preset(preset_id, name, description, light_service, metadata)
    status_code = 200 if result['success'] else 400
    return jsonify(result), status_code


@app.route('/api/presets/<preset_id>', methods=['GET'])
def get_preset(preset_id):
    """Get a specific preset"""
    if not preset_manager:
        return jsonify({'success': False, 'message': 'Preset manager not initialized'}), 500
    
    result = preset_manager.get_preset(preset_id)
    status_code = 200 if result['success'] else 404
    return jsonify(result), status_code


@app.route('/api/presets/<preset_id>', methods=['POST'])
def apply_preset(preset_id):
    """Apply a preset to the lights"""
    if not light_service or not preset_manager:
        return jsonify({'success': False, 'message': 'Services not initialized'}), 500
    
    result = preset_manager.load_preset(preset_id, light_service)
    status_code = 200 if result['success'] else 400
    
    if result['success']:
        preset_name = result.get('preset_data', {}).get('name', preset_id)
        print(f"🎭 Applied preset: {preset_name}")
    
    return jsonify(result), status_code


@app.route('/api/presets/<preset_id>', methods=['PUT'])
def update_preset(preset_id):
    """Update an existing preset"""
    if not preset_manager:
        return jsonify({'success': False, 'message': 'Preset manager not initialized'}), 500
    
    data = request.get_json() or {}
    name = data.get('name')
    description = data.get('description')
    metadata = data.get('metadata')
    update_from_current = data.get('update_from_current', False)
    
    light_service_param = light_service if update_from_current else None
    
    result = preset_manager.update_preset(preset_id, name, description, light_service_param, metadata)
    status_code = 200 if result['success'] else 404
    return jsonify(result), status_code


@app.route('/api/presets/<preset_id>', methods=['DELETE'])
def delete_preset(preset_id):
    """Delete a preset"""
    if not preset_manager:
        return jsonify({'success': False, 'message': 'Preset manager not initialized'}), 500
    
    result = preset_manager.delete_preset(preset_id)
    status_code = 200 if result['success'] else 404
    return jsonify(result), status_code


# Convenience endpoints for Siri/HomeKit integration
@app.route('/api/lights/on', methods=['POST'])
def lights_on():
    """Turn lights on with warm white (convenience endpoint)"""
    if not light_service:
        return jsonify({'success': False, 'message': 'Service not initialized'}), 500
    
    # Set all properties atomically to prevent flashing
    result = light_service.set_all_at_once(
        pattern='solid',
        brightness=0.8,      # 80% brightness - comfortable default  
        saturation=0.05,     # Very low saturation = warm white
        hue=30,              # Warm orange/amber hue
        mute=False           # Make sure lights are on
    )
    
    return jsonify({
        'success': result['success'],
        'message': 'Warm white lights turned on (atomic operation)',
        'details': result
    })


@app.route('/api/lights/off', methods=['POST'])
def lights_off():
    """Turn lights off (convenience endpoint)"""
    if not light_service:
        return jsonify({'success': False, 'message': 'Service not initialized'}), 500
    
    result = light_service.set_mute(True, 'instant')
    return jsonify({
        'success': result['success'],
        'message': 'Lights turned off',
        'details': result
    })


@app.route('/api/party-mode', methods=['POST'])
def party_mode():
    """Activate party mode (convenience endpoint)"""
    if not light_service:
        return jsonify({'success': False, 'message': 'Service not initialized'}), 500
    
    # Party mode: sparks pattern, high brightness, faster speed, colorful
    results = []
    results.append(light_service.set_pattern('sparks'))
    results.append(light_service.set_brightness(1.0))
    results.append(light_service.set_saturation(0.8))
    results.append(light_service.set_speed(2.0))
    results.append(light_service.set_mute(False))
    
    success = all(r['success'] for r in results)
    return jsonify({
        'success': success,
        'message': 'Party mode activated!',
        'details': results
    })


@app.route('/api/ambient-mode', methods=['POST'])
def ambient_mode():
    """Activate ambient mode (convenience endpoint)"""
    if not light_service:
        return jsonify({'success': False, 'message': 'Service not initialized'}), 500
    
    # Ambient mode: pulse pattern, low brightness, slow speed, low saturation
    results = []
    results.append(light_service.set_pattern('pulse'))
    results.append(light_service.set_brightness(0.3))
    results.append(light_service.set_saturation(0.2))
    results.append(light_service.set_speed(0.5))
    results.append(light_service.set_mute(False))
    
    success = all(r['success'] for r in results)
    return jsonify({
        'success': success,
        'message': 'Ambient mode activated',
        'details': results
    })


# Additional HomeKit/Siri-friendly endpoints
@app.route('/api/reading-mode', methods=['POST'])
def reading_mode():
    """Activate reading mode - soft, warm lighting (convenience endpoint)"""
    if not light_service:
        return jsonify({'success': False, 'message': 'Service not initialized'}), 500
    
    results = []
    results.append(light_service.set_pattern('pulse'))
    results.append(light_service.set_brightness(0.6))
    results.append(light_service.set_saturation(0.1))  # Very low saturation for warm white
    results.append(light_service.set_speed(0.3))       # Very slow
    results.append(light_service.set_mute(False))
    
    success = all(r['success'] for r in results)
    return jsonify({
        'success': success,
        'message': 'Reading mode activated',
        'details': results
    })


@app.route('/api/movie-mode', methods=['POST']) 
def movie_mode():
    """Activate movie mode - dim ambient lighting (convenience endpoint)"""
    if not light_service:
        return jsonify({'success': False, 'message': 'Service not initialized'}), 500
    
    results = []
    results.append(light_service.set_pattern('pulse'))
    results.append(light_service.set_brightness(0.15))  # Very dim
    results.append(light_service.set_saturation(0.4))
    results.append(light_service.set_speed(0.2))        # Very slow pulse
    results.append(light_service.set_mute(False))
    
    success = all(r['success'] for r in results)
    return jsonify({
        'success': success,
        'message': 'Movie mode activated',
        'details': results
    })


@app.route('/api/energize-mode', methods=['POST'])
def energize_mode():
    """Activate energize mode - bright, dynamic lighting (convenience endpoint)"""
    if not light_service:
        return jsonify({'success': False, 'message': 'Service not initialized'}), 500
    
    results = []
    results.append(light_service.set_pattern('pixel_train'))
    results.append(light_service.set_brightness(0.9))
    results.append(light_service.set_saturation(0.7))
    results.append(light_service.set_speed(1.5))
    results.append(light_service.set_mute(False))
    
    success = all(r['success'] for r in results)
    return jsonify({
        'success': success,
        'message': 'Energize mode activated!',
        'details': results
    })


@app.route('/api/sleep-mode', methods=['POST'])
def sleep_mode():
    """Activate sleep mode - very dim, slow fade (convenience endpoint)"""
    if not light_service:
        return jsonify({'success': False, 'message': 'Service not initialized'}), 500
    
    results = []
    results.append(light_service.set_pattern('pulse'))
    results.append(light_service.set_brightness(0.05))  # Extremely dim
    results.append(light_service.set_saturation(0.05))  # Almost white
    results.append(light_service.set_speed(0.1))        # Very slow fade
    results.append(light_service.set_mute(False))
    
    success = all(r['success'] for r in results)
    return jsonify({
        'success': success,
        'message': 'Sleep mode activated',
        'details': results
    })


if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='All of the Lights API Server')
    parser.add_argument('--no-lights', action='store_true', 
                       help='Run in simulation mode without actual lights')
    parser.add_argument('--show-animation', action='store_true',
                       help='Show pygame animation window (works with --no-lights)')
    parser.add_argument('--pixels', type=int, default=50,
                       help='Number of pixels in simulation mode')
    parser.add_argument('--host', default='0.0.0.0',
                       help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000,
                       help='Port to bind to')
    parser.add_argument('--debug', action='store_true',
                       help='Run in debug mode')
    
    args = parser.parse_args()
    
    # Initialize services
    try:
        initialize_services(use_lights=not args.no_lights, n_pixels=args.pixels, show_animation=args.show_animation)
        
        print(f"Starting Light API Server...")
        mode_str = 'Simulation'
        if not args.no_lights:
            mode_str = 'Hardware'
        elif args.show_animation:
            mode_str = 'Simulation with Animation'
        else:
            mode_str = 'Simulation (Headless)'
        
        print(f"Mode: {mode_str}")
        print(f"Pixels: {args.pixels}")
        print(f"Server: http://{args.host}:{args.port}")
        
        if args.show_animation:
            print("🎨 Pygame window will show light patterns")
        print("📡 REST API ready for control")
        print("Available endpoints:")
        print("  GET  /api/health       - Health check")
        print("  GET  /api/info         - API information") 
        print("  GET  /api/status       - Current status")
        print("  GET  /api/patterns     - Available patterns")
        print("  POST /api/patterns/<name> - Set pattern")
        print("  GET/POST /api/brightness  - Control brightness")
        print("  GET/POST /api/saturation  - Control saturation")
        print("  GET/POST /api/speed       - Control speed")
        print("  GET/POST /api/tempo       - Control tempo")
        print("  GET/POST /api/alt-mode    - Control alt mode")
        print("  GET/POST/DELETE /api/mute - Control mute")
        print("  POST /api/sync            - Sync phase")
        print("  POST /api/lights/on       - Turn lights on")
        print("  POST /api/lights/off      - Turn lights off")
        print("  POST /api/party-mode      - Party mode")
        print("  POST /api/ambient-mode    - Ambient mode")
        print("  POST /api/reading-mode    - Reading mode")
        print("  POST /api/movie-mode      - Movie mode")
        print("  POST /api/energize-mode   - Energize mode")
        print("  POST /api/sleep-mode      - Sleep mode")
        print("  GET  /api/presets         - List all presets")
        print("  POST /api/presets         - Create new preset")
        print("  GET  /api/presets/<id>    - Get specific preset")
        print("  POST /api/presets/<id>    - Apply preset")
        print("  PUT  /api/presets/<id>    - Update preset")
        print("  DELETE /api/presets/<id>  - Delete preset")
        print("")
        
        # Run the Flask server
        app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)
        
    except Exception as e:
        print(f"Failed to start server: {e}")
        exit(1)