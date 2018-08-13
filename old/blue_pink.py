from functions import *
from colors import *
import time

BLUE_VAL = (0, 0, 255)
PINK_VAL = (255, 10, 70)

pixels = get_pixels()

pixels.clear()
pixels.show()
glob = 0
pix_i = 0
col_i = 0

def interpolate(start, end, num):
    diff = start - end
    step = float(diff) / num
    ret = [start + step * i for i in range(num)]
    return ret

def interpolate_color(start_rgb, end_rgb, num):
    r_list = interpolate(start_rgb[0], end_rgb[0], num)
    g_list = interpolate(start_rgb[1], end_rgb[1], num)
    b_list = interpolate(start_rgb[2], end_rgb[2], num)
    return list(zip(r_list, g_list, b_list))
    


try:
    colors_list = interpolate_color(BLUE_VAL, PINK_VAL, pixels.count())
    colors_list = [BLUE_VAL]
    for i in range(24):
        colors_list.append((0,0,0))
    colors_list.append(PINK_VAL)
    for i in range(24):
        colors_list.append((0,0,0))
    start_pix = 0
    while True:
        for i in range(pixels.count()):
            r, g, b = colors_list[i]
            color = Adafruit_WS2801.RGB_to_color(int(r), int(g), int(b))
            change_pix = (start_pix + i) % pixels.count()
            set_pixel(pixels, color, change_pix)
        pixels.show()
        start_pix += 1
        start_pix = start_pix % pixels.count()
        time.sleep(0.05)

except KeyboardInterrupt:
    turn_off(pixels)