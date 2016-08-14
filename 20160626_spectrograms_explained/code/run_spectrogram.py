"""
San Diego Audio Hackers

https://github.com/weegreenblobbie/sd_audio_hackers

2016 Nick Hilton

"""

# python
import argparse
import os.path
import sys

assert sys.version_info.major == 2, "python 2 only!"


# third party

import matplotlib.pyplot as plt
import numpy as np
#~from scipy.io.wavfile import read as _wavread  # broken!

# Using Nsound to read wavefile since scipy 0.13.3 is broken for stereo, int32 files

import Nsound as ns


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c',
        '--channel',
        type = int,
        default = None,
        help = 'Selectes one channel if the input wave contains multiple channels',
    )

    parser.add_argument(
        'input_wav',
        help = 'The input wavfile to process',
    )

    args = parser.parse_args()

    if not os.path.isfile(args.input_wav):
        raise RuntimeError("Could not find file: %s" % args.input_wav)

    #-------------------------------------------------------------------------
    # read wavfile in

    sr, x = wavread(args.input_wav)

    if x.ndim > 1:

        if args.channel is not None:
            x = x[:, args.channel]

        else:
            raise RuntimeError(
                'Input wav has %d channles, use --channels to select one' % x.ndim
            )

    #-----------------------------------------------------------------------------
    # compute spectrogram

    cfg = Stft.get_defaults()

    cfg['sample_rate'] = sr

    stft_op = Stft(**cfg)

    data = stft_op(sample_rate = sr, signal = x)

    #-------------------------------------------------------------------------
    # plot data

    time_axis = data['stft_time_axis']
    freq_axis = data['stft_freq_axis']

    amp = np.abs(data['stft_spec']) ** 0.33

    plt.figure()
    imagesc(time_axis, freq_axis, amp.T, cmap = 'bone')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.title('Spectrogram: %s' % os.path.basename(args.input_wav))

    plt.ylim([freq_axis[0], 5000])

    plt.show()



"""
Short time Fourier transform
"""

class Stft:

    @staticmethod
    def get_defaults():

        return dict(
            sample_rate = 8000.0,
            t_sigma = 0.01,
            t_step = 0.01,
            f_step = 16.666,
            window = 'gaussian',
        )


    def __init__(self, **kwargs):
        """
        Computes the short time fourier transform on input signal.

        keyword arguments:

            sample_rate : float
                The sample rate of the input signal.

            t_sigma : float
                The standard deviation of the gaussian time-envelope used for
                the window.

            t_step : float
                The time step in seconds between fft samples

            f_step : float
                The frequency axis step size (nfft & frame_size are derived from this)

            window : str
                The name of the window to apply to the frame, one of: [
                    'gaussian', 'rectangular']
        """

        sr = kwargs['sample_rate']
        t_sigma = kwargs['t_sigma']
        t_step  = kwargs['t_step']
        f_step  = kwargs['f_step']
        window  = kwargs['window']

        assert sr > 0, "sample_rate <= 0"
        assert t_sigma > 0, "t_sigma <= 0"
        assert t_step > 0, "t_step <= 0"
        assert f_step > 0, "f_step <= 0"

        step = int(np.round(sr * t_step))

        #---------------------------------------------------------------------
        # compute frame size, nearest power of 2

        size_f_step = int(sr / f_step)
        size_t_sigma = int(np.round(sr * 6.0 * t_sigma))

        frame_size = round_up2(min(size_f_step, size_t_sigma))
        nfft = frame_size

        #---------------------------------------------------------------------
        # setup freq axis

        nyquist = sr / 2.0

        freq_axis = np.linspace(0, nyquist, nfft / 2 + 1).astype(np.float32)

        #---------------------------------------------------------------------
        # window

        if window == 'gaussian':

            t = np.arange(nfft) / float(sr)
            mu = np.mean(t)

            w = np.exp(-0.5 * ((t - mu) / t_sigma) ** 2.0)

        elif window == 'rectangular':
            w = np.ones(nfft)

        else:
            raise ValueError('unknown window type "%s"' % window)

        w = w.astype(np.float32)
        w /= np.sum(w)

        #---------------------------------------------------------------------
        # save values into object

        self._freq_axis = freq_axis
        self._nfft = nfft
        self._sample_rate = sr
        self._step = step
        self._window = w


    def __call__(self, **kwargs):
        """
        inputs: signal, sample_rate
        outputs: stft_spec, stft_freq_axis, stft_time_axis
        """

        signal = kwargs['signal']
        sample_rate = kwargs['sample_rate']

        assert int(self._sample_rate) == int(sample_rate), "sample_rate != %d" % self._sample_rate
        assert signal.ndim == 1, "signal must be 1D"

        # compute slices of the input signal

        sample_slices = compute_sample_slices(
            len(signal),
            self._nfft,
            self._step
        )

        #---------------------------------------------------------------------
        # forward stft

        n_time = len(sample_slices)

        time_axis = np.zeros(n_time)

        spec = np.zeros((n_time, len(self._freq_axis)), np.complex64)

        for i in xrange(n_time):

            center, s0, s1, pad_l, pad_r = sample_slices[i]

            time_axis[i] = center

            s = np.array(signal[s0 : s1])

            if pad_l > 0:
                s = np.hstack([np.zeros((pad_l), np.float32), s])

            if pad_r > 0:
                s = np.hstack([s, np.zeros((pad_r), np.float32)])

            s = s * self._window

            spec[i,:] = np.fft.rfft(s)

        #---------------------------------------------------------------------
        # conver time axis into seconds

        time_axis = time_axis.astype(np.float32) / self._sample_rate

        out = dict(
            stft_spec = spec,
            stft_freq_axis = np.array(self._freq_axis),
            stft_time_axis = time_axis,
        )

        kwargs.update(out)

        return kwargs


def round_up2(n):
    """
    Rounds up to next power of 2.  Returns n if n is already a power of 2.
    """

    assert n > 0, "n <= 0"

    return int(2 ** np.ceil(np.log(n) / np.log(2)))


def compute_sample_slices(N, frame_size, step):
    """
    Computes tart and stop indices and padding.

    Returns a list of tuples:

        (center_idx, begin_idx, end_idx, pad_left, pad_right),

    """

    assert N > 0, 'N <= 0'
    assert frame_size > 0, 'frame_size <= 0'
    assert step > 0, 'step <= 0'

    #-------------------------------------------------------------------------
    # compute center indicies for each frame

    h_frame = frame_size // 2

    centers = []

    c_idx = 0

    while c_idx < N + h_frame:
        centers.append(c_idx)
        c_idx += step

    #-------------------------------------------------------------------------
    # sampl

    sample_slices = []

    for c_idx in centers:

        i0 = c_idx - h_frame
        i1 = c_idx + h_frame

        pad_l = 0
        pad_r = 0

        if i0 < 0:
            pad_l = abs(i0)
            i0 = 0

        if i1 >= N:
            pad_r = i1 - N + 1
            i1 = N - 1

        sample_slices.append( (c_idx, i0, i1, pad_l, pad_r) )

    return sample_slices


def imagesc(x_axis, y_axis, Z, axes = None, **kwargs):
    """
    Plots the 2D matriz Z using the provided x & y axis for data labels.
    Additional keyword argumnts will be passed on to the Matplotlib imshow()
    method.

    Parameters:
        *x_axis*
            The data labels to use for the x axis, must be linear (shape N)

        *y_axis*
            The data labels to use for the y axis, must be linear (shape M)

        *Z*
            The data matrix to plot (shape M,N)

        *axes*
            The matplotlib.axes.Axes to draw on

        `**kwargs`
            Keyword arguments passed to matplotlib.axes.Axes.imshow()

    Returns:

        *h*
            The graphical handle

    Examples:

        By default, the origin is in the lower left corner:

        .. plot::
            :include-source:

            import numpy as np
            import matplotlib.pyplot as plt

            from prospero.plot.imagesc import imagesc

            # Create a data matrix, the Idenity with some zeros concatenated
            data = np.eye(5)
            data = np.hstack( (data, np.zeros((5,1))) )

            x_axis = range(6)
            y_axis = range(5)

            plt.figure()
            imagesc(x_axis, y_axis, data)
            plt.xlabel("X axis")
            plt.ylabel("Y axis")

        To change it, pass the matplotlib.axes.Axes.imshow() keyword argument
        `origin="upper"`:

        .. plot::
            :include-source:

            import numpy as np
            import matplotlib.pyplot as plt

            from prospero.plot.imagesc import imagesc

            # Create a data matrix, the Idenity with some zeros concatenated
            data = np.eye(5)
            data = np.hstack( (data, np.zeros((5,1))) )

            x_axis = range(6)
            y_axis = range(5)

            plt.figure()
            imagesc(x_axis, y_axis, data, origin = "upper")
            plt.xlabel("X axis")
            plt.ylabel("Y axis")

    """

    # always make a copy so that caller doesn't get a linked colormap by
    # accident!

    Z = np.array(Z)

    if Z.ndim != 2:
        raise ValueError("Z should be 2D, not %dD" % Z.ndim)

    M, N = Z.shape

    if x_axis is None:
        x_axis = np.arange(N).astype(np.int32)

    if y_axis is None:
        y_axis = np.arange(M).astype(np.int32)

    # Convert to arrays if lists.
    x_axis = np.array(x_axis)
    y_axis = np.array(y_axis)

    if M != y_axis.size:
        raise ValueError("y_axis.size != Z rows (%d != %d)" %(y_axis.size, M))

    if N != x_axis.size:
        raise ValueError("x_axis.size != Z cols (%d != %d)" %(x_axis.size, N))

    # Override these if not set.

    kwargs.setdefault('origin', 'lower')
    kwargs.setdefault('interpolation', 'nearest')

    y_axis = y_axis[::-1]

    if kwargs['origin'] == 'lower':
        y_axis = y_axis[::-1]

    dx = x_axis[1] - x_axis[0]
    dy = y_axis[1] - y_axis[0]

    extent = \
    [
        x_axis[0]  - 0.5 * dx,
        x_axis[-1] + 0.5 * dx,
        y_axis[0]  - 0.5 * dy,
        y_axis[-1] + 0.5 * dy
    ]

    # Always override these keyword.
    kwargs["extent"] = extent

    ax = axes

    if ax is None:
        h = plt.imshow(Z, **kwargs)
        ax = plt.gca()

    else:
        h = ax.imshow(Z, **kwargs)

    ax.axis("tight")

    return h


def wavread(filename):

    import Nsound as ns

    a = ns.AudioStream(filename)

    sr = a.getSampleRate()

    n_channels = a.getNChannels()
    n_samples = a.getLength()

    x = np.zeros((n_samples, n_channels), np.float32)

    for c in range(n_channels):
        x[:,c] = a[c].toList()

    x = np.squeeze(x) # remove singular dimensions if present

    return sr, x



if __name__ == "__main__":
    main()
