"""
Wavefile IO

Reads and writes RIFF WAVE files and headers.

"""

"""
-------------------------------------------------------------------------------
RIFF WAVE file format
-------------------------------------------------------------------------------

RIFF WAVE header:

          --------------------------------------------------------------------
byte 0:3  |      'R'       |       'I'       |       'F'     |     'F'       |
          --------------------------------------------------------------------
byte 4:7  |                          uint32 RIFF chunk size                  |
          --------------------------------------------------------------------
byte 8:10 |      'W'       |       'A'       |       'V'     |     'E'       |
          --------------------------------------------------------------------

Where "RIFF chunk size" is the total size of the file in bytes, excluding the
'RIFF' & chunk size bytes.

After the RIFF WAVE header, any number of chunks can follow, each chunk has the
following format:

    chunk : ( 4 byte chunk id), (uint32 chunk size), (raw bytes[chunk_size])

The format chunk:

           --------------------------------------------------------------------
byte  0:3  |      'f'       |       'm'       |       't'     |     ' '       |
           --------------------------------------------------------------------
byte  4:7  |                      uint32 sub-chunk size                       |
           --------------------------------------------------------------------
byte  8:11 | Format Tag: 1=PCM, 3=IEEE_FLOAT  |  n_channels 1, 2, ...         |
           --------------------------------------------------------------------
byte 12:15 |                      uint32 sample rate                          |
           --------------------------------------------------------------------
byte 16:19 |    Average # of Bytes P/Second (Sample rate*Channels*(Bits/8)    |
           --------------------------------------------------------------------
byte 20:23 | Block Align ((Bits/8)*Channels)  |   Bits per Sample (8 ... 64)  |
           --------------------------------------------------------------------
byte 24:29 | optional data if FORMAT Chunk Length is 18 or 40                 |
           --------------------------------------------------------------------

The data chunk, contians the raw audio data:

           --------------------------------------------------------------------
byte  0:3  |      'd'       |       'a'       |       't'     |     'a'       |
           --------------------------------------------------------------------
byte  4:7  |                       uint32 sub-chunk size                      |
           --------------------------------------------------------------------
byte  8    |                              raw data                            |
           --------------------------------------------------------------------


Optional 'TAG' chunk (aka ID3v1), all fields are plain ASCII except for the
genre byte.  Total size is 128 bytes and since the 'tag' is not 4 bytes long and
follwed by a chunk size, it does not conform to RIFF WAVE format, so it must
be placed at the end of the file.

           ----------------------------------------------------
byte  0:2  |      't'       |       'a'       |       'g'     |
           --------------------------------------------------------------------
byte  3:32 |                          Title - 30 bytes                        |
           --------------------------------------------------------------------
byte 33:62 |                         Artist - 30 bytes                        |
           --------------------------------------------------------------------
byte 63:92 |                          Album - 30 bytes                        |
           --------------------------------------------------------------------
byte 93:96 |                           Year -  4 bytes                        |
           --------------------------------------------------------------------
byte 97:126|                        Comment - 30 bytes                        |
           --------------------------------------------------------------------
byte 127   | Genre - 1 byte |
           ------------------

This class ignore all other tags.
"""

import os.path
import sys
import struct


# Assert python 3 is being used

if sys.version_info[0] != 3:
    sys.stdout.write("Sorry, requires Python 3.x\n")
    sys.exit(1)


class InvalidRiffWave(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class WavIOError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def read_chunks(filename):

    chunks = dict()

    if not os.path.isfile(filename):
        raise IOError('File not found: %s' % filename)

    with open(filename, 'rb') as fd:

        chunks['RIFF'] = _read_riff(fd, filename)

        tag = 'xx'

        while tag != '':

            tag = bytes.decode(fd.read(4), 'UTF-8')

            if tag == 'fmt ':
                ck = _read_fmt(fd, tag)
                chunks[tag] = ck

            elif tag == 'data':
                ck = _read_data_size(fd, tag)
                chunks[tag] = ck

            elif tag[0:2] == 'tag':
                ck = _read_tag(fd, tag)
                chunks[tag] = ck

            elif tag == '':
                pass

            else:
                raise WavIOError('unhandled tag "%s"' % tag)

    return chunks


def _read_riff(fd, filename):

    # read the RIFF header

    riff = fd.read(4)
    size = fd.read(4)
    wave = fd.read(4)

    if riff != b"RIFF" or wave != b"WAVE":
        raise InvalidRiffWave('Could not detect a RIFF WAVE header: %s' % filename)

    # convert the raw bytes into an unsigned int

    size = struct.unpack('<I', size)[0]

    return dict(
        tag = bytes.decode(riff, 'UTF-8'),
        size = size
    )


def _read_fmt(fd, tag):

    size = fd.read(4)

    pos = fd.tell()

    fmt_type      = fd.read(2)
    channels      = fd.read(2)
    sample_rate   = fd.read(4)
    bytes_per_sec = fd.read(4)
    align         = fd.read(2)
    bits_per_sam  = fd.read(2)

    size          = struct.unpack('<I', size)[0]
    fmt_type      = struct.unpack('<H', fmt_type)[0]
    channels      = struct.unpack('<H', channels)[0]
    sample_rate   = struct.unpack('<I', sample_rate)[0]
    bytes_per_sec = struct.unpack('<I', bytes_per_sec)[0]
    align         = struct.unpack('<H', align)[0]
    bits_per_sam  = struct.unpack('<H', bits_per_sam)[0]

    fd.seek(pos + size)

    return dict(
        tag = tag,
        size = size,
        format = fmt_type,
        channels = channels,
        sample_rate = sample_rate,
        bytes_per_sec = bytes_per_sec,
        align = align,
        bits_per_sam = bits_per_sam,
    )


def _read_data_size(fd, tag):

    size = fd.read(4)

    pos = fd.tell()

    size = struct.unpack('<I', size)[0]

    fd.seek(pos + size)

    return dict(
        tag = tag,
        size = size,
    )


def _read_tag(fd, tag):
    return dict(tag = tag)
