from mysocket import MySocket
import time
import threading

class Sender:

    def __init__(self, port, n=1, m=1):

        self.socket = MySocket(port,n,m)


    def start(self, dest, num):

        self.socket.start()

        start = time.time()
        for i in range(num):
            self.socket.send(i,dest)

            msg = None

            while msg is None:
                msg = self.socket.receive()
                
        end = time.time()
        print(end-start)
        return end-start


def start_sender(port, dest, num):
    threading.Thread(target=Sender(port).start,args=(dest,num,)).start()

def sender_factory(port, dest, n, it):
    for i in range(n):
        start_sender(port,dest,it)
        port = port+1


#sender_factory(4201,("127.0.0.1",4200),1,1)
port = 4201
dest = ("127.0.0.1",4200)
n = 1
it = 100
sender_factory(port,dest,n,it)