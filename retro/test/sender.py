import sys
sys.path.insert(0, "../")

import time
import threading
from mysocket import MySocket
from statistics import *
import subprocess 
import json
class Sender:

    def __init__(self, port, mblen=1, mbnum=1, debug = False, ip="127.0.0.1"):
        print("--- SENDER ONLINE ---")
        print(ip,port)
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
            self.socket.send(b'\x01',dest,mailbox=-1)
            timer = time.time()
            while time.time() - timer < 5 and res is None:
                res = self.socket.get_cmd()

        server_spec = json.loads(res.get_data().decode("utf-8"))

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
{}\n\
".format(self.socket.get_mb_len(),self.socket.get_mb_num(),server_spec["len"],server_spec["num"],time.time()*1000.0,len(times),sum(times),min(times),mean(times),max(times),median(times),pvariance(times),pstdev(times),subprocess.check_output(["ping",dest[0]]).decode("utf-8"))
        print("-------------------------------")
        print(stat)

        f = open("stats.txt", "a")
        f.write("-----------------------------\n")
        f.write(stat)
        f.close

        f = open("stats-data.txt", "a")
        f.write("-----------------------------\n")
        f.write(stat)
        f.write(str(times)+"\n")
        f.close

        return end-start

    def send(self, i,dest):
        start = time.time()
        msg = None
        while msg is None:
            msg = self.socket.send(i.to_bytes(sys.getsizeof(i),"big"),dest)
        if self.debug:
            print("send:",msg)
        msg = None
        while msg is None:
            msg = self.socket.receive()
            if msg is not None:
                if int.from_bytes(msg.get_data(),"big") != i:
                    msg = None
        end = time.time()
        if self.debug:
            print("recived:",msg)
        t = (end-start)*1000.0
         #print(i,"-","time:",t,"ms")
        return t


if __name__ == "__main__":
    
    if len(sys.argv) != 8 and len(sys.argv) != 9:
        print("sender [my_ip] [my_port] [server_ip] [server_port] [iteration] [mblen] [mbnum] [[debug]]")
    elif len(sys.argv) == 8:
        Sender(int(sys.argv[2]),int(sys.argv[6]),int(sys.argv[7]),False,str(sys.argv[1])).start((str(sys.argv[3]),int(sys.argv[4])),int(sys.argv[5]))
    else:
        Sender(int(sys.argv[2]),int(sys.argv[6]),int(sys.argv[7]),True,str(sys.argv[1])).start((str(sys.argv[3]),int(sys.argv[4])),int(sys.argv[5]))
