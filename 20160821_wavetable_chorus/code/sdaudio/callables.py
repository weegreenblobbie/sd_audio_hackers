"""
Little functor objects
"""

from sdaudio import assert_py3


class Constant(object):


    def __init__(self, value):
        self._value = value


    def __call__(self):
        return self._value


class Circular(object):


    def __init__(self, list_):
        assert len(list_) > 0, "list is empty"
        self._list = list_
        self._idx = 0


    def __call__(self):
        if self._idx >= len(self._list):
            self._idx = 0

        val = self._list[self._idx]

        self._idx += 1

        return val