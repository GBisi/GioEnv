from random import randrange

class Channel:

    _max_len = 1024

    def __init__(self, _max_size=_max_len):
        self._max_size = min(_max_size, Channel._max_len)
        self._queue = []

    @staticmethod
    def max_len():

        return Channel._max_len

    def max_size(self):

        return self._max_size

    def size(self):

        return len(self._queue)
        
    def is_full(self):
        
        return (self.size() >= self._max_size)

    def is_empty(self):

        return (self.size() == 0)

    def next(self):

        if self.is_empty():
            return None
        return self._queue[0]

    def last(self):

        if self.is_empty():
            return None
        return self._queue[-1]

    def get(self):

        if self.is_empty():
            return None
        return self._queue.pop(0)

    def put(self, elem):

        if elem is None:
            return False

        if(self.is_full()):
            self.get()

        self._queue.append(elem)

        return True

    def __repr__(self):
        
        return str(self._queue)