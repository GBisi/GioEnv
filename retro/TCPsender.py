import time
import threading
from mysocket import MySocket
import sys
from statistics import *
import subprocess 
import socket

class Sender:

    def __init__(self, port, debug = False, ip="127.0.0.1"):
        print("--- SENDER ONLINE ---")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.debug = debug


    def start(self, dest, num):
        times = []
        start = time.time()
        for i in range(num):
            times.append(self.send(i,dest))
            self.socket.close()
        end = time.time()
        print(times)
        times = list(filter(lambda a: a != -1, times))
        stat = "Timestamp: {}\n\
Packets Sended: {}\n\
Packets Received: {}\n\
Total Time: {:0.2f}\n\
min: {:0.2f}\n\
avg: {:0.2f}\n\
max: {:0.2f}\n\
median: {:0.2f}\n\
variance: {:0.2f}\n\
stdev: {:0.2f}\n\
{}\n\
".format(time.time()*1000.0,num,len(times),sum(times),min(times),mean(times),max(times),median(times),pvariance(times),pstdev(times),subprocess.check_output(["ping",dest[0]]).decode("utf-8"))
        print("-------------------------------")
        print(stat)

        f = open("statsUDP.txt", "a")
        f.write("-----------------------------\n")
        f.write(stat)
        f.close

        f = open("statsUDP-data.txt", "a")
        f.write("-----------------------------\n")
        f.write(stat)
        f.write(str(times)+"\n")
        f.close

        return end-start

    def send(self, i,dest):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(dest)
        start = time.time()
        self.socket.sendall(str(i).encode("utf-8"))
        if self.debug:
            print("send:",i)
        data = None
        # Look for the response
        amount_received = 0
        amount_expected = len(str(i).encode("utf-8"))
        while amount_received < amount_expected:
            data = self.socket.recv(16)
            amount_received += len(data)
        if data is not None and int(data.decode()) != i:
            return -1
        if data is None:
            return -1
        end = time.time()
        if self.debug:
            print("recived:",data)
        t = (end-start)*1000.0
        print(i,"-","time:",t,"ms")
        return t


if __name__ == "__main__":
    
    if len(sys.argv) != 6 and len(sys.argv) != 7:
        print("sender [my_ip] [my_port] [server_ip] [server_port] [iteration] [[debug]]")
    elif len(sys.argv) == 6:
        Sender(int(sys.argv[2]),ip=str(sys.argv[1]),debug=False).start((str(sys.argv[3]),int(sys.argv[4])),int(sys.argv[5]))
    else:
        Sender(int(sys.argv[2]),ip=str(sys.argv[1]),debug=True).start((str(sys.argv[3]),int(sys.argv[4])),int(sys.argv[5]))
