from threading import Event, Thread

class Timer(Thread):
    def __init__(self, function, time = 1000):
        Thread.__init__(self)
        self.stopped = Event()
        self.function = function
        self.time = time

    def get_flag(self):
        return self.stopped

    def run(self):
        while not self.stopped.wait(self.time/1000):
            self.function()