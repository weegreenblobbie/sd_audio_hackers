import json

import matplotlib.pyplot as plt

import wavio


def main():

    files = [
        "/home/nhilton/development/nsound/src/examples/california.wav",
        "/home/nhilton/development/nsound/src/examples/mynameis.wav",
        "/home/nhilton/development/nsound/src/examples/Temperature_in.wav",
        "/home/nhilton/development/nsound/src/examples/walle.wav",
        "/home/nhilton/development/nsound/src/examples/example1",
        "empty.bin",
        "chirp1.wav",
    ]

    for f in files:

        print('-------------------------------------------------------')
        print('Reading file')
        print('    in: %s'  % f)

        try:
            chunks = wavio.read_chunks(f)

            s = json.dumps(chunks, indent = 4, separators = (', ', ' : '))

            for line in s.split('\n'):
                print('    %s' % line)

            data = wavio.read(f)

            if data.ndim > 1:
                data = data[:,0]

            plt.figure()
            plt.plot(data, 'b-')
            plt.grid(True)
            plt.xlabel('sample bin')
            plt.ylabel('amplitude')
            plt.title('wav = %s' % f)

        except wavio.InvalidRiffWave:
            print("    Not a RIFF WAVE!")

    plt.show()


if __name__ == "__main__":
    main()