""" Preset management for saving and loading custom light configurations """

import json
import os
import threading
import time
from pathlib import Path
from state_manager import StateManager


class PresetManager:
    """ Manages saving, loading, and organizing light presets """
    
    DEFAULT_PRESETS_DIR = os.path.expanduser("~/.all_of_the_lights/presets")
    
    def __init__(self, presets_dir=None):
        self.presets_dir = Path(presets_dir) if presets_dir else Path(self.DEFAULT_PRESETS_DIR)
        self._lock = threading.RLock()
        
        # Ensure presets directory exists
        self.presets_dir.mkdir(parents=True, exist_ok=True)
        
        # Create default presets if they don't exist
        self._create_default_presets()
    
    def _create_default_presets(self):
        """Create default preset configurations if they don't exist"""
        default_presets = {
            'party': {
                'name': 'Party Mode',
                'description': 'High energy sparks pattern for parties',
                'config': {
                    'pattern': 'sparks',
                    'brightness': 1.0,
                    'saturation': 0.8,
                    'speed_factor': 2.0,
                    'tempo': 120,
                    'alt_mode': True,
                    'mute': False,
                    'mute_type': 'instant'
                }
            },
            'ambient': {
                'name': 'Ambient Mode',
                'description': 'Soft pulsing for ambient lighting',
                'config': {
                    'pattern': 'pulse',
                    'brightness': 0.3,
                    'saturation': 0.2,
                    'speed_factor': 0.5,
                    'tempo': 60,
                    'alt_mode': False,
                    'mute': False,
                    'mute_type': 'gradual'
                }
            },
            'chill': {
                'name': 'Chill Mode',
                'description': 'Slow moving droplets for relaxation',
                'config': {
                    'pattern': 'droplets',
                    'brightness': 0.6,
                    'saturation': 0.4,
                    'speed_factor': 0.75,
                    'tempo': 45,
                    'alt_mode': True,
                    'mute': False,
                    'mute_type': 'gradual'
                }
            },
            'energetic': {
                'name': 'Energetic Mode',
                'description': 'Fast-moving pixel train with high energy',
                'config': {
                    'pattern': 'pixel_train',
                    'brightness': 0.9,
                    'saturation': 0.9,
                    'speed_factor': 1.5,
                    'tempo': 140,
                    'alt_mode': False,
                    'mute': False,
                    'mute_type': 'instant'
                }
            },
            'meditation': {
                'name': 'Meditation Mode',
                'description': 'Very slow, gentle orbiting lights',
                'config': {
                    'pattern': 'orbits',
                    'brightness': 0.4,
                    'saturation': 0.1,
                    'speed_factor': 0.25,
                    'tempo': 30,
                    'alt_mode': True,
                    'mute': False,
                    'mute_type': 'gradual'
                }
            }
        }
        
        for preset_id, preset_data in default_presets.items():
            preset_path = self.presets_dir / f"{preset_id}.json"
            if not preset_path.exists():
                self._save_preset_file(preset_path, preset_data)
    
    def _save_preset_file(self, preset_path, preset_data):
        """Save preset data to file"""
        try:
            preset_data['created_at'] = time.time()
            preset_data['updated_at'] = time.time()
            
            with open(preset_path, 'w') as f:
                json.dump(preset_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving preset file {preset_path}: {e}")
            return False
    
    def _load_preset_file(self, preset_path):
        """Load preset data from file"""
        try:
            with open(preset_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading preset file {preset_path}: {e}")
            return None
    
    def save_preset(self, preset_id, name, description, light_service, metadata=None):
        """Save current light state as a preset
        
        Args:
            preset_id (str): Unique identifier for the preset
            name (str): Display name for the preset
            description (str): Description of the preset
            light_service: APILightService instance to get current state from
            metadata (dict, optional): Additional metadata
            
        Returns:
            dict: Result of the save operation
        """
        try:
            with self._lock:
                # Get current light service status
                status = light_service.get_status()
                
                # Extract relevant configuration
                config = {
                    'pattern': status.get('pattern', 'pulse'),
                    'brightness': status.get('brightness', 1.0),
                    'saturation': status.get('saturation', 0.0),
                    'speed_factor': status.get('speed_factor', 1.0),
                    'tempo': status.get('tempo', 60),
                    'alt_mode': status.get('alt_mode', True),
                    'mute': status.get('mute', False),
                    'mute_type': status.get('mute_type', 'instant')
                }
                
                # Create preset data structure
                preset_data = {
                    'name': name,
                    'description': description,
                    'config': config,
                    'metadata': metadata or {},
                    'created_at': time.time(),
                    'updated_at': time.time()
                }
                
                # Save to file
                preset_path = self.presets_dir / f"{preset_id}.json"
                success = self._save_preset_file(preset_path, preset_data)
                
                if success:
                    return {
                        'success': True,
                        'message': f'Preset "{name}" saved successfully',
                        'preset_id': preset_id,
                        'preset_data': preset_data
                    }
                else:
                    return {
                        'success': False,
                        'message': f'Failed to save preset "{name}"'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'message': f'Error saving preset: {e}'
            }
    
    def load_preset(self, preset_id, light_service):
        """Load and apply a preset to the light service
        
        Args:
            preset_id (str): Identifier of the preset to load
            light_service: APILightService instance to apply preset to
            
        Returns:
            dict: Result of the load operation
        """
        try:
            with self._lock:
                preset_path = self.presets_dir / f"{preset_id}.json"
                
                if not preset_path.exists():
                    return {
                        'success': False,
                        'message': f'Preset "{preset_id}" not found'
                    }
                
                preset_data = self._load_preset_file(preset_path)
                if not preset_data:
                    return {
                        'success': False,
                        'message': f'Failed to load preset "{preset_id}"'
                    }
                
                config = preset_data.get('config', {})
                
                # Apply configuration to light service
                results = []
                
                if 'pattern' in config:
                    result = light_service.set_pattern(config['pattern'])
                    results.append(('pattern', result))
                
                if 'brightness' in config:
                    result = light_service.set_brightness(config['brightness'])
                    results.append(('brightness', result))
                
                if 'saturation' in config:
                    result = light_service.set_saturation(config['saturation'])
                    results.append(('saturation', result))
                
                if 'speed_factor' in config:
                    result = light_service.set_speed(config['speed_factor'])
                    results.append(('speed_factor', result))
                
                if 'tempo' in config:
                    result = light_service.set_tempo(config['tempo'])
                    results.append(('tempo', result))
                
                if 'alt_mode' in config:
                    # Only toggle if current state differs from desired state
                    current_status = light_service.get_status()
                    if current_status.get('alt_mode') != config['alt_mode']:
                        result = light_service.toggle_alt_mode()
                        results.append(('alt_mode', result))
                
                if 'mute' in config and 'mute_type' in config:
                    result = light_service.set_mute(config['mute'], config['mute_type'])
                    results.append(('mute', result))
                
                # Count successful applications
                successful = sum(1 for _, result in results if result.get('success', False))
                total = len(results)
                
                return {
                    'success': successful > 0,
                    'message': f'Preset "{preset_data.get("name", preset_id)}" applied ({successful}/{total} settings)',
                    'preset_data': preset_data,
                    'results': results
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error loading preset: {e}'
            }
    
    def get_preset(self, preset_id):
        """Get preset data without applying it
        
        Args:
            preset_id (str): Identifier of the preset
            
        Returns:
            dict: Preset data or error result
        """
        try:
            preset_path = self.presets_dir / f"{preset_id}.json"
            
            if not preset_path.exists():
                return {
                    'success': False,
                    'message': f'Preset "{preset_id}" not found'
                }
            
            preset_data = self._load_preset_file(preset_path)
            if preset_data:
                return {
                    'success': True,
                    'preset_id': preset_id,
                    'preset_data': preset_data
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to load preset "{preset_id}"'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error getting preset: {e}'
            }
    
    def list_presets(self):
        """List all available presets
        
        Returns:
            dict: List of all presets with their metadata
        """
        try:
            with self._lock:
                presets = {}
                
                for preset_file in self.presets_dir.glob("*.json"):
                    preset_id = preset_file.stem
                    preset_data = self._load_preset_file(preset_file)
                    
                    if preset_data:
                        # Return summary info, not full config
                        presets[preset_id] = {
                            'name': preset_data.get('name', preset_id),
                            'description': preset_data.get('description', ''),
                            'created_at': preset_data.get('created_at'),
                            'updated_at': preset_data.get('updated_at'),
                            'pattern': preset_data.get('config', {}).get('pattern', 'unknown')
                        }
                
                return {
                    'success': True,
                    'presets': presets,
                    'count': len(presets)
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error listing presets: {e}'
            }
    
    def delete_preset(self, preset_id):
        """Delete a preset
        
        Args:
            preset_id (str): Identifier of the preset to delete
            
        Returns:
            dict: Result of the delete operation
        """
        try:
            with self._lock:
                preset_path = self.presets_dir / f"{preset_id}.json"
                
                if not preset_path.exists():
                    return {
                        'success': False,
                        'message': f'Preset "{preset_id}" not found'
                    }
                
                # Get preset name for the response
                preset_data = self._load_preset_file(preset_path)
                preset_name = preset_data.get('name', preset_id) if preset_data else preset_id
                
                # Delete the file
                preset_path.unlink()
                
                return {
                    'success': True,
                    'message': f'Preset "{preset_name}" deleted successfully',
                    'preset_id': preset_id
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error deleting preset: {e}'
            }
    
    def update_preset(self, preset_id, name=None, description=None, light_service=None, metadata=None):
        """Update an existing preset
        
        Args:
            preset_id (str): Identifier of the preset to update
            name (str, optional): New name for the preset
            description (str, optional): New description
            light_service (optional): If provided, update config from current state
            metadata (dict, optional): Additional metadata to merge
            
        Returns:
            dict: Result of the update operation
        """
        try:
            with self._lock:
                preset_path = self.presets_dir / f"{preset_id}.json"
                
                if not preset_path.exists():
                    return {
                        'success': False,
                        'message': f'Preset "{preset_id}" not found'
                    }
                
                # Load existing preset
                preset_data = self._load_preset_file(preset_path)
                if not preset_data:
                    return {
                        'success': False,
                        'message': f'Failed to load preset "{preset_id}" for updating'
                    }
                
                # Update fields
                if name is not None:
                    preset_data['name'] = name
                
                if description is not None:
                    preset_data['description'] = description
                
                if light_service is not None:
                    # Update config from current light service state
                    status = light_service.get_status()
                    preset_data['config'] = {
                        'pattern': status.get('pattern', 'pulse'),
                        'brightness': status.get('brightness', 1.0),
                        'saturation': status.get('saturation', 0.0),
                        'speed_factor': status.get('speed_factor', 1.0),
                        'tempo': status.get('tempo', 60),
                        'alt_mode': status.get('alt_mode', True),
                        'mute': status.get('mute', False),
                        'mute_type': status.get('mute_type', 'instant')
                    }
                
                if metadata is not None:
                    current_metadata = preset_data.get('metadata', {})
                    current_metadata.update(metadata)
                    preset_data['metadata'] = current_metadata
                
                preset_data['updated_at'] = time.time()
                
                # Save updated preset
                success = self._save_preset_file(preset_path, preset_data)
                
                if success:
                    return {
                        'success': True,
                        'message': f'Preset "{preset_data["name"]}" updated successfully',
                        'preset_id': preset_id,
                        'preset_data': preset_data
                    }
                else:
                    return {
                        'success': False,
                        'message': f'Failed to save updated preset "{preset_id}"'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating preset: {e}'
            }