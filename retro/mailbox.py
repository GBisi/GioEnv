from random import randrange
import time 
import json
from math import log
import threading
from channel import Channel

class Mailbox:

    _max_seq = 65536 #16 bit
    _delta = 5000

    _k = log(_max_seq,2)
    _threshold = pow(2,_k-1)

    def __init__(self, size, standby_time, delta=_delta):

        self._input = Channel(size)
        self._output = Channel(size)

        self._max_size = self._input.max_size()

        self._last_in = None
        self._next_out = randrange(self._max_seq)

        self._delta = delta
        self._timer = None

        self._timer_lock = threading.RLock()

        self._first = True
        self._standby_time = standby_time
        self._last_send = time.time()

    #RFC1982 3.2 https://tools.ietf.org/html/rfc1982
    def _check(self, message):

        if self._last_in is None:
            return True

        if message.is_syn():
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

        now = time.time()

        if now-self._last_send > self._standby_time/2:

            self.reset()

        self._last_send = now 

        if(self._first):

            message.set_syn()

        message.set_sequence(self._next_out)

        self._next_out = (self._next_out+1) % self._max_seq

        if self._output.put(message):
            return message
        
        return None

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

        self._timer_lock.acquire()

        self._timer = time.time()*1000.0

        self._timer_lock.release()

    def stop_timer(self):

        self._timer_lock.acquire()

        delta = -1

        if self._timer is not None:

            now = time.time()*1000.0
            delta =  now - self._timer

        self._timer = None

        self._timer_lock.release()

        return delta

        

    def set_timeout(self, delta):

        self._timer_lock.acquire()

        self._delta = delta

        self._timer_lock.release()
        
    def timeout(self):

        self._timer_lock.acquire()

        if self._timer is None: 
            self._timer_lock.release()
            return True

        now = time.time()*1000.0

        delta = now - self._timer

        if delta > self._delta:
            self.stop_timer()
            self._timer_lock.release()
            return True

        self._timer_lock.release()

        return False

    def ack(self, n):

        self._first = False


    def reset(self):

        self._first = True

    def set_standby_time(self, time):

        self._standby_time = time


    def __repr__(self):

        return str({"out":self._output, "in":self._input})

