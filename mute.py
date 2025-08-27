""" Contains the light mute functions. Each function
takes (elapsed, kwargs) as arguments so that they
can be used interchangably within the Controller class. 
Each function returns a numpy array with the dimming factor
for each rgb value of each light. """

import numpy as np

DURATION = 5000

def instant(elapsed, kwargs):
    shape = kwargs["shape"]
    return np.zeros(shape)

def gradual(elapsed, kwargs, duration=DURATION):
    shape = kwargs["shape"]
    if elapsed > duration:
        return np.zeros(shape)
    factor = (duration - elapsed) / float(duration)
    return np.full(shape, factor)

def fade_out(elapsed, kwargs, duration=1000):
    """Fade out over specified duration (default 1 second)"""
    shape = kwargs["shape"]
    if elapsed > duration:
        return np.zeros(shape)
    factor = (duration - elapsed) / float(duration)
    return np.full(shape, factor)

def fade_in(elapsed, kwargs, duration=1000):
    """Fade in over specified duration (default 1 second)"""
    shape = kwargs["shape"]
    if elapsed > duration:
        return np.ones(shape)
    factor = elapsed / float(duration)
    return np.full(shape, factor)

def flicker(elapsed, kwargs, duration=DURATION):
    shape = kwargs["shape"]
    if elapsed > duration:
        return np.zeros(shape)
    factor = (duration - elapsed) / float(duration)
    return np.random.binomial(1, factor, shape) * factor


