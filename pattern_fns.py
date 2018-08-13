import numpy as np
from pixel_fns import wheel
import random
from phase import modify_phase

def pixel_train(phase, cache, kwargs):
    ### ADD FUNCTION SO IT CAN FLIP?

    step = 2.5
    dim_factor = 0.92
    desaturate = 0

    shape = kwargs["shape"]
    n_pix = shape[0]
    n_cycles = kwargs["n_cycles"]
    saturation = kwargs["saturation"]
    desaturate = 255 - (saturation * 255.)

    # Initialize new cache
    if cache.get("mode") != "pixel_train":
        cache = {"mode":"pixel_train",
                 "rgb_values": np.zeros(shape),
                 "pix_idx": 0,
                 "wheel_color": 0
                 }

    rgb_values = cache["rgb_values"]
    pix_idx = cache["pix_idx"]
    wheel_color = cache["wheel_color"]

 
    # Works best at slower speeds
    phase, direction = modify_phase(phase, n_cycles, 2)

    # Update if moved to next pix
    curr_pix = int(n_pix * phase)
    if curr_pix != pix_idx:
        wheel_color = int((wheel_color + step) % 255)
        rgb = wheel(wheel_color, True)
        rgb_values = rgb_values * dim_factor
        rgb_values[curr_pix] = rgb
        rgb_values[curr_pix] = np.maximum(rgb_values[curr_pix], desaturate)

    # Save new values in cache
    cache["rgb_values"] = rgb_values
    cache["pix_idx"] = curr_pix
    cache["wheel_color"] = wheel_color
    return rgb_values, cache


def pulse(phase, cache, kwargs):

    floor = 0.2

    # Initialize new cache
    if cache.get("mode") != "pulse":
        cache = {"mode": "pulse"}

    start = "high"

    rgb = kwargs["rgb"]
    shape = kwargs["shape"]
    phase_rad = 2 * np.pi * phase
    if start == "low":
        phase_rad -= 0.5 * np.pi
    elif start == "high":
        phase_rad += 0.5 * np.pi
    r, g, b = rgb
    sin_phase = np.sin(phase_rad)
    sin_squashed = (sin_phase + 1) / 2
    sin_floored = floor + ((1-floor) * sin_squashed)
    r *= sin_floored
    g *= sin_floored
    b *= sin_floored
    values = np.zeros(shape)
    values[:, 0] = r
    values[:, 1] = g
    values[:, 2] = b
    return values, cache

def droplets(phase, cache, kwargs):

    shifted = True
    radius = 24
    palette = "rainbow"

    # Get var from kwargs
    curr_cycle = kwargs.get("n_cycles")
    shape = kwargs.get("shape")
    n_pix = shape[0]
    saturation = kwargs.get("saturation")
    desaturation = 255 - (saturation * 255.)

    # Initialize new cache
    if cache.get("mode") != "droplets":
        cache = {"mode": "droplets",
                 "last_cycle": 0,
                 "center_pix": random.randint(radius, n_pix - radius - 1)}
        if palette == "rainbow":
            cache["rgb"] = wheel(random.randint(0, 255), True, desaturation)
            
        elif palette == "random":
            cache["rgb"] = random_rgb()
    center_pix = cache.get("center_pix")
    last_cycle = cache.get("last_cycle")
    rgb = cache.get("rgb")

    rgb_values = np.zeros(shape)
    if curr_cycle != last_cycle:
        rgb = wheel(random.randint(0, 255), True, desaturation)
        center_pix = random.randint(radius, n_pix - radius - 1)

    # So that drops are biggest at beginning of phase
    if shifted:
        phase = (phase + 0.5) % 1
    drop_shape = calculate_drop(phase, radius)
    d_start = center_pix - radius
    d_end = center_pix + radius
    rgb_values[d_start: d_end + 1] = rgb
    rgb_values[d_start: d_end + 1] = rgb_values[d_start: d_end + 1] * drop_shape

    cache["rgb"] = rgb
    cache["last_cycle"] = curr_cycle
    cache["center_pix"] = center_pix

    return rgb_values, cache

def calculate_drop(phase, radius, transform="linear"):
    if transform == "sin":
        phase_rads = phase * 2 * np.pi
        phase_rads -= (np.pi / 4)         # so that pixels start off
        phase = (np.sin(phase_rads) + 1) / 2
    elif transform == "linear":
        phase = -np.abs(phase * 2 - 1) + 1
    diam = 2 * radius + 1
    pixels_offset = -np.abs(np.linspace(1, -1,  2 * radius + 1))
    pixels_phased = np.maximum(pixels_offset + phase, 0)

    return np.expand_dims(pixels_phased, 1)
