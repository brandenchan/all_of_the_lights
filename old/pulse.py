from functions import *
from colors import *
import random
import time
import numpy as np
import curses

# BUTTON FOR DOUBLE / HALF SPEED
# BUTTON FOR COLOR CHANGE


class Pulser:
    def __init__(self):
        self.max_tempo = 200
        self.min_tempo = 0.25
        self.rgb = PINK
        self.color = Adafruit_WS2801.RGB_to_color(*self.rgb)
        self.floor = 0.05
        self.freq = None
        self.tempo = None
        self.cycle_time = None
        self.clock = 0
        self.tap_start = None
        self.tap_end = None
        self.pixels = get_pixels()
        self.n_pix = self.pixels.count()

    def start_curses(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)
        self.stdscr.nodelay(1)
        self.stdscr.box()

    def end_curses(self):
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()

    def pulse(self):
        try:
            self.start_curses()
            while True:
                act_start = time.time()
                ch = self.stdscr.getch()
                if ch != -1: # i.e. key pressed
                    self.tap_start = self.tap_end
                    self.tap_end = time.time()
                    success = self.calculate_times()
                    if success:
                        self.clock = 0
                color_arr = self.calculate_colors()
                if color_arr is not None:
                    set_all_values(self.pixels, color_arr)
                self.pixels.show()
                act_end = time.time()
                act_dur = (act_end - act_start) * 1000
                self.clock += act_dur
        finally:
            turn_off(self.pixels)
            self.end_curses()

    def calculate_times(self):
        if not self.tap_start:
            return
        dur = (self.tap_end - self.tap_start) * 1000
        self.freq = 1000 / dur
        new_tempo = self.freq * 60
        if self.tempo != new_tempo:
            
            self.stdscr.clear()
            self.stdscr.box()
            self.stdscr.addstr(1, 1, "tempo: {}\n".format(self.tempo))


            
        self.tempo = new_tempo
        self.cycle_time = dur
        return True

    def calculate_colors(self, fn="sine"):
        if not self.cycle_time:
            return None
        phase = (self.clock % self.cycle_time / self.cycle_time) * 2
        rads = phase * np.pi
        bright = np.asarray([self.rgb] * self.n_pix)
        if fn == "sine":
            rads_shifted = rads + (0.5 * np.pi)     # So that phase starts at max value
            dim_factor_unsmoothed = (np.sin(rads) + 1) / 2
            dim_factor = self.floor + ((1-self.floor) * dim_factor_unsmoothed)
        elif fn == "spiking":
            if rads > 1.5 * np.pi:
                exp_phase = ((rads - (1.5 * np.pi)) / np.pi) * 2
                dim_factor = np.exp2(exp_phase) - 1
            else:
                lin_phase = 1 - (rads / np.pi / 1.5)
                dim_factor = lin_phase
        colors = bright * dim_factor

        return colors
            

if __name__ == "__main__":
    p = Pulser()
    p.pulse()
