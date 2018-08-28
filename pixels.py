import Adafruit_WS2801
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

def turn_off(pixels):
    pixels.clear()
    pixels.show()
    pixels.clear()
    pixels.show()
    pixels.clear()
    pixels.show()

def get_all_values(pixels):
    return np.asarray([pixels.get_pixel_rgb(i) for i in range(pixels.count()) ])

def set_all_values(pixels, array):
    for i, (r, g, b) in enumerate(array):
        pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color(int(r), int(g), int(b)))



