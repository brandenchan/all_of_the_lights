import Adafruit_WS2801
import time
import numpy as np

BRIGHT_WHITE = Adafruit_WS2801.RGB_to_color(255, 255, 255)

def get_pixels():
    # Configure the count of pixels:
    PIXEL_COUNT = 50

    # The WS2801 library makes use of the BCM pin numbering scheme. See the README.md for details.

    # Specify a software SPI connection for Raspberry Pi on the following pins:
    PIXEL_CLOCK = 18
    PIXEL_DOUT  = 23
    pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, clk=PIXEL_CLOCK, do=PIXEL_DOUT)
    return pixels

def wheel(pos, ret_rgb=False, saturation=100):
    desaturate = 255 - (saturation * 255.)
    if pos < 85:
        rgb = [pos * 3, 255 - pos * 3, 0]
    elif pos < 170:
        pos -= 85
        rgb = [255 - pos * 3, 0, pos * 3]
    else:
        pos -= 170
        rgb = [0, pos * 3, 255 - pos * 3]
    if ret_rgb:
        rgb = np.maximum(rgb, desaturate)
        return rgb
    return Adafruit_WS2801.RGB_to_color(*rgb)

def set_pixel(pixels, color, idx=None):
    if idx is None:
        for i in range(pixels.count()):
            pixels.set_pixel(i, color)
    else:
        pixels.set_pixel(idx, color)

def _dim_one(pixels, idx, factor, floor):
    r, g, b = pixels.get_pixel_rgb(idx)
    r = max(int(r * factor), floor)
    g = max(int(g * factor), floor)
    b = max(int(b * factor), floor)
    pixels.set_pixel(idx, Adafruit_WS2801.RGB_to_color( r, g, b ))

def dim(pixels, idx=None, factor=0.9, floor=0):
    if idx is None:
        for i in range(pixels.count()):
            _dim_one(pixels, i, factor, floor)
    else:
        _dim_one(pixels, idx, factor, floor)

def turn_off(pixels):
    pixels.clear()
    pixels.show()
    pixels.clear()
    pixels.show()
    pixels.clear()
    pixels.show()

def interp_color(rgb_1, rgb_2, phase_pos, phase):
    r = interp_one(rgb_1[0], rgb_2[0], phase_pos, phase)
    g = interp_one(rgb_1[1], rgb_2[1], phase_pos, phase)
    b = interp_one(rgb_1[2], rgb_2[2], phase_pos, phase)
    return (r,g,b)

def get_all_values(pixels):
    return np.asarray([pixels.get_pixel_rgb(i) for i in range(pixels.count()) ])

def set_all_values(pixels, array):
    for i, (r, g, b) in enumerate(array):
        pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color(int(r), int(g), int(b)))
        
def interp_one(c_1, c_2, phase_pos, phase):
    if phase:
        phase_pos = 1 - phase_pos
    return int((c_1 - c_2) * phase_pos + c_1)

def random_rgb():
    return (random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255))

def shift(rgb, warm_rgb, amount, boost=0.4):
    """ Applies the color ratio of warm_rgb to 
    rgb by the amount (0-100). Floor boosts
    how much shifting happens even when amount
    is low"""
    amount = min(amount * (1 + boost), 1.)
    retain = 1. - amount
    # retain = np.minimum(retain * (1 + boost), 1.)
    warm_rgb = np.asarray(warm_rgb)
    warm_ratio = warm_rgb / float(max(warm_rgb))
    gap = 1 - warm_ratio
    shift = warm_ratio + (gap * retain)
    return (rgb * shift).astype(int)


if __name__ == "__main__":
    pixels = get_pixels()
    set_pixel(pixels, BRIGHT_WHITE)
    pixels.show()
    time.sleep(5)
    pixels.clear()
    pixels.show()


