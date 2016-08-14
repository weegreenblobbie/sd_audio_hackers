"""
Assert python 3 is being used
"""

import sys

if sys.version_info[0] != 3:
    raise RuntimeError("Sorry, requires Python 3.x")