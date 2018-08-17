import numpy as np
from pixel_fns import wheel, shift
import random
from phase import modify_phase
import time

def pixel_train(phase, cache, kwargs):

    step = 2.5
    dim_factor = 0.92

    shape = kwargs["shape"]
    n_pix = shape[0]
    n_cycles = kwargs["n_cycles"]
    saturation = kwargs["saturation"]
    warm_shift = kwargs["warm_shift"]
    warm_rgb = kwargs["warm_rgb"]
    alt = kwargs["alt"]

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
    if alt:
        curr_pix = n_pix - curr_pix - 1
    if curr_pix != pix_idx:
        wheel_color = int((wheel_color + step) % 255)
        rgb = wheel(wheel_color, True, saturation)
        rgb_values = rgb_values * dim_factor
        if warm_shift:
            rgb = shift(rgb, warm_rgb, 1. - saturation)
        rgb_values[curr_pix] = rgb


    # Save new values in cache
    cache["rgb_values"] = rgb_values
    cache["pix_idx"] = curr_pix
    cache["wheel_color"] = wheel_color
    return rgb_values, cache


def pulse(phase, cache, kwargs):

    floor = 0.2

    warm_shift = kwargs["warm_shift"]
    warm_rgb = kwargs["warm_rgb"]
    shape = kwargs["shape"]
    saturation = kwargs["saturation"]
    n_pix = shape[0]
    alt = kwargs["alt"]

    # Initialize new cache
    if cache.get("mode") != "pulse":
        cache = {"mode": "pulse",
                 "wheel_idx": 0,
                 "old_alt": alt}
        if alt:
            cache["offset"] = np.random.randn(n_pix)
        else:
            cache["offset"] = np.zeros(n_pix)


    wheel_idx = (cache["wheel_idx"] + 1) % 256
    old_alt = cache["old_alt"]
    if alt != old_alt:
        if alt:
            cache["offset"] = np.random.randn(n_pix)
        else:
            cache["offset"] = np.zeros(n_pix)

    offset = cache["offset"]


    # Phase in radians, shifted so it
    # starts at the peak
    phase_rad = 2 * np.pi * np.expand_dims(offset + phase, 1)
    phase_rad += 0.5 * np.pi

    sin_phase = np.sin(phase_rad)
    sin_squashed = (sin_phase + 1) / 2
    sin_floored = floor + ((1-floor) * sin_squashed)

    rgb = wheel(wheel_idx, True, saturation)
    if warm_shift:
        rgb = shift(rgb, warm_rgb, 1. - saturation)
    rgb_values = np.zeros(shape)
    rgb_values[:] = rgb
    rgb_values = rgb_values * sin_floored

    cache["wheel_idx"] = wheel_idx
    cache["old_alt"] = alt

    return rgb_values, cache

def droplets(phase, cache, kwargs):

    shifted = True
    radius = 24

    # Get var from kwargs
    curr_cycle = kwargs["n_cycles"]
    shape = kwargs["shape"]
    n_pix = shape[0]
    saturation = kwargs["saturation"]
    warm_shift = kwargs["warm_shift"]
    warm_rgb = kwargs["warm_rgb"]
    alt = kwargs["alt"]


    # Initialize new cache
    if cache.get("mode") != "droplets":
        cache = {"mode": "droplets",
                 "last_cycle":0,
                 "center_pix": random.randint(radius, n_pix - radius - 1),
                 "rgb": wheel(random.randint(0, 255), True, saturation),
                 "last_phase":0.}

    center_pix = cache["center_pix"]
    last_cycle = cache["last_cycle"]
    last_phase = cache["last_phase"]
    rgb = cache["rgb"]

    rgb_values = np.zeros(shape)

    # So that drops are biggest at beginning of phase
    phase = (phase + 0.5) % 1

    # In alt mode, color changes when droplet is at largest
    if alt:     
        change_threshold = 0.5   
        if last_phase < change_threshold and phase > change_threshold:
            rgb = wheel(random.randint(0, 255), True, saturation)

    # In regular mode, color changes when droplet is at smallest
    else:
        leap = 0.9
        if abs(last_phase - phase) > 0.9:
            rgb = wheel(random.randint(0, 255), True, saturation)

    if curr_cycle != last_cycle:
        center_pix = random.randint(radius, n_pix - radius - 1)

    drop_shape = calculate_drop(phase, radius)
    d_start = center_pix - radius
    d_end = center_pix + radius
    if warm_shift:
        final_rgb = shift(rgb, warm_rgb, 1. - saturation)
    else:
        final_rgb = rgb
    rgb_values[d_start: d_end + 1] = final_rgb
    rgb_values[d_start: d_end + 1] = rgb_values[d_start: d_end + 1] * drop_shape

    cache["rgb"] = rgb
    cache["last_cycle"] = curr_cycle
    cache["last_phase"] = phase
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




def orbits(phase, cache, kwargs):

    dim_factor = 0.8
    margin = 70
    
    shape = kwargs["shape"]
    n_pix = shape[0]
    n_cycles = kwargs["n_cycles"]
    saturation = kwargs["saturation"]
    warm_shift = kwargs["warm_shift"]
    warm_rgb = kwargs["warm_rgb"]
    alt = kwargs["alt"]

    # Initialize new cache
    if cache.get("mode") != "orbits":
        cache = {"mode":"orbits",
                 "rgb_values": np.zeros(shape),
                 "pix_1": n_pix / 2
                 }
        color_1_int = random.randint(0, 255)
        color_2_int = random.randint(0, 255)
        while abs(color_1_int - color_2_int) < margin:
            color_2_int = random.randint(0, 255)
        cache["color_1"] = wheel(color_1_int, True)
        cache["color_2"] = wheel(color_2_int, True)

    rgb_values = cache["rgb_values"]
    pix_1 = cache["pix_1"]
    color_1 = cache["color_1"]
    color_2 = cache["color_2"]

    desaturate = 255 - (saturation * 255.)
    color_1_sat = np.maximum(color_1, desaturate)
    color_2_sat = np.maximum(color_2, desaturate)

    # Update if moved to next pix
    curr_pix_1 = int(n_pix * phase) + (n_pix / 2)
    curr_pix_1 = curr_pix_1 % n_pix
    if not alt:
        curr_pix_2 = n_pix - curr_pix_1 - 1
    else: 
        curr_pix_2 = (curr_pix_1 + (n_pix / 2)) % n_pix

    if curr_pix_1 != pix_1:
        # Update pix_1
        rgb_1 = color_1_sat
        if warm_shift:
            rgb_1 = shift(rgb_1, warm_rgb, 1. - saturation)
        rgb_values[curr_pix_1] = rgb_1

        # Update pix_2
        rgb_2 = color_2_sat
        if warm_shift:
            rgb_2 = shift(rgb_2, warm_rgb, 1. - saturation)
        rgb_values[curr_pix_2] = rgb_2

        rgb_values = rgb_values * dim_factor

    # Save new values in cache
    cache["rgb_values"] = rgb_values
    cache["pix_1"] = curr_pix_1
    cache["color_1"] = color_1
    cache["color_2"] = color_2

    return rgb_values, cache

def sparks(phase, cache, kwargs):

    active_fraction = 0.5
    wait_factor = 0.4

    shape = kwargs["shape"]
    n_pix = shape[0]
    n_cycles = kwargs["n_cycles"]
    saturation = kwargs["saturation"]
    warm_shift = kwargs["warm_shift"]
    warm_rgb = kwargs["warm_rgb"]
    loop_start = kwargs["loop_start"]

    # Initialize new cache
    if cache.get("mode") != "sparks":
        cache = {"mode":"sparks",
                 "wait": None,
                 "wait_start": None}

    wait = cache["wait"]
    wait_start = cache["wait_start"]

    rgb_values = np.zeros(shape)
    desaturate = 255 - (saturation * 255.)

    # If in wait mode
    if wait is not None and wait_start is not None:
        elapsed = (loop_start - wait_start) * 1000
        if elapsed < wait:
            return rgb_values, cache
    else:
        wait = None
        wait_start = None

    n_choices = int(n_pix * active_fraction)
    for i in range(n_choices):
        dim = random.random()
        curr_rgb = wheel(random.randint(0, 255), True, saturation)
        if warm_shift:
            curr_rgb = shift(curr_rgb, warm_rgb, 1. - saturation)
        rgb_values[random.randint(0, n_pix-1)] = curr_rgb

    wait_start = time.time()
    wait = random.random() * wait_factor * 1000

    cache["wait"] = wait
    cache["wait_start"] = wait_start

    return rgb_values, cache







