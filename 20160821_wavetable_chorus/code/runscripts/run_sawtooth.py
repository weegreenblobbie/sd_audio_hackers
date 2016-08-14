
import matplotlib.pyplot as plt


from sdaudio.callables import Circular
from sdaudio.callables import Constant
from sdaudio import draw
from sdaudio import wavio
from sdaudio.wt_oscillators import Choruses


def main():

    #-------------------------------------------------------------------------
    # sawtooth demo

    sr = 8000
    dur = 5.0

    freqs = draw.line(sr, dur, 220, 440)

    x = draw.sawtooth(sr, dur, Circular(freqs), n = 5)

    plt.figure()
    plt.plot(x)
    plt.xlim([0, 3000])
    plt.grid(True)
    plt.title('Sawtooth, n = 5, no chorus')

    fout = 'saw-no-chorus.wav'

    wavio.write(fout, 0.666 * x, sr)

    print("Wrote: %s" % fout)

    #-------------------------------------------------------------------------
    # sawtooth oscillator with chorus

    table = draw.sawtooth(sr, 1.0, Constant(1.0))

    chorus = [0.98, 0.99, 1.0, 1.03]

    gen = Choruses(sr, table, chorus)

    x = gen.generate(dur, Circular(freqs))

    plt.figure()
    plt.plot(x)
    plt.xlim([0, 3000])
    plt.grid(True)
    plt.title('Sawtooth, n = 5, with chorus')

    fout = 'saw-with-chorus.wav'

    wavio.write(fout, 0.666 * x, sr)

    print("Wrote: %s" % fout)


    plt.show()




if __name__ == "__main__":
    main()