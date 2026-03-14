""" Contains functions which handle the interface to
the WS2801 LED lights """

import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI
import numpy as np

BRIGHT_WHITE = Adafruit_WS2801.RGB_to_color(255, 255, 255)

def get_pixels():
    # Configure the count of pixels:
    PIXEL_COUNT = 50

    # Use hardware SPI (device 0, chip select CE0)
    # This is much more reliable than software SPI — no timing glitches
    SPI_PORT = 0
    SPI_DEVICE = 0
    pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

    # Lower the SPI clock speed for better signal integrity over jumper wires
    # Default can be too fast and cause occasional data corruption
    try:
        pixels._spi._spi.max_speed_hz = 1000000  # 1 MHz
    except Exception:
        pass  # If we can't set it, use the default

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
