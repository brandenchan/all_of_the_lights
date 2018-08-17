from pattern_fns import *
from mute_fns import *

SPACEBAR = 32
ENTER = 10
S_KEY = 115
A_KEY = 97
C_KEY = 99
D_KEY = 100
Q_KEY = 113
W_KEY = 119
E_KEY = 101
RIGHT = 261
LEFT = 260
UP = 259
DOWN = 258
MINUS_KEY = 45
PLUS_KEY = 61

# RGB Values for different colors

CANDLE = (255, 147, 41)
WARM_CANDLE = (255, 130, 30)
BLUE = (0, 0, 255)
PINK = (255, 10, 70)


PATTERN_FN_NAMES = {pulse: "Pulse",
                    pixel_train: "Pixel Train",
                    droplets: "Droplets"}

MUTE_FN_NAMES = {instant: "Instant",
                 gradual: "Gradual",
                 flicker: "Flicker"}