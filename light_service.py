""" Thread-safe light service wrapper for API operations """

import threading
import time
import atexit
from headless_controller import HeadlessController


class APILightService:
    """ Thread-safe wrapper for light operations that can be controlled via API """
    
    def __init__(self, use_lights=True, n_pixels=50, show_animation=False):
        self.controller = HeadlessController(use_lights=use_lights, n_pixels=n_pixels, show_animation=show_animation)
        self._lock = threading.RLock()
        self._initialized = False
        
        # Register cleanup on exit
        atexit.register(self.shutdown)
    
    def initialize(self):
        """Initialize and start the light service"""
        with self._lock:
            if not self._initialized:
                success = self.controller.start()
                if success:
                    self._initialized = True
                    # Give the controller a moment to start up
                    time.sleep(0.1)
                return success
            return True
    
    def shutdown(self):
        """Shutdown the light service"""
        with self._lock:
            if self._initialized:
                self.controller.stop()
                self._initialized = False
    
    def is_running(self):
        """Check if the service is running"""
        with self._lock:
            return self._initialized and self.controller._running
    
    # Pattern control methods
    def set_pattern(self, pattern_name):
        """Set the current light pattern
        
        Args:
            pattern_name (str): Name of pattern ('pulse', 'pixel_train', 'droplets', 'orbits', 'sparks')
            
        Returns:
            dict: Result with success status and message
        """
        if not self._initialized:
            return {'success': False, 'message': 'Service not initialized'}
        
        success = self.controller.set_pattern(pattern_name)
        if success:
            return {'success': True, 'message': f'Pattern set to {pattern_name}', 'pattern': pattern_name}
        else:
            return {'success': False, 'message': f'Invalid pattern name: {pattern_name}'}
    
    def set_brightness(self, brightness):
        """Set brightness level
        
        Args:
            brightness (float): Brightness level (0.0 to 1.0) or (0 to 100 for percentage)
            
        Returns:
            dict: Result with success status and actual brightness value
        """
        if not self._initialized:
            return {'success': False, 'message': 'Service not initialized'}
        
        # Handle percentage values
        if brightness > 1.0:
            brightness = brightness / 100.0
        
        actual_brightness = self.controller.set_brightness(brightness)
        return {
            'success': True, 
            'message': f'Brightness set to {int(actual_brightness * 100)}%',
            'brightness': actual_brightness,
            'brightness_percent': int(actual_brightness * 100)
        }
    
    def set_saturation(self, saturation):
        """Set color saturation
        
        Args:
            saturation (float): Saturation level (0.0 to 1.0) or (0 to 100 for percentage)
            
        Returns:
            dict: Result with success status and actual saturation value
        """
        if not self._initialized:
            return {'success': False, 'message': 'Service not initialized'}
        
        # Handle percentage values
        if saturation > 1.0:
            saturation = saturation / 100.0
        
        actual_saturation = self.controller.set_saturation(saturation)
        return {
            'success': True,
            'message': f'Saturation set to {int(actual_saturation * 100)}%',
            'saturation': actual_saturation,
            'saturation_percent': int(actual_saturation * 100)
        }
    
    def set_speed(self, speed_factor):
        """Set animation speed multiplier
        
        Args:
            speed_factor (float): Speed multiplier (0.1 to 8.0)
            
        Returns:
            dict: Result with success status and actual speed value
        """
        if not self._initialized:
            return {'success': False, 'message': 'Service not initialized'}
        
        actual_speed = self.controller.set_speed(speed_factor)
        return {
            'success': True,
            'message': f'Speed set to {actual_speed}x',
            'speed_factor': actual_speed
        }
    
    def set_tempo(self, bpm):
        """Set tempo in beats per minute
        
        Args:
            bpm (int): Beats per minute (30 to 300)
            
        Returns:
            dict: Result with success status and actual tempo value
        """
        if not self._initialized:
            return {'success': False, 'message': 'Service not initialized'}
        
        actual_tempo = self.controller.set_tempo(bpm)
        return {
            'success': True,
            'message': f'Tempo set to {actual_tempo} BPM',
            'tempo': actual_tempo
        }
    
    def toggle_alt_mode(self):
        """Toggle alternate pattern mode
        
        Returns:
            dict: Result with success status and current alt mode state
        """
        if not self._initialized:
            return {'success': False, 'message': 'Service not initialized'}
        
        alt_state = self.controller.toggle_alt_mode()
        return {
            'success': True,
            'message': f'Alt mode {"enabled" if alt_state else "disabled"}',
            'alt_mode': alt_state
        }
    
    def sync_phase(self):
        """Synchronize the animation phase (restart timing)
        
        Returns:
            dict: Result with success status
        """
        if not self._initialized:
            return {'success': False, 'message': 'Service not initialized'}
        
        self.controller.sync_phase()
        return {
            'success': True,
            'message': 'Phase synchronized'
        }
    
    def set_mute(self, enabled, mute_type='instant'):
        """Set mute state and type
        
        Args:
            enabled (bool): Whether to enable mute
            mute_type (str): Type of mute ('instant', 'gradual', 'flicker')
            
        Returns:
            dict: Result with success status and mute state
        """
        if not self._initialized:
            return {'success': False, 'message': 'Service not initialized'}
        
        success = self.controller.set_mute(enabled, mute_type)
        if success:
            return {
                'success': True,
                'message': f'Mute {"enabled" if enabled else "disabled"} with {mute_type} mode',
                'mute': enabled,
                'mute_type': mute_type
            }
        else:
            return {'success': False, 'message': f'Invalid mute type: {mute_type}'}
    
    def get_status(self):
        """Get comprehensive service and controller status
        
        Returns:
            dict: Complete status information
        """
        controller_status = self.controller.get_status() if self._initialized else {}
        
        return {
            'service_initialized': self._initialized,
            'service_running': self.is_running(),
            **controller_status
        }
    
    def get_available_patterns(self):
        """Get list of available light patterns
        
        Returns:
            dict: Available patterns and their descriptions
        """
        return {
            'success': True,
            'patterns': {
                'pulse': 'Synchronized pulsing effect across all lights',
                'pixel_train': 'Moving train of colored pixels',
                'droplets': 'Water droplet-like expanding effects',
                'orbits': 'Two colored lights orbiting around the strip',
                'sparks': 'Random sparkling effect'
            }
        }
    
    def get_available_mute_types(self):
        """Get list of available mute types
        
        Returns:
            dict: Available mute types and their descriptions
        """
        return {
            'success': True,
            'mute_types': {
                'instant': 'Immediately turn off lights',
                'gradual': 'Gradually fade lights to off',
                'flicker': 'Flicker effect before turning off'
            }
        }


# Global service instance
_light_service = None
_service_lock = threading.Lock()


def get_light_service(use_lights=True, n_pixels=50, show_animation=False):
    """Get the global light service instance (singleton pattern)
    
    Args:
        use_lights (bool): Whether to control actual lights or use animation
        n_pixels (int): Number of pixels if using animation mode
        show_animation (bool): Whether to show pygame animation when use_lights=False
        
    Returns:
        APILightService: The global service instance
    """
    global _light_service
    
    with _service_lock:
        if _light_service is None:
            _light_service = APILightService(use_lights=use_lights, n_pixels=n_pixels, show_animation=show_animation)
        return _light_service