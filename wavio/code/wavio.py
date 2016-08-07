"""
Wavefile IO

Reads and writes RIFF WAVE files and headers.


Reference: http://soundfile.sapp.org/doc/WaveFormat/

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


import numpy as np


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
                ck = _read_unhandled_tag(fd, tag)

                if 'unhandled' not in chunks:
                    chunks['unhandled'] = []

                chunks['unhandled'].append(ck)

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

    # map bits_per_sample and format_type to a numpy dtype

    format = _fmt_type_to_str(fmt_type)

    dtype = 'unknown'

    if format == "Microsoft PCM":

        if bits_per_sam == 8:
            dtype = 'uint8'

        elif bits_per_sam == 16:
            dtype = 'int16'

        elif bits_per_sam in [24, 32]:
            dtype = 'int32'

        elif bits_per_sam == 64:
            dtype = 'int64'

    elif format == "IEEE Float":

        if bits_per_sam == 32:
            dtype = 'float32'

        elif bits_per_sam == 64:
            dtype = 'float64'

    return dict(
        tag = tag,
        size = size,
        format = format,
        channels = channels,
        sample_rate = sample_rate,
        bytes_per_second = bytes_per_sec,
        align = align,
        bits_per_sample = bits_per_sam,
        dtype = dtype,
    )


def _read_unhandled_tag(fd, tag):

    size = fd.read(4)

    pos = fd.tell()

    size = struct.unpack('<I', size)[0]

    fd.seek(pos + size)

    return dict(
        tag = tag,
        size = size,
    )


def _read_data_size(fd, tag):

    size = fd.read(4)

    pos = fd.tell()

    size = struct.unpack('<I', size)[0]

    fd.seek(pos + size)

    return dict(
        tag = tag,
        size = size,
        pos = pos,
    )


def _read_tag(fd, tag):
    return dict(tag = tag)


def _fmt_type_to_str(typ):

    if   typ == 0x0000: return "Unknown"
    elif typ == 0x0001: return "Microsoft PCM"
    elif typ == 0x0002: return "Microsoft ADPCM"
    elif typ == 0x0003: return "IEEE Float"
    elif typ == 0x0004: return "Compaq VSELP"
    elif typ == 0x0005: return "IBM CVSD"
    elif typ == 0x0006: return "Microsoft ALAW"
    elif typ == 0x0007: return "Microsoft MULAW"
    elif typ == 0x000A: return "Microsoft Windows Media Audio Speech"
    elif typ == 0x0010: return "OKI ADPCM"
    elif typ == 0x0011: return "Intel DVI ADPCM"
    elif typ == 0x0012: return "Videologic MediaSpace ADPCM"
    elif typ == 0x0013: return "Sierra ADPCM"
    elif typ == 0x0014: return "Antex Electronics G.723 ADPCM"
    elif typ == 0x0015: return "DSP Solution DIGISTD"
    elif typ == 0x0016: return "DSP Solution DIGIFIX"
    elif typ == 0x0017: return "Dialogic OKI ADPCM"
    elif typ == 0x0018: return "MediaVision ADPCM"
    elif typ == 0x0019: return "HP CU"
    elif typ == 0x0020: return "Yamaha ADPCM"
    elif typ == 0x0021: return "Speech Compression Sonarc"
    elif typ == 0x0022: return "DSP Group True Speech"
    elif typ == 0x0023: return "Echo Speech EchoSC1"
    elif typ == 0x0024: return "Audiofile AF36"
    elif typ == 0x0025: return "APTX"
    elif typ == 0x0026: return "AudioFile AF10"
    elif typ == 0x0027: return "Prosody 1612"
    elif typ == 0x0028: return "LRC"
    elif typ == 0x0030: return "Dolby AC2"
    elif typ == 0x0031: return "Microsoft GSM610"
    elif typ == 0x0032: return "Microsoft MSNAudio"
    elif typ == 0x0033: return "Antex ADPCME"
    elif typ == 0x0034: return "Control Res VQLPC"
    elif typ == 0x0035: return "Digireal"
    elif typ == 0x0036: return "DigiADPCM AC2"
    elif typ == 0x0037: return "Control Res CR10"
    elif typ == 0x0038: return "NMS VBXADPCM AC2"
    elif typ == 0x0039: return "Roland RDAC"
    elif typ == 0x003A: return "EchoSC3"
    elif typ == 0x003B: return "Rockwell ADPCM"
    elif typ == 0x003C: return "Rockwell Digit LK"
    elif typ == 0x003D: return "Xebec"
    elif typ == 0x0040: return "Antex Electronics G.721"
    elif typ == 0x0041: return "Antex Electronics G.728 CELP"
    elif typ == 0x0042: return "Microsoft MSG723"
    elif typ == 0x0050: return "MPEG"
    elif typ == 0x0052: return "Voxware RT24"
    elif typ == 0x0053: return "InSoft PAC"
    elif typ == 0x0055: return "MPEG Layer 3"
    elif typ == 0x0057: return "AMR NB"
    elif typ == 0x0058: return "AMR WB"
    elif typ == 0x0059: return "Lucent G.723"
    elif typ == 0x0060: return "Cirrus"
    elif typ == 0x0061: return "ESPCM"
    elif typ == 0x0062: return "Voxware"
    elif typ == 0x0063: return "Canopus Atrac"
    elif typ == 0x0064: return "APICOM G.726 ADPCM"
    elif typ == 0x0065: return "APICOM G.722 ADPCM"
    elif typ == 0x0066: return "Microsoft DSAT"
    elif typ == 0x0067: return "Microsoft DSAT Display"
    elif typ == 0x0069: return "Voxware Byte Aligned"
    elif typ == 0x0070: return "Voxware AC8"
    elif typ == 0x0071: return "Voxware AC10"
    elif typ == 0x0072: return "Voxware AC16"
    elif typ == 0x0073: return "Voxware AC20"
    elif typ == 0x0074: return "Voxware Metavoice"
    elif typ == 0x0075: return "Voxware Metasound"
    elif typ == 0x0076: return "Voxware RT29HW"
    elif typ == 0x0077: return "Voxware VR12"
    elif typ == 0x0078: return "Voxware VR18"
    elif typ == 0x0079: return "Voxware TQ40"
    elif typ == 0x0080: return "Softsound"
    elif typ == 0x0081: return "Voxware TQ60"
    elif typ == 0x0082: return "MSRT24"
    elif typ == 0x0083: return "AT&T G.729A"
    elif typ == 0x0084: return "Motion Pixels MVI MV12"
    elif typ == 0x0085: return "DF G.726"
    elif typ == 0x0086: return "DF GSM610"
    elif typ == 0x0088: return "ISIAudio"
    elif typ == 0x0089: return "Onlive"
    elif typ == 0x0091: return "Siemens SBC24"
    elif typ == 0x0092: return "Dolby AC3 SPDIF"
    elif typ == 0x0093: return "Mediasonic G723"
    elif typ == 0x0094: return "Prosody 8KBPS"
    elif typ == 0x0097: return "ZyXEL ADPCM"
    elif typ == 0x0098: return "Philips LPCBB"
    elif typ == 0x0099: return "Packed"
    elif typ == 0x00A0: return "Malden PhonyTalk"
    elif typ == 0x00FF: return "AAC"
    elif typ == 0x0100: return "Rhetorex ADPCM"
    elif typ == 0x0101: return "IBM MULAW"
    elif typ == 0x0102: return "IBM ALAW"
    elif typ == 0x0103: return "IBM ADPCM"
    elif typ == 0x0111: return "Vivo G.723"
    elif typ == 0x0112: return "Vivo Siren"
    elif typ == 0x0123: return "DEC G.723"
    elif typ == 0x0125: return "Sanyo LD ADPCM"
    elif typ == 0x0130: return "Siprolab ACEPLNET"
    elif typ == 0x0131: return "Siprolab ACELP4800"
    elif typ == 0x0132: return "Siprolab ACELP8V3"
    elif typ == 0x0133: return "Siprolab G729"
    elif typ == 0x0134: return "Siprolab G729A"
    elif typ == 0x0135: return "Siprolab Kelvin"
    elif typ == 0x0140: return "G726 ADPCM"
    elif typ == 0x0150: return "Qualcomm Purevoice"
    elif typ == 0x0151: return "Qualcomm Halfrate"
    elif typ == 0x0155: return "Tub GSM"
    elif typ == 0x0160: return "WMAV1"
    elif typ == 0x0161: return "WMAV2"
    elif typ == 0x0162: return "WMAV3"
    elif typ == 0x0163: return "WMAV3 L"
    elif typ == 0x0200: return "Creative ADPCM"
    elif typ == 0x0202: return "Creative FastSpeech8"
    elif typ == 0x0203: return "Creative FastSpeech10"
    elif typ == 0x0210: return "UHER ADPCM"
    elif typ == 0x0220: return "Quarterdeck"
    elif typ == 0x0230: return "iLink VC"
    elif typ == 0x0240: return "Raw Sport"
    elif typ == 0x0250: return "IPI HSX"
    elif typ == 0x0251: return "IPI RPELP"
    elif typ == 0x0260: return "CS2"
    elif typ == 0x0270: return "Sony ATRAC3"
    elif typ == 0x028E: return "Siren"
    elif typ == 0x0300: return "Fujitsu FM Towns Snd"
    elif typ == 0x0400: return "BTV Digital"
    elif typ == 0x0401: return "IMC"
    elif typ == 0x0450: return "QDesign Music"
    elif typ == 0x0680: return "AT&T VME VMPCM"
    elif typ == 0x0681: return "TCP"
    elif typ == 0x1000: return "Olivetti OLIGSM"
    elif typ == 0x1001: return "Olivetti OLIADPCM"
    elif typ == 0x1002: return "Olivetti OLICELP"
    elif typ == 0x1003: return "Olivetti OLISBC"
    elif typ == 0x1004: return "Olivetti OLIOPR"
    elif typ == 0x1100: return "LH Codec"
    elif typ == 0x1400: return "Norris"
    elif typ == 0x1401: return "AT&T ISIAudio"
    elif typ == 0x1500: return "AT&T Soundspace Music Compression"
    elif typ == 0x2000: return "DVM"
    elif typ == 0x2001: return "DTS"
    elif typ == 0x2048: return "Sonic"
    elif typ == 0x4143: return "AAC AC"
    elif typ == 0x674f: return "Vorbis 1"
    elif typ == 0x6750: return "Vorbis 2"
    elif typ == 0x6751: return "Vorbis 3"
    elif typ == 0x676f: return "Vorbis 1+"
    elif typ == 0x6770: return "Vorbis 2+"
    elif typ == 0x6771: return "Vorbis 3+"
    elif typ == 0x706d: return "AAC PM"
    elif typ == 0x7A21: return "GSM AMR CBR"
    elif typ == 0x7A22: return "GSM AMR VBR"
    elif typ == 0xF1AC: return "FLAC"
    elif typ == 0xFFFE: return "WAVE_FORMAT_EXTENSIBLE"
    elif typ == 0xFFFF: return "Experimental"

    return "UNKOWN"


def read(filename, dtype = np.float32):
    """
    reads RIFF WAVE files and returns numpy array.

    defaults to returing an array of type np.float32, setting dtype = None will
    return the raw type.
    """

    chunks = read_chunks(filename)

    pos = chunks['data']['pos']
    size = chunks['data']['size']

    with open(filename, 'rb') as fd:
        fd.seek(data_pos)
        raw = fd.read(size)







