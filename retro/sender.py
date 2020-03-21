import time
import threading
from mysocket import MySocket
import sys
from statistics import *
class Sender:

    def __init__(self, port, n=1, m=1, debug = False, ip="127.0.0.1"):
        print("--- SENDER ONLINE ---")
        self.socket = MySocket(port,n,m,ip=ip)
        self.n = n
        self.m = m
        self.debug = debug


    def start(self, dest, num):

        self.socket.start()
        times = []
        start = time.time()
        for i in range(num):
            times.append(self.send(i,dest))
        end = time.time()

        res = None
        while res is None:
            self.socket.send(1,dest,mailbox=-1)
            timer = time.time()
            while time.time() - timer < 5 and res is None:
                res = self.socket.get_cmd()

        server_spec = res.get_data()

        stat = "Client Spec: {} {}\n\
Server Spec: {} {}\n\
Timestamp: {}\n\
Total Packets: {}\n\
Total Time: {:0.2f}\n\
min: {:0.2f}\n\
avg: {:0.2f}\n\
max: {:0.2f}\n\
median: {:0.2f}\n\
variance: {:0.2f}\n\
stdev: {:0.2f}\n\
".format(self.n,self.m,server_spec["len"],server_spec["num"],time.time()*1000.0,len(times),sum(times),min(times),mean(times),max(times),median(times),pvariance(times),pstdev(times))
        print("-------------------------------")
        print(stat)

        f = open("stats.txt", "a")
        f.write("-----------------------------\n")
        f.write(stat)
        f.write(str(times)+"\n")
        f.close

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
