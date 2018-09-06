""" Contains the Controller class which is the core of the program"""

import argparse
import curses
import random
import time

import numpy as np
from animation import Animation
from constants import *
from display import Display
from mute import flicker, gradual, instant
from patterns import droplets, orbits, pixel_train, pulse, sparks
from phase import calculate_phase, modify_phase

parser = argparse.ArgumentParser(
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--no_lights', dest='no_lights', action='store_true')
parser.set_defaults(feature=True)
args = parser.parse_args()

if not args.no_lights:
    from pixels import get_pixels, set_all_values, turn_off

class Controller:
    """ This class contains the main loop which handles the key press functions,
    the light updates and display updates """

    def __init__(self):
        if args.no_lights:
            self.output = "animation"
            self.n_pix = 50
            self.animation = Animation()
        else:
            self.pixels = get_pixels()
            self.n_pix = self.pixels.count()
            self.output = "lights"
        self.saturation = 0.
        self.freq = 1
        self.tempo = 60
        self.show_disp = True
        self.cycle_time = 1000
        self.curr_cycle = 0
        self.tap_start = None
        self.tap_end = None
        self.speed_factor = 1
        self.function = pulse
        self.brightness = 1.
        self.warm_shift = True
        self.warm_rgb = CANDLE
        self.shape = (self.n_pix, 3)
        self.mute = False
        self.mute_fn = instant
        self.mute_start = None
        self.show_key = False
        self.alt = False
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
                loop_start = time.time()
                elapsed = (loop_start - self.start_time) * 1000 
                phase, n_cycles = calculate_phase(elapsed, self.cycle_time)

                # Speeding up or slowing down phase
                curr_speed = self.speed_factor
                if self.function == pixel_train:
                    curr_speed /= 4.
                phase, direction = modify_phase(phase, n_cycles, curr_speed)

                kwargs = {"shape": self.shape,
                          "n_cycles": n_cycles,
                          "saturation": self.saturation,
                          "warm_rgb": self.warm_rgb,
                          "warm_shift": self.warm_shift,
                          "alt": self.alt,
                          "loop_start": loop_start}

                # Generate new colors (persisting)
                rgb_values, cache = self.function(phase,
                                                  cache,
                                                  kwargs)

                # Master dimming
                rgb_values_curr = (rgb_values * self.brightness).astype(int)

                # Mute functions
                if self.mute:
                    elapsed_mute = (loop_start - self.mute_start) * 1000
                    rgb_values_curr = (rgb_values_curr * self.mute_fn(elapsed_mute, kwargs)).astype(int)

                # Set and show pixel values
                if self.output == "lights":
                    set_all_values(self.pixels, rgb_values_curr)
                    self.pixels.show()
                elif self.output == "animation":
                    self.animation.update(rgb_values_curr)

                # Timing
                loop_end = time.time()
                loop_dur = loop_end - loop_start
                act_freq = 1000 / (loop_dur * 1000)

                # Update Display
                if self.show_disp:
                    self.display.update(self.tempo,
                                        PATTERN_FN_NAMES[self.function],
                                        self.brightness,
                                        self.speed_factor,
                                        self.saturation,
                                        phase,
                                        direction,
                                        MUTE_FN_NAMES[self.mute_fn],
                                        self.mute,
                                        self.alt)
                
        finally:
            if self.output == "lights":
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

        # Lighting modes
        elif ch == A_KEY:
            self.function = pulse
        elif ch == S_KEY:
            self.function = pixel_train
        elif ch == D_KEY:
            self.function = droplets
        elif ch == F_KEY:
            self.function = orbits
        elif ch == G_KEY:
            self.function = sparks
        elif ch == B_KEY:
            self.alt = not self.alt

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

        # Mute keys
        elif ch == ENTER:
            if not self.mute:
                self.mute = True
                self.mute_start = time.time()
            else:
                self.mute = False
                self.mute_start = None
        elif ch == Q_KEY:
            self.mute_fn = instant
        elif ch == W_KEY:
            self.mute_fn = gradual
        elif ch == E_KEY:
            self.mute_fn = flicker

        elif ch != -1:
            if self.show_key:
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
