from pixel_fns import *
from pattern_fns import *
from colors import *
from constants import *
import random
import time
import numpy as np
from display import Display
import curses
from phase import modify_phase, calculate_phase

# DEFAULT WARM SHIFT
# HOW TO IMPLEMENT TRANSITION EFFECTS
# ORBITS IN OPPOSITE DIRECTIONS
# FLASHING NON PERSISTANT EFFECT
# Droplet from centre then droplet from edges


class Controller:
    def __init__(self):
        self.rgb = WARM_CANDLE
        self.saturation = 0.
        self.freq = 1
        self.tempo = 60
        self.show_disp = True
        self.cycle_time = 1000
        self.curr_cycle = 0
        self.tap_start = None
        self.tap_end = None
        self.speed_factor = 1
        self.pixels = get_pixels()
        self.n_pix = self.pixels.count()
        self.function = pulse
        self.brightness = 0.5
        self.shape = (self.n_pix, 3)
        if self.show_disp:
            self.display = Display()

    def start(self):
        self.start_time = time.time()
        counter = 0
        rgb_values = np.zeros((self.n_pix, 3))
        cache = {}
        try:
            # Main loop
            while True:

                # Check for keypress
                if self.show_disp:
                    self.process_press()

                # Timing
                act_start = time.time()
                elapsed = (act_start - self.start_time) * 1000 
                phase, n_cycles = calculate_phase(elapsed, self.cycle_time)

                # Speeding up or slowing down phase
                curr_speed = self.speed_factor
                if self.function == pixel_train:
                    curr_speed /= 4.
                phase, direction = modify_phase(phase, n_cycles, curr_speed)

                kwargs = {"shape": self.shape,
                          "rgb": self.rgb,
                          "n_cycles": n_cycles,
                          "saturation": self.saturation}

                # Generate new colors (persisting)
                rgb_values, cache = self.function(phase,
                                                  cache,
                                                  kwargs)

                # Master dimming
                rgb_values_curr = (rgb_values * self.brightness).astype(int)

                # Set and show pixel values
                set_all_values(self.pixels, rgb_values_curr)
                self.pixels.show()

                # Timing
                act_end = time.time()
                act_dur = act_end - act_start
                act_freq = 1000 / (act_dur * 1000)

                # Update Display
                if self.show_disp:
                    self.display.update(self.tempo,
                                        FN_NAMES[self.function],
                                        self.brightness,
                                        self.speed_factor,
                                        self.saturation,
                                        phase,
                                        direction)
                
        finally:
            turn_off(self.pixels)
            if self.show_disp:
                self.display.close()

    def process_press(self):
        ch = self.display.getch()

        if ch == SPACEBAR: # i.e. key pressed
            self.tap_start = self.tap_end
            self.tap_end = time.time()
            tempo_update = self.calculate_times()
            if tempo_update:
                self.start_time = time.time()

        # Toggle different lighting modes
        elif ch == A_KEY:
            self.function = pulse
        elif ch == S_KEY:
            self.function = pixel_train
        elif ch == D_KEY:
            self.function = droplets

        # Master control keys
        elif ch == C_KEY:
            self.start_time = time.time()
        elif ch == LEFT:
            self.brightness -= 0.02
            self.brightness = min(self.brightness, 1)
            self.brightness = max(self.brightness, 0)
        elif ch == RIGHT:
            self.brightness += 0.02
            self.brightness = min(self.brightness, 1)
            self.brightness = max(self.brightness, 0)
        elif ch == UP:
            self.speed_factor = self.speed_factor * 2
        elif ch == DOWN:
            self.speed_factor = self.speed_factor / 2.
        elif ch == PLUS_KEY:
            self.saturation += 0.02
            self.saturation = min(self.saturation, 1)
            self.saturation = max(self.saturation, 0)
        elif ch == MINUS_KEY:
            self.saturation -= 0.02
            self.saturation = min(self.saturation, 1)
            self.saturation = max(self.saturation, 0)

        elif ch != -1:
            self.display.set_field("debug", ch)

    def calculate_times(self):
        if not self.tap_start:
            return
        dur = (self.tap_end - self.tap_start) * 1000
        self.freq = 1000 / dur
        new_tempo = self.freq * 60
        self.tempo = new_tempo
        self.cycle_time = dur
        return True


if __name__ == "__main__":
    c = Controller()
    c.start()