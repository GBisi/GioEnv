import requests
import threading
import time

class Observer:

    def __init__(self, url):
        self.url = url
        self.run = True

    def _run(self, callback, timeout=None):
        while self.run:
            try:
                callback(requests.get(self.url, timeout=None).json())
            except:
                pass

    def start(self, callback, detached = False, timeout=None):

        if detached:
            threading.Thread(target=self._run, args=(callback,timeout,)).start()
        else:
            self._run(callback)

    def stop(self):
        self.run = False

if __name__ == "__main__":
    o = Observer("http://131.114.73.148:2000/tuvov/events/setup")
    o.start(lambda x: print(x),True)
    time.sleep(10)
    o.stop()
