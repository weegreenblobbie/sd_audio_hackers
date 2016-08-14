# 3rd party modules

import matplotlib.pyplot as plt
import numpy as np

# local modules

from callables import Constant
from callables import Circular

import draw

import wt_oscillators


def main():

    sr = 1000
    dur = 1.0

    #--------------------------------------------------------------------------
    # drawn waveforms

    _3_hz = Constant(3)

    x = draw.sine(sr, dur, _3_hz)

    plt.figure()
    plt.plot(x)
    plt.grid(True)
    plt.title('Sine wave: f = %d Hz' % _3_hz())

    x = draw.sine(sr, dur, _3_hz, Constant(0.5))

    plt.figure()
    plt.plot(x)
    plt.grid(True)
    plt.title('Cosine wave: f = %d Hz' % _3_hz())

    f_3_10 = Circular(draw.line(sr, dur, 3, 10))

    x = draw.sine(sr, dur, f_3_10)

    plt.figure()
    plt.plot(x)
    plt.grid(True)
    plt.title('Sine wave: f = 3-10 Hz')

    phase = Circular(draw.line(sr, dur, 0.0, 1.0))

    x = draw.sine(sr, dur, _3_hz, phase)

    plt.figure()
    plt.plot(x)
    plt.grid(True)
    plt.title('Sine wave: f = 3, phase = 0 - 180 deg')

    plt.show()

    #--------------------------------------------------------------------------
    # wave table gen Nearest

    # create a 3 tables each holding 1 cycle

    _1_hz = Constant(1.0)

    table_1000 = draw.sine(1000, 1000, _1_hz)
    table_500  = draw.sine( 500,  500, _1_hz)
    table_250  = draw.sine( 250,  250, _1_hz)

    gen_1000 = wt_oscillators.Nearest(sr, table_1000)
    gen_500  = wt_oscillators.Nearest(sr, table_500)
    gen_250  = wt_oscillators.Nearest(sr, table_250)

    dur = 1.0

    x0 = gen_1000.generate(dur, f_3_10)
    x1 = gen_500.generate(dur,  f_3_10)
    x2 = gen_250.generate(dur,  f_3_10)

    plt.figure()
    plt.plot(x0, 'b-', label = 'wt 1000')
    plt.plot(x1, 'r-', label = 'wt 500')
    plt.plot(x2, 'm-', label = 'wt 250')
    plt.title('wt_oscillators.Neartest signals')
    plt.grid(True)
    plt.legend()

    # round off error residuals

    res_500 = x1 - x0
    res_250 = x2 - x0

    plt.figure()
    plt.plot(res_500, label = 'wt 500 error')
    plt.plot(res_250, label = 'wt 250 error')
    plt.title('wt_oscillators.Nearest residual error')
    plt.grid(True)
    plt.legend()

    plt.show()

    #--------------------------------------------------------------------------
    # wave table gen Lininterp

    gen_1000 = wt_oscillators.Lininterp(sr, table_1000)
    gen_500  = wt_oscillators.Lininterp(sr, table_500)
    gen_250  = wt_oscillators.Lininterp(sr, table_250)

    x0 = gen_1000.generate(dur, f_3_10)
    x1 = gen_500.generate(dur,  f_3_10)
    x2 = gen_250.generate(dur,  f_3_10)

    plt.figure()
    plt.plot(x0, 'b-', label = 'wt 1000')
    plt.plot(x1, 'r-', label = 'wt 500')
    plt.plot(x2, 'm-', label = 'wt 250')
    plt.title('wt_oscillators.Lininterp signals')
    plt.grid(True)
    plt.legend()

    # round off error residuals

    res_500 = x1 - x0
    res_250 = x2 - x0

    plt.figure()
    plt.plot(res_500, label = 'wt 500 error')
    plt.plot(res_250, label = 'wt 250 error')
    plt.title('wt_oscillators.Lininterp residual error')
    plt.grid(True)
    plt.legend()

    plt.show()

    #--------------------------------------------------------------------------
    # draw with phase

    phase = Circular(draw.line(sr, 1.0, 0.0, 1.0))

    _3_hz = Constant(3.0)

    x0 = draw.sine(sr, dur, _3_hz, phase)
    x1 = gen_250.generate(dur, _3_hz, phase)

    plt.figure()
    plt.plot(x0, label = 'drawn')
    plt.plot(x1, label = 'wt 250 interp')
    plt.title('3 Hz sine with 180 deg phase change')
    plt.grid(True)
    plt.legend()

    res = x1 - x0

    plt.figure()
    plt.plot(res, label = 'wt 250 interp error')
    plt.title('Residual error with 180 deg phase change')
    plt.grid(True)
    plt.legend()

    plt.show()


if __name__ == "__main__":
    main()
