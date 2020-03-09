from channel import Channel
from message import Message
from random import randrange
import time 
import json
from math import log

class Mailbox:

    _max_seq = 1024
    _delta = 5000

    _k = log(_max_seq,2)
    _threshold = pow(2,_k-1)

    def __init__(self, size, delta=_delta):

        self._input = Channel(size)
        self._output = Channel(size)

        self._max_size = self._input.max_size()

        self._last_in = None
        self._next_out = randrange(self._max_seq)

        self._delta = delta
        self._timer = None

    #RFC1982 3.2 https://tools.ietf.org/html/rfc1982
    def _check(self, message):

        if self._last_in is None:
            return True

        i1 = message.get_sequence()
        i2 = self._last_in

        if (i1 < i2 and i2 - i1 > Mailbox._threshold) or (i1 > i2 and i1 - i2 < Mailbox._threshold):
            return True

        return False

    def max_size(self):

        return self._max_size
    
    def get_input(self):

        return self._input

    def get_output(self):
    
        return self._output

    def get_last_in(self):

        return self._last_in

    def get_next_out(self):
    
        return self._next_out

    def send(self, message):

        message.set_sequence(self._next_out)

        self._next_out = (self._next_out+1) % self._max_seq

        return self._output.put(message)

    def receive(self):

        message = self._input.get()
        if message is None:
            return None

        return message

    def post(self, message):

        if self._check(message):

            self._input.put(message)
            self._last_in = message.get_sequence()
            return True

        return False

    def start_timer(self):

        self._timer = time.time()*1000.0

    def stop_timer(self):
    
        self._timer = None
        
    def timeout(self):

        if self._timer == None: 
            return True

        now = time.time()*1000.0

        if now - self._timer > self._delta:
            self._timer = None
            return True

        return False


    def __repr__(self):

        return str({"out":self._output, "in":self._input})

