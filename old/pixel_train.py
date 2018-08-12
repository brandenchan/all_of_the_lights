#!/usr/bin/env python


# TO DO: CURSES KEY CONTROL SO IT CAN FLIP DIRECTION


from functions import *
import argparse
import numpy as np
import random

parser = argparse.ArgumentParser(description='Pixel are sequentially updated. Dimming happens constantly')
parser.add_argument('--wait', type=float, default=0.01,
                    help='Time between each pixel update')
parser.add_argument("--step", type=float, default=3,
                    help="Step size around a 256 step color wheel")
parser.add_argument('--dim_factor', type=float, default=0.92, 
                    help='What factor of current brightness is maintained after udpate')
parser.add_argument('--dim_random', type=float, default=0.0, 
                    help='Amount that dim factor can vary by each step')
parser.add_argument("--warm_up", type=int, default=0,
                    help="Number of steps until reaching full brightness")
args = parser.parse_args()

wait = args.wait
step = args.step
dim_factor = args.dim_factor
warm_up = args.warm_up
dim_random = args.dim_random

pixels = get_pixels()
pixels.clear()
pixels.show()
glob = 0
pix_i = 0
col = 0
try:
    while True:
        col += step
        pix_i += 1
        glob += 1
        col_i = int(col % 255)
        pix_i = pix_i % pixels.count()
        if dim_random:
            randomness = random.uniform(-dim_random, dim_random)
            curr_dim = dim_factor + randomness
        else:
            curr_dim = dim_factor
        dim(pixels, factor=curr_dim)
        color = wheel(col_i)
        set_pixel(pixels, color, pix_i)
        if wait > 0:
            time.sleep(wait)

        if glob < warm_up:
            warm_factor = np.exp2(glob / float(warm_up)) - 1

            saved = [pixels.get_pixel_rgb(i) for i in range(pixels.count())]
            dim(pixels, factor=warm_factor)
            pixels.show()
            for i in range(pixels.count()):
                r, g, b = saved[i]
                pixels.set_pixel_rgb(i, r, g, b)
        else:
            pixels.show()

except KeyboardInterrupt:
    print("Done!")
    turn_off(pixels)