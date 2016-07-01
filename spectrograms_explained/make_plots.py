import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import Nsound as ns



def main():

    matplotlib.rc('font', size = 24)
    matplotlib.rc('figure', figsize = [16, 6])
    matplotlib.rcParams.update({'figure.subplot.left'  : 0.09 })
    matplotlib.rcParams.update({'figure.subplot.bottom': 0.15 })
    matplotlib.rcParams.update({'figure.subplot.right' : 0.97 })
    matplotlib.rcParams.update({'figure.subplot.top'   : 0.88 })

    sr = 1000

    #--------------------------------------------------------------------------
    # figure 1

    gen = ns.Sine(sr)

    signal = ns.AudioStream(sr, 1)

    signal << gen.generate(1.0, 3)

    signal.plot('3 Hz Signal')

    fig = plt.gcf()
    ax = plt.gca()

    blue_line = ax.lines[0]

    plt.xlabel('Time')
    plt.ylabel('Amplitude')

    plt.xlim([-0.05, 1.05])
    plt.ylim([-1.05, 1.05])

    plt.savefig('figure_1-0.svg')

    # plot sub-sampled signal in time

    buf = signal[0]

    step = len(signal) // 32

    y = buf[0:-1:step]

    t = np.linspace(0, 1.0, len(signal))[0:-1:step]

    red_lines = []

    for tt, yy in zip(t, y):
        l = plt.axvline(x = tt, color = 'red')
        red_lines.append(l)

    plt.savefig('figure_1-2.svg')

    plt.plot(t, y, 'ro')

    plt.savefig('figure_1-3.svg')

    # remove blue line & red lines

    blue_line.remove()
    for l in red_lines:
        l.remove()

    # draw lolli pop

    for tt, yy in zip(t, y):
        plt.plot([tt, tt], [0, yy], 'b-', zorder = -1)

    fig.canvas.draw()

    plt.savefig('figure_1-4.svg')

    #--------------------------------------------------------------------------
    # figure 2

    signal.plot('3 Hz Signal')

    plt.xlabel('Time')
    plt.ylabel('Amplitude')

    plt.xlim([-0.05, 1.05])
    plt.ylim([-1.05, 1.05])

    plt.savefig('figure_2-0.svg')

    # multiply the signal by a gaussian

    s1 = signal * gen.drawGaussian(1.0, 0.33, 0.15)

    s1.plot('3 Hz Signal * env')

    plt.xlabel('Time')
    plt.ylabel('Amplitude')

    plt.xlim([-0.05, 1.05])
    plt.ylim([-1.05, 1.05])

    plt.savefig('figure_2-1.svg')

    # multiply the signal by a gaussian

    s2 = signal * gen.drawGaussian(1.0, 0.5, 0.15)

    s2.plot('3 Hz Signal * env')

    plt.xlabel('Time')
    plt.ylabel('Amplitude')

    plt.xlim([-0.05, 1.05])
    plt.ylim([-1.05, 1.05])

    plt.savefig('figure_2-2.svg')

    # multiply the signal by a gaussian

    s3 = signal * gen.drawGaussian(1.0, 0.66, 0.15)

    s3.plot('3 Hz Signal * env')

    plt.xlabel('Time')
    plt.ylabel('Amplitude')

    plt.xlim([-0.05, 1.05])
    plt.ylim([-1.05, 1.05])

    plt.savefig('figure_2-3.svg')


    # multiply the signal by a gaussian

    s4 = signal * (0.05 + gen.drawGaussian(1.0, 0.66, 0.15))
    s4.normalize();

    s4.plot('3 Hz Signal & ???')

    plt.xlabel('Time')
    plt.ylabel('Amplitude')

    plt.xlim([-0.05, 1.05])
    plt.ylim([-1.05, 1.05])

    plt.savefig('figure_2-4.svg')


    plt.show()




if __name__ == "__main__":
    main()