"""
Wavefile IO

Reads and writes RIFF WAVE files and headers.

RIFF WAVE file format:

          --------------------------------------------------------------------
byte 0:3  |      'R'       |       'I'       |       'F'     |     'F'       |
          --------------------------------------------------------------------
byte 4:7  |                          uint32 RIFF chunk size                  |
          --------------------------------------------------------------------
byte 8:10 |      'W'       |       'A'       |       'V'     |     'E'       |
          --------------------------------------------------------------------

Where "RIFF chunk size" is the total size of the file in bytes, excluding the
'RIFF' bytes.

After the RIFF WAVE header, any number of chunks can follow, each chunk has the
following format:

    chunk : [ 4 byte chunk id], [uint32 chunk size], [raw data]


The required format chunk:

           --------------------------------------------------------------------
byte  0:3  |      'f'       |       'm'       |       't'     |     ' '       |
           --------------------------------------------------------------------
byte  4:7  |                FORMAT Chunk Length (16, 18, 30, 40)              |
           --------------------------------------------------------------------
byte  8:11 | Format Tag: 1=PCM, 3=IEEE_FLOAT  |  n_channels 1, 2, ...         |
           --------------------------------------------------------------------
byte 12:15 |                             Sample Rate                          |
           --------------------------------------------------------------------
byte 16:19 |    Average # of Bytes P/Second (Sample rate*Channels*(Bits/8)    |
           --------------------------------------------------------------------
byte 20:23 | Block Align ((Bits/8)*Channels)  |   Bits per Sample (8 ... 64)  |
           --------------------------------------------------------------------
byte 24:29 | optional data if FORMAT Chunk Length is 18 or 40                 |
           --------------------------------------------------------------------


"""

