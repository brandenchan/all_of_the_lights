from functions import *
from colors import *
import Adafruit_WS2801
import random
import time
import numpy as np


def calculate_drop(phase, radius, transform="sin"):
    # phase is in range 0. - 1.
    if transform == "sin":
        phase_rads = phase * 2 * np.pi
        phase_rads -= (np.pi / 4)         # so that pixels start off
        phase = (np.sin(phase_rads) + 1) / 2
        phase = max(phase, 0)
    elif transform == "linear":
        phase = -np.abs(phase * 2 - 1) + 1
    diam = 2 * radius + 1
    pixels_offset = -np.abs(np.linspace(1, -1,  2 * radius + 1))
    pixels_phased = np.maximum(pixels_offset + phase, 0)

    return np.expand_dims(pixels_phased, 1)


def droplets(rgb=WARM_CANDLE,
             cycle_time=2000,
             radius=24,
             color_scheme="random"):
    pixels = get_pixels()
    n_pix = pixels.count()
    start = time.time()
    cycle = 0
    center_pix = random.randint(radius, n_pix - radius - 1)

    try:
        while True:
            now = time.time()
            elapsed = (now - start) * 1000
            phase, n_cycles = calculate_phase(elapsed, cycle_time)
            if cycle != n_cycles:
                cycle = n_cycles
                center_pix = random.randint(radius, n_pix - radius - 1)
                if color_scheme == "rainbow":
                    rgb = wheel(random.randint(0, 255), True)
                elif color_scheme == "random":
                    rgb = (random.randint(20, 255),
                            random.randint(20, 255),
                            random.randint(20, 255))
            drop_shape = calculate_drop(phase, radius)
            values = np.zeros((n_pix, 3))
            d_start = center_pix - radius
            d_end = center_pix + radius
            values[d_start: d_end + 1] = rgb
            values[d_start: d_end + 1] = values[d_start: d_end + 1] * drop_shape
            set_all_values(pixels, values)
            pixels.show()
    finally:
        turn_off(pixels)


droplets()


