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

def flicker(elapsed, kwargs, duration=DURATION):
    shape = kwargs["shape"]
    if elapsed > duration:
        return np.zeros(shape)
    factor = (duration - elapsed) / float(duration)
    return np.random.binomial(1, factor, shape) * factor


