from pixels import set_all_values, get_pixels, turn_off, get_all_values
import Adafruit_WS2801
import numpy as np
import argparse
import sys

STATE_FILE = "/home/pi/all_of_the_lights/state"

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--red", type=int, default=255,
                    help="Red channel value 0 - 255")
parser.add_argument("-g", "--green", type=int, default=130,
                    help="Green channel value 0 - 255")
parser.add_argument("-b", "--blue", type=int, default=30,
                    help="Blue channel value 0 - 255")
args = parser.parse_args()

N_PIXELS=50

try:

    try:
    	state = open(STATE_FILE).readline()
    except IOError:
	open(STATE_FILE, "w").write("ON")
	state = "ON" 

    pixels = get_pixels()

    if state == "ON":
	state = "OFF"
	turn_off(pixels)

    elif state == "OFF":
	state = "ON"
        r = args.red
        g = args.green
        b = args.blue
        array = np.stack([[int(r), int(g), int(b)]]*N_PIXELS)
        set_all_values(pixels, array)
        pixels.show()

    open(STATE_FILE, "w").write(state)

except KeyboardInterrupt:
    turn_off(pixels)
