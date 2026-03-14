""" Contains the HeadlessController class which provides the core light control
functionality without the curses display interface for API usage """

import argparse
import random
import time
import threading
import numpy as np
from constants import *
from patterns import droplets, orbits, pixel_train, pulse, sparks, solid
from phase import calculate_phase, modify_phase
from mute import flicker, gradual, instant


class HeadlessController:
    """ Light controller that runs without curses interface for API usage """

    def __init__(self, use_lights=True, n_pixels=50, show_animation=False):
        self.use_lights = use_lights
        self.show_animation = show_animation

        if not use_lights:
            if show_animation:
                self.output = "animation"
                self.n_pix = n_pixels
                from animation import Animation
                self.animation = Animation()
            else:
                self.output = "headless"
                self.n_pix = n_pixels
        else:
            try:
                from pixels import get_pixels, set_all_values, turn_off
                self.get_pixels = get_pixels
                self.set_all_values = set_all_values
                self.turn_off = turn_off
                self.pixels = get_pixels()
                self.n_pix = self.pixels.count()
                self.output = "lights"
            except ImportError:
                # Fallback to headless mode if pixels module not available
                self.output = "headless"
                self.n_pix = n_pixels

        # Initialize state
        self.saturation = 0.0
        self.freq = 1
        self.tempo = 60
        self.cycle_time = 1000
        self.curr_cycle = 0
        self.speed_factor = 1
        self.function = pulse
        self.brightness = 1.0
        self.hue = 30  # Default to warm orange/amber (30 on color wheel)
        self.warm_shift = True
        self.warm_rgb = CANDLE
        self.shape = (self.n_pix, 3)
        self.mute = False
        self.mute_fn = instant
        self.mute_start = None
        self.alt = True
        self._updating = False  # Flag to pause rendering during atomic updates
        self._static_mode = False  # Flag for static patterns that don't need continuous updates
        self._static_rendered = False  # True when static frame has been written to SPI

        # Sunrise state
        self._sunrise_active = False
        self._sunrise_start_time = None
        self._sunrise_duration = 1800  # seconds (30 min default)
        self._sunrise_start_brightness = 0.0
        self._sunrise_end_brightness = 0.8
        self._sunrise_start_hue = 20  # deep orange/red
        self._sunrise_end_hue = 40    # warm white
        self._sunrise_start_saturation = 0.6
        self._sunrise_end_saturation = 0.05

        # Threading controls
        self._running = False
        self._thread = None
        self._fade_thread = None
        self._lock = threading.RLock()
        self._wake_event = threading.Event()  # Used to wake the loop in static mode

    def start(self):
        """Start the light processing loop in a background thread"""
        with self._lock:
            if self._running:
                return False
            self._running = True

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        """Stop the light processing loop"""
        with self._lock:
            self._running = False
        self._wake_event.set()  # Wake the loop so it can exit

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

        # Turn off lights when stopping
        if self.output == "lights":
            self.turn_off(self.pixels)

    def _request_render(self):
        """Mark that a new frame needs to be rendered and wake the loop"""
        self._static_rendered = False
        self._wake_event.set()

    def _run_loop(self):
        """Main light processing loop"""
        start_time = time.time()
        rgb_values = np.zeros((self.n_pix, 3))
        cache = {}

        try:
            while self._running:
                # Timing
                loop_start = time.time()
                elapsed = (loop_start - start_time) * 1000
                phase, n_cycles = calculate_phase(elapsed, self.cycle_time)

                # Thread-safe access to parameters
                with self._lock:
                    # Skip rendering during atomic updates
                    if self._updating:
                        time.sleep(0.001)
                        continue

                    # Sunrise interpolation
                    if self._sunrise_active and self._sunrise_start_time:
                        elapsed_sunrise = loop_start - self._sunrise_start_time
                        progress = min(1.0, elapsed_sunrise / self._sunrise_duration)

                        self.brightness = self._sunrise_start_brightness + (
                            self._sunrise_end_brightness - self._sunrise_start_brightness) * progress
                        hue_deg = self._sunrise_start_hue + (
                            self._sunrise_end_hue - self._sunrise_start_hue) * progress
                        self.hue = int(hue_deg * 255 / 360)
                        self.saturation = self._sunrise_start_saturation + (
                            self._sunrise_end_saturation - self._sunrise_start_saturation) * progress

                        if self._static_mode:
                            self._static_rendered = False

                        if progress >= 1.0:
                            self._sunrise_active = False

                    # Static mode: if already rendered and nothing changed, just sleep
                    if self._static_mode and self._static_rendered:
                        # Check if muting (need to animate the mute effect)
                        if self.mute and self.mute_start:
                            pass  # Fall through to render the mute animation
                        else:
                            # Nothing to do — sleep until woken by a parameter change
                            self._wake_event.clear()
                            # Release lock before sleeping
                            lock_ref = self._lock
                            lock_ref.release()
                            try:
                                # Wake every 0.5s to check sunrise progress, or immediately on param change
                                self._wake_event.wait(timeout=0.5 if self._sunrise_active else 5.0)
                            finally:
                                lock_ref.acquire()
                            continue

                    curr_speed = self.speed_factor
                    curr_function = self.function
                    curr_brightness = self.brightness
                    curr_saturation = self.saturation
                    curr_hue = self.hue
                    curr_warm_rgb = self.warm_rgb
                    curr_warm_shift = self.warm_shift
                    curr_alt = self.alt
                    curr_mute = self.mute
                    curr_mute_fn = self.mute_fn
                    curr_mute_start = self.mute_start
                    is_static = self._static_mode

                # Speeding up or slowing down phase
                if curr_function == pixel_train:
                    curr_speed /= 4.0
                phase, direction = modify_phase(phase, n_cycles, curr_speed)

                kwargs = {"shape": self.shape,
                          "n_cycles": n_cycles,
                          "saturation": curr_saturation,
                          "hue": curr_hue,
                          "warm_rgb": curr_warm_rgb,
                          "warm_shift": curr_warm_shift,
                          "alt": curr_alt,
                          "loop_start": loop_start}

                # Generate new colors
                rgb_values, cache = curr_function(phase, cache, kwargs)

                # Master dimming
                rgb_values_curr = (rgb_values * curr_brightness).astype(int)

                # Mute functions
                if curr_mute and curr_mute_start:
                    elapsed_mute = (loop_start - curr_mute_start) * 1000
                    rgb_values_curr = (rgb_values_curr * curr_mute_fn(elapsed_mute, kwargs)).astype(int)

                # Set and show pixel values
                if self.output == "lights":
                    self.set_all_values(self.pixels, rgb_values_curr)
                    self.pixels.show()
                elif self.output == "animation":
                    self.animation.update(rgb_values_curr)

                # Mark static frame as rendered so we stop writing to SPI
                if is_static and not curr_mute:
                    with self._lock:
                        self._static_rendered = True

                # Sleep: animated patterns run at ~60fps
                time.sleep(0.016)

        except Exception as e:
            print(f"Error in light loop: {e}")
        finally:
            if self.output == "lights":
                self.turn_off(self.pixels)

    # Pattern control methods
    def set_pattern(self, pattern_name):
        """Set the current light pattern"""
        pattern_map = {
            'pulse': pulse,
            'pixel_train': pixel_train,
            'droplets': droplets,
            'orbits': orbits,
            'sparks': sparks,
            'solid': solid
        }
        
        if pattern_name.lower() in pattern_map:
            with self._lock:
                self.function = pattern_map[pattern_name.lower()]
                if pattern_name.lower() == 'solid':
                    self._static_mode = True
                else:
                    self._static_mode = False
                self._request_render()
            return True
        return False
    
    def set_brightness(self, brightness, transition=0.0):
        """Set brightness (0.0 to 1.0) with optional smooth transition"""
        brightness = max(0.0, min(1.0, float(brightness)))
        if transition > 0 and self._running:
            # Smooth fade in a background thread
            threading.Thread(
                target=self._fade_brightness,
                args=(brightness, transition),
                daemon=True
            ).start()
        else:
            with self._lock:
                self.brightness = brightness
                self._request_render()
        return brightness

    def _fade_brightness(self, target, duration):
        """Smoothly fade brightness over duration seconds"""
        steps = max(1, int(duration * 30))  # 30 steps per second
        with self._lock:
            start_val = self.brightness
        for i in range(1, steps + 1):
            if not self._running:
                break
            # Ease-out curve for natural feel
            progress = i / steps
            eased = 1.0 - (1.0 - progress) ** 2
            val = start_val + (target - start_val) * eased
            with self._lock:
                self.brightness = val
                self._request_render()
            time.sleep(duration / steps)
        with self._lock:
            self.brightness = target
            self._request_render()
    
    def set_saturation(self, saturation):
        """Set saturation (0.0 to 1.0)"""
        saturation = max(0.0, min(1.0, float(saturation)))
        with self._lock:
            self.saturation = saturation
            self._request_render()
        return saturation

    def set_hue(self, hue):
        """Set color hue (0-360 degrees, mapped to 0-255 color wheel)"""
        hue = max(0, min(360, float(hue)))
        wheel_value = int(hue * 255 / 360)
        with self._lock:
            self.hue = wheel_value
            self._request_render()
        return hue
    
    def set_speed(self, speed_factor):
        """Set speed multiplier"""
        speed_factor = max(0.1, min(8.0, float(speed_factor)))
        with self._lock:
            self.speed_factor = speed_factor
        return speed_factor
    
    def set_tempo(self, bpm):
        """Set tempo in beats per minute"""
        bpm = max(30, min(300, int(bpm)))
        cycle_time = 60000 / bpm  # Convert BPM to milliseconds per cycle
        with self._lock:
            self.tempo = bpm
            self.cycle_time = cycle_time
        return bpm
    
    def toggle_alt_mode(self):
        """Toggle alternate mode"""
        with self._lock:
            self.alt = not self.alt
        return self.alt
    
    def sync_phase(self):
        """Sync the phase (restart timing)"""
        # This will be handled by restarting the timing in the loop
        return True
    
    def set_mute(self, mute_enabled, mute_type='instant'):
        """Set mute state and type"""
        from mute import fade_in, fade_out
        mute_map = {
            'instant': instant,
            'gradual': gradual,
            'flicker': flicker,
            'fade_out': fade_out,
            'fade_in': fade_in
        }
        
        if mute_type.lower() in mute_map:
            with self._lock:
                self.mute = bool(mute_enabled)
                self.mute_fn = mute_map[mute_type.lower()]
                if self.mute and not self.mute_start:
                    self.mute_start = time.time()
                elif not self.mute:
                    self.mute_start = None
                self._request_render()
            return True
        return False
    
    def set_all_atomic(self, pattern=None, brightness=None, saturation=None, hue=None, mute=None):
        """Set multiple parameters atomically without intermediate rendering"""
        with self._lock:
            # Pause rendering during the update
            self._updating = True
            
            try:
                # Set all parameters
                if pattern is not None:
                    pattern_map = {
                        'pulse': pulse,
                        'pixel_train': pixel_train,
                        'droplets': droplets,
                        'orbits': orbits,
                        'sparks': sparks,
                        'solid': solid
                    }
                    if pattern.lower() in pattern_map:
                        self.function = pattern_map[pattern.lower()]
                        if pattern.lower() == 'solid':
                            self._static_mode = True
                        else:
                            self._static_mode = False
                
                if brightness is not None:
                    self.brightness = max(0.0, min(1.0, float(brightness)))
                    
                if saturation is not None:
                    self.saturation = max(0.0, min(1.0, float(saturation)))
                    
                if hue is not None:
                    hue_val = max(0, min(360, float(hue)))
                    self.hue = int(hue_val * 255 / 360)
                    
                if mute is not None:
                    self.mute = bool(mute)
                    if self.mute and not self.mute_start:
                        self.mute_start = time.time()
                    elif not self.mute:
                        self.mute_start = None
                        
                # Short delay to ensure any in-progress frame completes
                time.sleep(0.02)

            finally:
                # Resume rendering and request a new frame
                self._updating = False
                self._request_render()
                
        return True
    
    def start_sunrise(self, duration_minutes=30, end_brightness=0.8,
                       start_hue=20, end_hue=40,
                       start_saturation=0.6, end_saturation=0.05):
        """Start a sunrise fade-in over the given duration"""
        with self._lock:
            self._sunrise_duration = duration_minutes * 60
            self._sunrise_start_brightness = 0.0
            self._sunrise_end_brightness = max(0.0, min(1.0, float(end_brightness)))
            self._sunrise_start_hue = float(start_hue)
            self._sunrise_end_hue = float(end_hue)
            self._sunrise_start_saturation = float(start_saturation)
            self._sunrise_end_saturation = float(end_saturation)

            # Set initial state
            self.brightness = 0.0
            self.hue = int(start_hue * 255 / 360)
            self.saturation = start_saturation
            self.mute = False
            self.mute_start = None

            # Activate
            self._sunrise_start_time = time.time()
            self._sunrise_active = True
            self._request_render()
        return True

    def stop_sunrise(self):
        """Cancel sunrise, keep current brightness"""
        with self._lock:
            self._sunrise_active = False
        return True

    def get_sunrise_status(self):
        """Get sunrise progress"""
        with self._lock:
            if not self._sunrise_active or not self._sunrise_start_time:
                return {'active': False}
            elapsed = time.time() - self._sunrise_start_time
            progress = min(1.0, elapsed / self._sunrise_duration)
            remaining = max(0, self._sunrise_duration - elapsed)
            return {
                'active': True,
                'progress': round(progress, 4),
                'progress_percent': round(progress * 100, 1),
                'elapsed_seconds': round(elapsed, 1),
                'remaining_seconds': round(remaining, 1),
                'remaining_minutes': round(remaining / 60, 1),
                'current_brightness': round(self.brightness, 3),
            }

    def get_status(self):
        """Get current controller status"""
        with self._lock:
            # Get pattern name
            pattern_name = 'unknown'
            for name, func in [('pulse', pulse), ('pixel_train', pixel_train), 
                             ('droplets', droplets), ('orbits', orbits), ('sparks', sparks), ('solid', solid)]:
                if self.function == func:
                    pattern_name = name
                    break
            
            # Get mute function name  
            mute_name = 'unknown'
            for name, func in [('instant', instant), ('gradual', gradual), ('flicker', flicker)]:
                if self.mute_fn == func:
                    mute_name = name
                    break
            
            return {
                'running': self._running,
                'pattern': pattern_name,
                'brightness': self.brightness,
                'saturation': self.saturation,
                'hue': int(self.hue * 360 / 255),  # Convert back to 0-360 degrees
                'speed_factor': self.speed_factor,
                'tempo': self.tempo,
                'alt_mode': self.alt,
                'mute': self.mute,
                'mute_type': mute_name,
                'output_mode': self.output,
                'n_pixels': self.n_pix
            }