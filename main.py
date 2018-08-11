from functions import *
from colors import *
import random
import time
import numpy as np
import sys
import curses

# HOW TO IMPLEMENT DELAY / DIMMER


class Controller:
    def __init__(self):
        self.max_tempo = 200
        self.min_tempo = 0.25
        self.start_rgb = WARM_CANDLE
        self.start_color = Adafruit_WS2801.RGB_to_color(*self.start_rgb)
        self.freq = 1
        self.tempo = 60
        self.cycle_time = 1000
        self.curr_cycle = 0
        self.tap_start = None
        self.tap_end = None
        self.pixels = get_pixels()
        self.n_pix = self.pixels.count()
        self.function = self.test_fn
        self.brightness = 1.

    def test_fn(self, rgb_values):
        return rgb_values + 1

    def start(self):
        self.start_time = time.time()
        self.rgb_values = np.zeros((n_pix, 3))
        try:
            while True:
                elapsed = time.time() - self.start_time
                phase, n_cycles = calculate_phase(elapsed, self.cycle_time)
                self.rgb_values = self.function(self.rgb_values)
                final_rgb_values = (self.rgb_values * brightness).astype(int)



        finally:
            turn_off(pixels)
