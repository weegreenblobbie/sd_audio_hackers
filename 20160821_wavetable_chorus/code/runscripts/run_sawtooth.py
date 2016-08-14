
import matplotlib.pyplot as plt


from sdaudio.callables import Circular
from sdaudio.callables import Constant
from sdaudio import draw
from sdaudio import wavio
from sdaudio.wt_oscillators import Choruses


def main():

    #-------------------------------------------------------------------------
    # sawtooth demo

    print("Generating 60 Hz sawtooth, no chorus")

    sr = 8000
    dur = 7.0

    freqs = draw.line(sr, dur, 60, 60)

    x = draw.sawtooth(sr, dur, Circular(freqs), n = 5)

    plt.figure()
    plt.plot(x)
    plt.xlim([0, 3000])
    plt.grid(True)
    plt.title('Sawtooth, n = 5, no chorus')

    fout = 'saw-no-chorus.wav'

    print("Writing: %s" % fout)

    wavio.write(fout, 0.666 * x, sr)

    #-------------------------------------------------------------------------
    # sawtooth oscillator with chorus

    print("Generating 60 Hz sawtooth, with chorus")

    table = draw.sawtooth(sr, 1.0, Constant(1.0))

    chorus = [0.99, 1.0, 1.01]

    chorus = [0.97, 1.0, 1.03]

    chorus = [0.991234134, 1.012983475290375]

    gen = Choruses(sr, table, chorus)

    x = gen.generate(dur, Circular(freqs))

    plt.figure()
    plt.plot(x)
    plt.xlim([0, 3000])
    plt.grid(True)
    plt.title('Sawtooth, n = 5, with chorus')

    fout = 'saw-with-chorus.wav'

    print("Writing: %s" % fout)

    wavio.write(fout, 0.666 * x, sr)

    #-------------------------------------------------------------------------
    # freq ramp

    print("Generating sawtooth ramp, no chorus")

    freqs = draw.line(sr, dur, 40, 200)

    x = draw.sawtooth(sr, dur, Circular(freqs))

    fout = 'saw-ramp-no-chorus.wav'

    print("Writing: %s" % fout)

    wavio.write(fout, 0.666 * x, sr)

    print("Generating sawtooth ramp, with chorus")

    x = gen.generate(dur, Circular(freqs))

    fout = 'saw-ramp-with-chorus.wav'

    print("Writing: %s" % fout)

    wavio.write(fout, 0.666 * x, sr)

    plt.show()




if __name__ == "__main__":
    main()