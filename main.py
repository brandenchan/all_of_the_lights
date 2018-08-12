from pixel_fns import *
from pattern_fns import *
from colors import *
# from pixel_train import pixel_train
import random
import time
import numpy as np
from display import Display
import curses

# HOW TO IMPLEMENT DELAY / DIMMER
# HOW TO IMPLEMENT TRANSITION EFFECTS
# HOW TO IMPLEMENT WAIT
# ORBITS IN OPPOSITE DIRECTIONS
# ADD GRAPH - DISP CONSTANTLY UPDATES

SPACEBAR = 32
S_KEY = 115
A_KEY = 97
C_KEY = 99

class Controller:
    def __init__(self):
        # self.max_tempo = 200
        # self.min_tempo = 0.25
        self.rgb = WARM_CANDLE
        # self.color = Adafruit_WS2801.RGB_to_color(*self.rgb)
        self.freq = 1
        self.tempo = 60
        self.show_disp = True
        self.cycle_time = 1000
        self.curr_cycle = 0
        self.tap_start = None
        self.tap_end = None
        self.pixels = get_pixels()
        self.n_pix = self.pixels.count()
        self.function = test_fn
        self.brightness = 1
        self.shape = (self.n_pix, 3)
        if self.show_disp:
            self.display = Display()
            self.display.update("tempo", self.tempo)

    def start(self):
        self.start_time = time.time()
        counter = 0
        rgb_values = np.zeros((self.n_pix, 3))
        cache = None
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

                kwargs = {"shape": self.shape,
                          "rgb": self.rgb}

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
                self.display.update("freq", act_freq)
                

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
                self.display.update("tempo", self.tempo)
        elif ch == S_KEY:
            self.function = pixel_train
        elif ch == A_KEY:
            self.function = test_fn
        elif ch == C_KEY:
            self.start_time = time.time()
        elif ch != -1:
            self.display.update("debug", ch)

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