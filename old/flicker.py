from functions import *
import random
import time

flicker_factor = 0.7
wait = 0.06


try:
    pixels = get_pixels()
    s = raw_input("Input RGB separated by space: ")
    while True:
        r, g, b = s.split()
        r = int(r)
        g = int(g)
        b = int(b)
        color = Adafruit_WS2801.RGB_to_color( r, g, b )
        set_pixel(pixels, color)
        for i in range(pixels.count()):
            if random.randint(0, 10) > 8:
                continue
            dim_factor = (1 - flicker_factor) + (random.random() * flicker_factor)

            dim(pixels, i, dim_factor)
        pixels.show()
        time.sleep(wait)

except KeyboardInterrupt:
    turn_off(pixels)