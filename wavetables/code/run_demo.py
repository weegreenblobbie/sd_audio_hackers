# 3rd party modules

import matplotlib.pyplot as plt
import numpy as np

# local modules

from callables import Constant
from callables import Circular

import draw

import wave_table_gen


def main():

    sr = 1000

    freq = Constant(3.0)
    phase = Constant(0.0)

    #--------------------------------------------------------------------------
    # drawn waveforms

    x = draw.sine(sr, 1.0, freq)

    plt.figure()
    plt.plot(x)
    plt.grid(True)
    plt.title('Sine wave: f = %d Hz' % freq())

    f_3_10 = draw.line(sr, 1.0, 3, 10)

    x = draw.sine(sr, 1.0, Circular(f_3_10))

    plt.figure()
    plt.plot(x)
    plt.grid(True)
    plt.title('Sine wave: f = 3-10 Hz')

    #--------------------------------------------------------------------------
    # wave table gen Nearest

    # create a 3 tables each holding 1 cycle

    _1_hz = Constant(1.0)

    table_1000 = draw.sine(1000, 1000, _1_hz)
    table_500  = draw.sine( 500,  500, _1_hz)
    table_250  = draw.sine( 250,  250, _1_hz)

    gen_1000 = wave_table_gen.Nearest(1000, table_1000)
    gen_500  = wave_table_gen.Nearest(1000, table_500)
    gen_250  = wave_table_gen.Nearest(1000, table_250)

    dur = 1.0

    x0 = gen_1000.generate(dur, Circular(f_3_10))
    x1 = gen_500.generate(dur,  Circular(f_3_10))
    x2 = gen_250.generate(dur,  Circular(f_3_10))

    plt.figure()
    plt.plot(x0, 'b-', label = 'wt 1000')
    plt.plot(x1, 'r-', label = 'wt 500')
    plt.plot(x2, 'm-', label = 'wt 250')
    plt.title('wave_table_gen.Neartest signals')
    plt.grid(True)
    plt.legend()

    # round off error residuals

    # res_500 = np.abs(x1 - x0)
    # res_250 = np.abs(x2 - x0)

    res_500 = x1 - x0
    res_250 = x2 - x0

    plt.figure()
    plt.plot(res_500, label = 'wt 500 error')
    plt.plot(res_250, label = 'wt 250 error')
    plt.title('wave_table_gen.Nearest residual error')
    plt.grid(True)
    plt.legend()

    #--------------------------------------------------------------------------
    # wave table gen Lininterp

    gen_1000 = wave_table_gen.Lininterp(1000, table_1000)
    gen_500  = wave_table_gen.Lininterp(1000, table_500)
    gen_250  = wave_table_gen.Lininterp(1000, table_250)

    x0 = gen_1000.generate(dur, Circular(f_3_10))
    x1 = gen_500.generate(dur,  Circular(f_3_10))
    x2 = gen_250.generate(dur,  Circular(f_3_10))

    plt.figure()
    plt.plot(x0, 'b-', label = 'wt 1000')
    plt.plot(x1, 'r-', label = 'wt 500')
    plt.plot(x2, 'm-', label = 'wt 250')
    plt.title('wave_table_gen.Lininterp signals')
    plt.grid(True)
    plt.legend()

    # round off error residuals

    # res_500 = np.abs(x1 - x0)
    # res_250 = np.abs(x2 - x0)

    res_500 = x1 - x0
    res_250 = x2 - x0

    plt.figure()
    plt.plot(res_500, label = 'wt 500 error')
    plt.plot(res_250, label = 'wt 250 error')
    plt.title('wave_table_gen.Lininterp residual error')
    plt.grid(True)
    plt.legend()


    plt.show()


if __name__ == "__main__":
    main()
