from functions import *
import random
import Adafruit_WS2801
import time

pixels = get_pixels()
n_pixels = pixels.count()
rainbow = False

while True:
    try:
        rand_pix = random.randint(0, n_pixels - 1) / 2
        for i in range(rand_pix):
            rand = random.randint(0, n_pixels - 1)
            if not rainbow:
                dim = random.random()

                r = int(random.randint(0, 255) * dim)
                g = int(random.randint(0, 255) * dim)
                b = int(random.randint(0, 255) * dim)
                pixels.set_pixel(rand, Adafruit_WS2801.RGB_to_color(r, g, b))
            else:
                color = wheel(random.randint(0,255))
                pixels.set_pixel(rand, color)

        wait = random.random() / 2.5
        time.sleep(wait)

        pixels.show()
    finally:
        turn_off(pixels)