from random import randrange
import threading
from header import header

class Channel:

    _max_len = 1024

    def __init__(self, _max_size=_max_len):
        self._max_size = min(_max_size, Channel._max_len)
        self._queue = []
        self._lock = threading.RLock()


    @staticmethod
    def max_len():

        return Channel._max_len

    def max_size(self):

        return self._max_size

    def size(self):
        self._lock.acquire()
        data = len(self._queue)
        self._lock.release()
        return data
        
    def is_full(self):
        
        return (self.size() >= self._max_size)

    def is_empty(self):

        return (self.size() == 0)

    def next(self):
        self._lock.acquire()
        if self.is_empty():
            self._lock.release()
            return None
        data = self._queue[0]
        self._lock.release()
        return data

    def last(self):
        self._lock.acquire()
        if self.is_empty():
            self._lock.release()
            return None
        data = self._queue[-1]
        self._lock.release()
        return data

    def get(self):
        self._lock.acquire()
        if self.is_empty():
            self._lock.release()
            return None
        data = self._queue.pop(0)
        self._lock.release()
        return data

    def put(self, elem):
        
        self._lock.acquire()
        if elem is None:
            self._lock.release()
            return False

        if(self.is_full()):
            self.get()

        self._queue.append(elem)
        self._lock.release()
        return True

    def __repr__(self):
        
        return str(self._queue)