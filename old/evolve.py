from functions import *
import random

pixels = get_pixels()
n_pix = pixels.count()
step = 10

def can_increment(i, pixels, step, col_i):
    c = pixels.get_pixel_rgb(i)[col_i]
    if c + step > 255:
        return False
    return True

def can_decrement(i, pixels, step, col_i):
    c = pixels.get_pixel_rgb(i)[col_i]
    if c - step < 0:
        return False
    return True

def increment(i, pixels, col_i):
    rgb = list(pixels.get_pixel_rgb(i))
    c = rgb[col_i]
    c += step
    rgb[col_i] = c
    pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color(*rgb))

def decrement(i, pixels, col_i):
    rgb = list(pixels.get_pixel_rgb(i))
    c = rgb[col_i]
    c -= step
    rgb[col_i] = c
    pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color(*rgb))

try:
    pixels.clear()
    incr = np.full((n_pix, 3), True)
    set_all_values(pixels, np.full((n_pix, 3), 120))

    while True:
        for i in range(12):
            r = random.randint(0, n_pix - 1)
            c = random.randint(0, 2)
            rgb = pixels.get_pixel_rgb(r)
            diff = max(rgb) - min(rgb) + 1
            step = max(255 / diff, 5)
            
            if incr[r][c] == True:
                if can_increment(r, pixels, step, c):
                    increment(r, pixels, c)
                else:
                    incr[r][c] = False
                    decrement(r, pixels, c)
            elif incr[r][c] == False:
                if can_decrement(r, pixels, step, c):
                    decrement(r, pixels, c)
                else:
                    incr[r][c] = True
                    increment(r, pixels, c)
        pixels.show()
finally:
    turn_off(pixels)



