# 3rd party modules

import matplotlib.pyplot as plt


# local modules

from callables import Constant
from callables import Circular

import draw



def main():

    sr = 1000

    freq = Constant(3.0)
    phase = Constant(0.0)

    x = draw.sine(sr, 1.0, freq)

    plt.figure()
    plt.plot(x)
    plt.grid(True)
    plt.title('Sine wave: f = %d Hz' % freq())

    f = draw.line(sr, 1.0, 3, 10)

    x = draw.sine(sr, 1.0, Circular(f))

    plt.figure()
    plt.plot(x)
    plt.grid(True)
    plt.title('Sine wave: f = 3-10 Hz')

    plt.show()


if __name__ == "__main__":
    main()
