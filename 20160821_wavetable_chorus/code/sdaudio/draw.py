"""
drawing tools
"""

import numpy as np


from sdaudio import assert_py3


def line(sr, dur, v0, v1):
    '''
    draws a linear line from v0 to v1 over duration samples

    sr = sample rate
    dur = float (duration in seconds), int (duration in samples)
    v0 = constant, start value
    v1 = constant, end value
    '''

    n_samples = get_n_samples(sr, dur)

    return np.linspace(v0, v1, n_samples).astype(np.float32)


def sine(sr, dur, freq, phase = None):
    '''

    draws a sine wave

    sr = sample rate
    sur = float (duration in secodns), int (duration in samples)
    freq = callable, returns frequency in Hz
    phase = callable, returns phase offset in unites of pi:
        0 = no offset
        0.5 = 0.5 * pi = 90 degrees
        1.0 = pi = 180 degrees
    '''

    if phase is None:
        phase = lambda : 0

    assert callable(freq), "freq must be a callable object"
    assert callable(phase), "phase must be a callable object"

    n_samples = get_n_samples(sr, dur)

    tau = 1.0 / sr

    t = 0.0

    out = np.zeros(n_samples, np.float32)

    for i in range(n_samples):

        out[i] = np.sin(2 * np.pi * t * tau + np.pi * phase())

        t += freq()

    return out


#------------------------------------------------------------------------------
# utils


def get_n_samples(sr, dur):

    assert sr > 0, "sr <= 0"
    assert dur > 0, "dur <= 0"

    if type(dur) in [int, np.int32, np.int64]:
        return dur

    return int(np.round(dur * sr))

