from pixels import set_all_values, get_pixels, turn_off, get_all_values
import Adafruit_WS2801
import numpy as np
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--red", type=int, default=None,
                    help="Red channel value 0 - 255")
parser.add_argument("-g", "--green", type=int, default=None,
                    help="Green channel value 0 - 255")
parser.add_argument("-b", "--blue", type=int, default=None,
                    help="Blue channel value 0 - 255")
args = parser.parse_args()

N_PIXELS=50

try:
    pixels = get_pixels()
    past = get_all_values(pixels)
    zeros = np.count_nonzero(past)
    if zeros != 0:
        turn_off(pixels)
        sys.exit()
    r = args.red
    g = args.green
    b = args.blue
    array = np.stack([[int(r), int(g), int(b)]]*N_PIXELS)
    set_all_values(pixels, array)
    pixels.show()
    sys.exit()

except KeyboardInterrupt:
    turn_off(pixels)
