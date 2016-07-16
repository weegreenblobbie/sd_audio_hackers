'''
wave table generators
'''

import numpy as np


# local modules
from draw import get_n_samples


class Nearest(object):
    '''
    Returns samples from the wavetable without any interpolation.
    '''

    def __init__(self, sr, table):

        table = np.array(table).astype(np.float32)

        table = np.squeeze(table)

        assert len(table.shape) == 1, 'table must be a 1D array'

        # factor, if the table size != sr, the frequeny needs to be multiplied
        # by this.

        sr = np.float32(sr)

        factor = np.float32(len(table)) / sr

        # save into object

        self._factor = factor
        self._table = table
        self._sr = sr


    def generate(self, dur, freq, phase = None):
        '''
        gernerates a signal
        '''

        if phase is None:
            phase = lambda : 0

        assert callable(freq), "freq must be a callable object"
        assert callable(phase), "phase must be a callable object"

        n_samples = get_n_samples(self._sr, dur)

        out = np.zeros(n_samples, np.float32)

        pos = 0.0

        for i in range(n_samples):

            ph = (phase() * self._sr / 2.0) + 0.5
            pos2 = pos + self._factor * ph

            # range check

            sr = self._factor * self._sr

            while(pos2 >= sr):
                pos2 -= sr

            while(pos2 < 0):
                pos2 += sr

            sample = self._table[int(np.floor(pos2))]

            pos += self._factor * freq()

            out[i] = sample

        return out

