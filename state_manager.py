""" State management for persisting and restoring light controller settings """

import json
import os
import threading
import time
from pathlib import Path


class StateManager:
    """ Manages saving and loading of light controller state """
    
    DEFAULT_STATE_DIR = os.path.expanduser("~/.all_of_the_lights")
    DEFAULT_STATE_FILE = "controller_state.json"
    
    def __init__(self, state_dir=None, state_file=None):
        self.state_dir = Path(state_dir) if state_dir else Path(self.DEFAULT_STATE_DIR)
        self.state_file = state_file or self.DEFAULT_STATE_FILE
        self.state_path = self.state_dir / self.state_file
        self._lock = threading.RLock()
        
        # Ensure state directory exists
        self.state_dir.mkdir(parents=True, exist_ok=True)
    
    def save_state(self, controller_status, metadata=None):
        """Save controller state to file
        
        Args:
            controller_status (dict): Status from controller.get_status()
            metadata (dict, optional): Additional metadata to save
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            with self._lock:
                state_data = {
                    'timestamp': time.time(),
                    'controller_state': controller_status,
                    'metadata': metadata or {}
                }
                
                # Write to temporary file first, then rename for atomic operation
                temp_path = self.state_path.with_suffix('.tmp')
                with open(temp_path, 'w') as f:
                    json.dump(state_data, f, indent=2)
                
                # Atomic rename
                temp_path.rename(self.state_path)
                return True
                
        except Exception as e:
            print(f"Error saving state: {e}")
            return False
    
    def load_state(self):
        """Load controller state from file
        
        Returns:
            dict or None: State data if loaded successfully, None otherwise
        """
        try:
            with self._lock:
                if not self.state_path.exists():
                    return None
                
                with open(self.state_path, 'r') as f:
                    state_data = json.load(f)
                
                return state_data
                
        except Exception as e:
            print(f"Error loading state: {e}")
            return None
    
    def get_controller_state(self):
        """Get just the controller state portion
        
        Returns:
            dict or None: Controller state if available, None otherwise
        """
        state_data = self.load_state()
        if state_data and 'controller_state' in state_data:
            return state_data['controller_state']
        return None
    
    def state_exists(self):
        """Check if state file exists
        
        Returns:
            bool: True if state file exists
        """
        return self.state_path.exists()
    
    def delete_state(self):
        """Delete the state file
        
        Returns:
            bool: True if deleted successfully or file didn't exist
        """
        try:
            if self.state_path.exists():
                self.state_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting state: {e}")
            return False
    
    def create_default_state(self):
        """Create a default state configuration
        
        Returns:
            dict: Default controller state
        """
        return {
            'running': True,
            'pattern': 'pulse',
            'brightness': 1.0,
            'saturation': 0.0,
            'speed_factor': 1.0,
            'tempo': 60,
            'alt_mode': True,
            'mute': False,
            'mute_type': 'instant',
            'output_mode': 'animation',
            'n_pixels': 50
        }
    
    def apply_state_to_service(self, light_service, state=None):
        """Apply saved state to a light service
        
        Args:
            light_service: APILightService instance
            state (dict, optional): State to apply. If None, loads from file
            
        Returns:
            dict: Result of applying the state
        """
        if state is None:
            state = self.get_controller_state()
        
        if not state:
            # Use default state if no saved state found
            state = self.create_default_state()
        
        results = []
        
        try:
            # Apply each setting
            if 'pattern' in state:
                result = light_service.set_pattern(state['pattern'])
                results.append(('pattern', result))
            
            if 'brightness' in state:
                result = light_service.set_brightness(state['brightness'])
                results.append(('brightness', result))
            
            if 'saturation' in state:
                result = light_service.set_saturation(state['saturation'])
                results.append(('saturation', result))
            
            if 'speed_factor' in state:
                result = light_service.set_speed(state['speed_factor'])
                results.append(('speed_factor', result))
            
            if 'tempo' in state:
                result = light_service.set_tempo(state['tempo'])
                results.append(('tempo', result))
            
            if 'alt_mode' in state:
                # Only toggle if current state differs from desired state
                current_status = light_service.get_status()
                if current_status.get('alt_mode') != state['alt_mode']:
                    result = light_service.toggle_alt_mode()
                    results.append(('alt_mode', result))
            
            if 'mute' in state and 'mute_type' in state:
                result = light_service.set_mute(state['mute'], state['mute_type'])
                results.append(('mute', result))
            
            # Count successful applications
            successful = sum(1 for _, result in results if result.get('success', False))
            total = len(results)
            
            return {
                'success': successful > 0,
                'message': f'Applied {successful}/{total} state settings',
                'results': results,
                'state_applied': state
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error applying state: {e}',
                'results': results
            }


class AutoStateManager:
    """ Automatically saves state at regular intervals """
    
    def __init__(self, light_service, state_manager=None, save_interval=30):
        self.light_service = light_service
        self.state_manager = state_manager or StateManager()
        self.save_interval = save_interval  # seconds
        self._running = False
        self._thread = None
        self._lock = threading.Lock()
    
    def start(self):
        """Start automatic state saving"""
        with self._lock:
            if self._running:
                return False
            
            self._running = True
            self._thread = threading.Thread(target=self._save_loop, daemon=True)
            self._thread.start()
            return True
    
    def stop(self):
        """Stop automatic state saving"""
        with self._lock:
            self._running = False
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
    
    def _save_loop(self):
        """Main loop for automatic state saving"""
        while self._running:
            try:
                # Get current status and save it
                status = self.light_service.get_status()
                if status.get('service_running', False):
                    self.state_manager.save_state(status, {'auto_saved': True})
                
                # Wait for next save interval
                for _ in range(int(self.save_interval)):
                    if not self._running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                print(f"Error in auto-save loop: {e}")
                time.sleep(5)  # Wait a bit before retrying
    
    def force_save(self):
        """Force an immediate save"""
        try:
            status = self.light_service.get_status()
            return self.state_manager.save_state(status, {'manual_save': True})
        except Exception as e:
            print(f"Error in force save: {e}")
            return False