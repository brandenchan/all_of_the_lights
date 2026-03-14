""" Contains functions which handle the interface to
the WS2801 LED lights """

import Adafruit_WS2801
import numpy as np

BRIGHT_WHITE = Adafruit_WS2801.RGB_to_color(255, 255, 255)

# Software SPI pins (BCM numbering)
SPI_CLK = 25   # GPIO 25 (physical pin 22)
SPI_DO = 18    # GPIO 18 (physical pin 12)

def get_pixels():
    PIXEL_COUNT = 50
    pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, clk=SPI_CLK, do=SPI_DO)
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
