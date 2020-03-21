import time
import threading
from mysocket import MySocket
import sys
from statistics import *
class Sender:

    def __init__(self, port, n=1, m=1, debug = False, ip="127.0.0.1"):
        print("--- SENDER ONLINE ---")
        self.socket = MySocket(port,n,m,ip=ip)
        self.debug = debug


    def start(self, dest, num):

        self.socket.start()
        times = []
        start = time.time()
        for i in range(num):
            times.append(self.send(i,dest))
        end = time.time()
        print("-------------------------------")
        print("Total Packets:",len(times))
        print("Total Time:",sum(times))
        print("min:",min(times))
        print("avg:",mean(times))
        print("max:",max(times))
        print("median:",median(times))
        print("variance:",pvariance(times))
        print("dev:",pstdev(times))
        return end-start

    def send(self, i,dest):
        start = time.time()
        msg = None
        while msg is None:
            msg = self.socket.send(i,dest)
        if self.debug:
            print("send:",msg)
        msg = None
        while msg is None:
            msg = self.socket.receive()
        if self.debug:
            print("recived:",msg)
        end = time.time()
        t = (end-start)*1000.0
        print(i,"-","time:",t,"ms")
        return t


def start_sender(ip, port, dest, num, debug = False):
    threading.Thread(target=Sender(port,ip=ip, debug=debug).start,args=(dest,num,)).start()

def sender_factory(ip, port, dest, n, it, debug = False):
    for i in range(n):
        start_sender(ip, port,dest,it, debug = debug)
        port = port+1


if __name__ == "__main__":
    
    if len(sys.argv) != 6 and len(sys.argv) != 7:
        print("sender [my_ip] [my_port] [server_ip] [server_port] [iteration] [[debug]]")
    elif len(sys.argv) == 6:
        sender_factory(str(sys.argv[1]),int(sys.argv[2]),(str(sys.argv[3]),int(sys.argv[4])),1,int(sys.argv[5]),debug=False)
    else:
        sender_factory(str(sys.argv[1]),int(sys.argv[2]),(str(sys.argv[3]),int(sys.argv[4])),1,int(sys.argv[5]),debug=True)
