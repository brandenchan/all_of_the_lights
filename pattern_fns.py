import numpy as np
from functions import wheel

def pixel_train(phase, cache, kwargs):
    shape = kwargs["shape"]
    n_pix = shape[0]

    # Initialize cache
    if not cache:
        cache = {"rgb_values": np.zeros(shape),
                 "pix_idx": 0,
                 "wheel_color": 0
                 }

    rgb_values = cache["rgb_values"]
    pix_idx = cache["pix_idx"]
    wheel_color = cache["wheel_color"]

    step = 3
    dim_factor = 0.92

    # Update if moved to next pix
    curr_pix = int(n_pix * phase)
    if curr_pix != pix_idx:
        wheel_color = (wheel_color + step) % 255
        rgb = wheel(wheel_color, True)
        rgb_values = rgb_values * dim_factor
        rgb_values[curr_pix] = rgb

    # Save new values in cache
    cache["rgb_values"] = rgb_values
    cache["pix_idx"] = curr_pix
    cache["wheel_color"] = wheel_color
    return rgb_values, cache


def test_fn(self, phase, cache, kwargs):
    phase_rad = 2 * np.pi * phase
    
    r, g, b = self.rgb
    r *= (np.sin(phase_rad) + 1 ) / 2 / 10
    g *= (np.sin(phase_rad) + 1 ) / 2 / 10
    b *= (np.sin(phase_rad) + 1 ) / 2 / 10
    values = np.zeros(self.shape)
    values[:, 0] = r
    values[:, 1] = g
    values[:, 2] = b
    return values, cache