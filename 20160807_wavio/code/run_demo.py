import json

import numpy as np
import matplotlib.pyplot as plt

import wavio


def main():

    files = [
        # "/home/nhilton/development/nsound/src/examples/california.wav",
        # "/home/nhilton/development/nsound/src/examples/mynameis.wav",
        # "/home/nhilton/development/nsound/src/examples/Temperature_in.wav",
        # "/home/nhilton/development/nsound/src/examples/walle.wav",
        # "/home/nhilton/development/nsound/src/examples/example1",
        # "empty.bin",
        "chirp1.wav",
    ]

    for i, f in enumerate(files):

        print('-------------------------------------------------------')
        print('Reading file')
        print('    in: %s'  % f)

        try:
            chunks = wavio.read_chunks(f)
        except wavio.InvalidRiffWave:
            print("    Not a RIFF WAVE!")
            continue

        s = json.dumps(chunks, indent = 4, separators = (', ', ' : '), sort_keys = True)

        for line in s.split('\n'):
            print('    %s' % line)

        x, sr = wavio.read(f)

        if x.ndim > 1:
            x = x[:,0]

        plt.figure()
        plt.plot(x, 'b-')
        plt.grid(True)
        plt.xlabel('sample bin')
        plt.ylabel('amplitude')
        plt.title('wav = %s' % f)

        # write out forward & reverse

        fout = 'fwd-%02d.wav' % i

        wavio.write(fout, x, sr, dtype = np.float32)

        print('Wrote %s' % fout)

        f = fout

        chunks = wavio.read_chunks(f)

        s = json.dumps(chunks, indent = 4, separators = (', ', ' : '), sort_keys = True)

        for line in s.split('\n'):
            print('    %s' % line)

        x, sr = wavio.read(f)

        if x.ndim > 1:
            x = x[:,0]

        plt.figure()
        plt.plot(x, 'b-')
        plt.grid(True)
        plt.xlabel('sample bin')
        plt.ylabel('amplitude')
        plt.title('wav = %s' % f)


    plt.show()


if __name__ == "__main__":
    main()