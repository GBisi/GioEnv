import time
import threading
from mysocket import MySocket
import sys
from statistics import *
class Sender:

    def __init__(self, port, mblen=1, mbnum=1, debug = False, ip="127.0.0.1"):
        print("--- SENDER ONLINE ---")
        self.socket = MySocket(port,mblen,mbnum,ip=ip)
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
".format(self.socket.get_mb_len(),self.socket.get_mb_num(),server_spec["len"],server_spec["num"],time.time()*1000.0,len(times),sum(times),min(times),mean(times),max(times),median(times),pvariance(times),pstdev(times))
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
            msg = self.socket.send(0,dest)
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


if __name__ == "__main__":
    
    if len(sys.argv) != 8 and len(sys.argv) != 9:
        print("sender [my_ip] [my_port] [server_ip] [server_port] [iteration] [mblen] [mbnum] [[debug]]")
    elif len(sys.argv) == 8:
        Sender(int(sys.argv[2]),int(sys.argv[6]),int(sys.argv[7]),False,str(sys.argv[1])).start((str(sys.argv[3]),int(sys.argv[4])),int(sys.argv[5]))
    else:
        Sender(int(sys.argv[2]),int(sys.argv[6]),int(sys.argv[7]),True,str(sys.argv[1])).start((str(sys.argv[3]),int(sys.argv[4])),int(sys.argv[5]))
