""" Here are functions which either generate or
modify RGB color values """

import random
import numpy as np

def wheel(pos, ret_rgb=False, saturation=100):
    # NOTE: the ret_rgb argument is useless
    # Remove in future and remove all instances
    # in the rest of the code
    desaturate = 255 - (saturation * 255.)
    if pos < 85:
        rgb = [pos * 3, 255 - pos * 3, 0]
    elif pos < 170:
        pos -= 85
        rgb = [255 - pos * 3, 0, pos * 3]
    else:
        pos -= 170
        rgb = [0, pos * 3, 255 - pos * 3]
    if ret_rgb:
        rgb = np.maximum(rgb, desaturate)
        return rgb

def random_rgb():
    return (random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255))

def shift(rgb, warm_rgb, amount, boost=0.4):
    """ Applies the color ratio of warm_rgb to 
    rgb by the amount (0-100). Floor boosts
    how much shifting happens even when amount
    is low"""
    amount = min(amount * (1 + boost), 1.)
    retain = 1. - amount
    # retain = np.minimum(retain * (1 + boost), 1.)
    warm_rgb = np.asarray(warm_rgb)
    warm_ratio = warm_rgb / float(max(warm_rgb))
    gap = 1 - warm_ratio
    shift = warm_ratio + (gap * retain)
    return (rgb * shift).astype(int)