""" Functions in this file deal with the tricky math of 
trying to slow down or speed up the phase of functions.
While phase values change, n_cycles remains unaffected """

def modify_phase(phase, n_cycles, speed_factor):
    if speed_factor > 1:
        return speed_phase(phase, n_cycles, speed_factor)
    elif speed_factor < 1:
        slow_factor = 1. / speed_factor
        return slow_phase(phase, n_cycles, slow_factor)
    else:
        return phase, n_cycles % 2

def speed_phase(phase, n_cycles, factor):
    # Phase is broken up into different segments 
    # which represent each sped up phase
    fraction = 1. / factor
    sped_phase = phase % fraction / fraction
    direction = phase // fraction % 2
    return sped_phase, direction

def slow_phase(phase, n_cycles, factor):
    fraction = 1. / factor
    slowed_phase = (phase * fraction) + (n_cycles % factor * fraction)
    direction = n_cycles // factor % 2
    return slowed_phase, direction

def calculate_phase(elapsed, cycle_time):
    phase = elapsed % cycle_time / cycle_time
    n_cycles = elapsed // cycle_time
    return phase, n_cycles