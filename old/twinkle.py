from functions import *
from colors import *
import Adafruit_WS2801
import random
import time
import numpy as np

pixels = get_pixels()
n_pixels = pixels.count()
phase = np.asarray([random.random() for i in range(n_pixels)])
rgb = WARM_CANDLE
color = Adafruit_WS2801.RGB_to_color(*rgb)

clock = 0.0
start = time.time()
cycle_time = 1000.


rainbow = True

try:
    counter = 0
    while True:
        if rainbow:
            for i in range(n_pixels):
                color_i = (i + int(counter)) % n_pixels
                color_idx = 255 / n_pixels * color_i
                curr_color = wheel(color_idx)
                pixels.set_pixel(i, curr_color)
        else:
            pixels.set_pixels(color)
        act_start = time.time()
        elapsed = (act_start - start) * 1000 / cycle_time
        phase_pos_shifted = phase + elapsed
        sin_phase = np.sin(phase_pos_shifted * 2 * np.pi)
        for i, pps in enumerate(sin_phase):
            dim(pixels, i, pps) 
        pixels.show()
        counter += 0.1
finally:
    turn_off(pixels)
    




